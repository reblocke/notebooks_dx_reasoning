"""Build and time a local narration track from the clinical cue source."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from .cues import timestamp
from .voice_config import VOICE, VOICE_RATE


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def make_narration(cues, output, slug, *, voice=VOICE, rate=VOICE_RATE):
    output = Path(output)
    audio = output / f'{slug}_narration.wav'
    receipt = output / f'{slug}_narration_audio.json'
    source = json.dumps([vars(c) for c in cues], sort_keys=True).encode()
    source_hash = hashlib.sha256(source).hexdigest()
    if audio.exists() or receipt.exists():
        if not audio.exists() or not receipt.exists():
            raise ValueError('Incomplete existing narration; inspect before replacing it')
        data = json.loads(receipt.read_text())
        if (data['cue_source_sha256'] != source_hash or data['audio_sha256'] != digest(audio)
                or data['voice'] != voice or data['rate_wpm'] != rate):
            raise ValueError('Existing narration does not match this cue source')
        return data

    intervals = []
    with tempfile.TemporaryDirectory(prefix='narration-', dir=output) as temporary:
        folder = Path(temporary)
        files = []
        for cue in cues:
            part = folder / f'{cue.beat_id}.aiff'
            subprocess.run(['/usr/bin/say', '-v', voice, '-r', str(rate),
                            '-o', str(part), cue.narration], check=True)
            duration = float(subprocess.check_output([
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', str(part)], text=True))
            start = cue.start + .1
            end = start + duration
            if end > cue.end - .1:
                raise ValueError(f'{cue.beat_id} narration exceeds its cue window')
            intervals.append({'beat_id': cue.beat_id, 'start': round(start, 3),
                              'end': round(end, 3), 'source_duration': duration})
            files.append(part)
        command = ['ffmpeg', '-v', 'error', '-xerror']
        for part in files:
            command += ['-i', str(part)]
        filters = [f'[{i}:a]aresample=48000,adelay={round(row["start"]*1000)}:all=1[a{i}]'
                   for i, row in enumerate(intervals)]
        joined = ''.join(f'[a{i}]' for i in range(len(files)))
        filters.append(f'{joined}amix=inputs={len(files)}:duration=longest:normalize=0,'
                       f'apad,atrim=duration={cues[-1].end},asetpts=PTS-STARTPTS[out]')
        command += ['-filter_complex', ';'.join(filters), '-map', '[out]', '-ar', '48000',
                    '-ac', '1', '-c:a', 'pcm_s16le', '-y', str(audio)]
        subprocess.run(command, check=True)
    data = {'voice': voice, 'rate_wpm': rate, 'sample_rate': 48000,
            'cue_source_sha256': source_hash, 'audio_sha256': digest(audio),
            'speech_intervals': intervals,
            'os_version': subprocess.check_output(['sw_vers', '-productVersion'], text=True).strip()}
    receipt.write_text(json.dumps(data, indent=2) + '\n')
    return data


def write_narrated_sidecars(cues, audio_record, output, slug):
    output = Path(output)
    intervals = audio_record['speech_intervals']
    if [c.beat_id for c in cues] != [row['beat_id'] for row in intervals]:
        raise ValueError('Narration intervals do not match cue IDs')
    srt, vtt = [], ['WEBVTT\n']
    narration = [f'# Narration: {slug}', '', 'Locally synthesized speech; captions remain readable without sound.', '']
    for i, (cue, interval) in enumerate(zip(cues, intervals), 1):
        start, end = interval['start'], interval['end']
        if not cue.start <= start < end <= cue.end:
            raise ValueError('Narration extends beyond its cue')
        srt.append(f'{i}\n{timestamp(start, ",")} --> {timestamp(end, ",")}\n{cue.narration}\n')
        vtt.append(f'{cue.beat_id}\n{timestamp(start, ".")} --> {timestamp(end, ".")}\n{cue.narration}\n')
        narration.extend([f'## {cue.beat_id} ({timestamp(start, ".")}–{timestamp(end, ".")})', '', cue.narration, ''])
    (output / f'{slug}.srt').write_text('\n'.join(srt), encoding='utf-8')
    (output / f'{slug}.vtt').write_text('\n'.join(vtt), encoding='utf-8')
    (output / f'{slug}_narration.md').write_text('\n'.join(narration), encoding='utf-8')
