"""Extract beat frames and stream/decode evidence for a completed film render."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]


def check_video_timeline(frames, time_base, fps, duration):
    """Require each decoded presentation timestamp to occupy its CFR slot."""
    expected = Fraction(str(duration)) * fps
    if expected.denominator != 1 or expected <= 0 or len(frames) != expected.numerator:
        raise ValueError(f'Video frame count does not cover the requested timeline: {len(frames)} versus {expected}')
    tick = Fraction(time_base)
    timestamps = [int(frame['best_effort_timestamp']) for frame in frames]
    if tick <= 0 or any(abs(t * tick - Fraction(i, fps)) > tick
                        for i, t in enumerate(timestamps)):
        raise ValueError('Video frame timestamps do not match the required timeline')
    return {'status': 'passed', 'frame_count': len(frames),
            'first_pts': timestamps[0], 'last_pts': timestamps[-1],
            'time_base': time_base, 'expected_duration': duration}


def verify_export(movie, receipt, *, width, height, fps, duration, audio_expected=False):
    """Invalidate stale evidence before checking every expected stream and decoding it."""
    movie, receipt = Path(movie), Path(receipt)
    record = {'verification_version': 3, 'video': str(movie), 'full_decode': 'pending'}

    def save():
        temp = receipt.with_suffix(receipt.suffix + '.tmp')
        temp.write_text(json.dumps(record, indent=2) + '\n')
        temp.replace(receipt)

    save()
    try:
        record['sha256'] = hashlib.sha256(movie.read_bytes()).hexdigest()
        probe = ['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(movie)]
        data = json.loads(subprocess.check_output(probe, text=True, stderr=subprocess.PIPE))
        videos = [s for s in data['streams'] if s['codec_type'] == 'video']
        audios = [s for s in data['streams'] if s['codec_type'] == 'audio']
        if (len(videos) != 1 or len(audios) != int(audio_expected)
                or len(data['streams']) != 1 + int(audio_expected)):
            raise ValueError('Unexpected stream count or missing required audio stream')
        stream = videos[0]
        if (stream['codec_name'] != 'h264' or (stream['width'], stream['height']) != (width, height)
                or stream['r_frame_rate'] != f'{fps}/1'
                or abs(float(data['format']['duration']) - duration) > 1/fps):
            raise ValueError('Export does not match duration or video requirements')
        if audio_expected and (audios[0]['codec_name'] != 'aac' or audios[0]['channels'] != 1
                               or audios[0]['sample_rate'] != '48000'):
            raise ValueError('Audio stream must be mono AAC at 48000 Hz')
        if audio_expected and (abs(float(audios[0].get('duration', 0)) - duration) > .1
                               or abs(float(audios[0].get('start_time', 0))) > .1):
            raise ValueError('Audio stream duration or start does not match the video')
        command = ['ffmpeg', '-v', 'error', '-xerror', '-i', str(movie), '-map', '0:v:0']
        if audio_expected:
            command += ['-map', '0:a:0']
        command += ['-f', 'null', '-']
        record['decode_command'] = command
        result = subprocess.run(command, capture_output=True, text=True)
        record['decode_returncode'] = result.returncode
        record['diagnostics'] = result.stderr
        if result.returncode or result.stderr.strip():
            raise ValueError('Full-file decoding failed: ' + result.stderr.strip())
        frame_command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                         '-show_frames', '-show_entries', 'frame=best_effort_timestamp',
                         '-of', 'json', str(movie)]
        record['frame_probe_command'] = frame_command
        frames = json.loads(subprocess.check_output(frame_command, text=True,
                                                    stderr=subprocess.PIPE))['frames']
        record['video_timeline'] = check_video_timeline(frames, stream['time_base'], fps, duration)
        record.update({'full_decode': 'passed', 'codec': stream['codec_name'],
                       'width': width, 'height': height, 'fps': fps,
                       'duration': float(data['format']['duration']),
                       'audio_expected': audio_expected})
        save()
        return record
    except Exception as exc:
        record['full_decode'] = 'failed'
        record['diagnostics'] = record.get('diagnostics') or str(exc)
        save()
        raise


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--slug',required=True)
    parser.add_argument('--quality',choices=['preview','final'],required=True)
    parser.add_argument('--decode-only',action='store_true',help='Write a strict decode receipt without changing visual review evidence')
    args=parser.parse_args()
    root=ROOT/'output'/args.slug
    tag='preview' if args.quality=='preview' else '1080p30'
    movie=root/f'{args.slug}_{tag}.mp4'
    timing=json.loads((root/f'{args.slug}_timing.json').read_text())
    width,height,fps=(854,480,15) if args.quality=='preview' else (1920,1080,30)
    strict=verify_export(movie, root/f'{args.slug}_{args.quality}_strict_decode_v3.json',
                         width=width,height=height,fps=fps,duration=timing['duration_seconds'],
                         audio_expected=timing.get('audio_expected', False))
    if args.decode_only:
        print(json.dumps(strict,indent=2))
        return
    frames=root/f'{args.slug}_{args.quality}_keyframes';frames.mkdir(exist_ok=True)
    images=[]
    for cue in timing['cues']:
        sample=cue.get('review_time',(cue['start']+cue['end'])/2)
        for kind,seconds in [('state',sample),('transition',cue['start']+.5)]:
            path=frames/f"{cue['beat_id']}_{kind}.png"
            subprocess.run(['ffmpeg','-v','error','-y','-ss',str(seconds),'-i',str(movie),'-frames:v','1',str(path)],check=True)
        img=Image.open(frames/f"{cue['beat_id']}_state.png").convert('RGB')
        img.thumbnail((426,240))
        images.append((cue['beat_id'],sample,img.copy()))
    for event in timing.get('events', []):
        if event.get('settled', event['start']) > event['start']:
            for phase, seconds in [('before', max(0,event['start']-1/fps)),
                                   ('during', (event['start']+event['settled'])/2),
                                   ('after', min(timing['duration_seconds']-1/fps,event['settled']+1/fps))]:
                subprocess.run(['ffmpeg','-v','error','-y','-ss',str(seconds),'-i',str(movie),'-frames:v','1',str(frames/f"event_{event['id']}_{phase}.png")],check=True)
    for item in timing.get('extra_keyframes', []):
        subprocess.run(['ffmpeg','-v','error','-y','-ss',str(item['time']),'-i',str(movie),'-frames:v','1',str(frames/f"extra_{item['id']}.png")],check=True)
    final=frames/'final_hold.png'
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(timing['duration_seconds']-1),'-i',str(movie),'-frames:v','1',str(final)],check=True)
    timeline = strict['video_timeline']
    last_time = float(timeline['last_pts'] * Fraction(timeline['time_base']))
    # Select the actual decoded final frame by index, avoiding approximate seeks.
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(movie),'-vf',
                    f"select=eq(n\\,{timeline['frame_count']-1})",'-frames:v','1',
                    str(frames/'last_decoded_frame.png')],check=True)
    sheet=Image.new('RGB',(426*3,270*((len(images)+2)//3)),'#111827')
    draw=ImageDraw.Draw(sheet)
    try: font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',19)
    except OSError: font=ImageFont.load_default()
    for i,(name,sec,img) in enumerate(images):
        x,y=(i%3)*426,(i//3)*270
        sheet.paste(img,(x,y+24));draw.text((x+8,y+2),f'{name} — {sec:.1f} s',font=font,fill='white')
    sheet.save(root/f'{args.slug}_{args.quality}_contact_sheet.png')
    report={'video':str(movie),'sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),
            'bytes':movie.stat().st_size,'codec':strict['codec'],'width':width,'height':height,
            'fps':fps,'duration':strict['duration'],'full_decode':'passed',
            'keyframes':str(frames),'last_decoded_frame_time':last_time,
            'visual_review':'pending','frame_review':'pending',
            'playback_review':'pending',
            'audio_review':'pending' if timing.get('audio_expected') else 'not_applicable'}
    (root/f'{args.slug}_{args.quality}_probe.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__': main()
