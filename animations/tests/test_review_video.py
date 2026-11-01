import json
import hashlib
import subprocess
import sys

import pytest

from scripts.review_video import verify_export, check_video_timeline
from scripts import finalize_film


def make_video(path, audio=False):
    command = ['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i',
               'testsrc2=size=96x54:rate=15']
    if audio:
        command += ['-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000']
    command += ['-t', '2', '-c:v', 'libx264', '-pix_fmt', 'yuv420p']
    if audio:
        command += ['-c:a', 'aac', '-ac', '1']
    subprocess.run(command + ['-y', str(path)], check=True)


def check(path, receipt, audio=False):
    return verify_export(path, receipt, width=96, height=54, fps=15,
                         duration=2, audio_expected=audio)


@pytest.mark.parametrize('audio', [False, True])
def test_valid_streams_decode(tmp_path, audio):
    movie, receipt = tmp_path / 'valid.mp4', tmp_path / 'receipt.json'
    make_video(movie, audio)
    result = check(movie, receipt, audio)
    assert result['full_decode'] == 'passed'
    assert '-xerror' in result['decode_command']
    assert json.loads(receipt.read_text())['sha256'] == result['sha256']


def test_corrupt_video_replaces_stale_pass(tmp_path):
    movie, receipt = tmp_path / 'video.mp4', tmp_path / 'receipt.json'
    make_video(movie)
    check(movie, receipt)
    packets = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_packets',
        '-show_entries', 'packet=pos,size,flags', '-of', 'json', str(movie)
    ], text=True))['packets']
    packet = next(p for p in packets[4:] if 'K' not in p['flags'] and int(p['size']) > 100)
    content = bytearray(movie.read_bytes())
    pos = int(packet['pos'])
    content[pos:pos+4] = b'\xff\xff\xff\xff'
    movie.write_bytes(content)
    with pytest.raises(ValueError, match='decod'):
        check(movie, receipt)
    record = json.loads(receipt.read_text())
    assert record['full_decode'] == 'failed'
    assert record['diagnostics']


def test_missing_audio_replaces_stale_pass(tmp_path):
    movie, receipt = tmp_path / 'video.mp4', tmp_path / 'receipt.json'
    make_video(movie)
    check(movie, receipt)
    with pytest.raises(ValueError, match='stream'):
        check(movie, receipt, audio=True)
    assert json.loads(receipt.read_text())['full_decode'] == 'failed'


def test_long_audio_cannot_hide_short_video(tmp_path):
    movie, receipt = tmp_path / 'short-video.mp4', tmp_path / 'receipt.json'
    subprocess.run([
        'ffmpeg', '-v', 'error', '-f', 'lavfi', '-i',
        'testsrc2=size=96x54:rate=15:duration=1', '-f', 'lavfi', '-i',
        'sine=frequency=440:sample_rate=48000:duration=2', '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ac', '1', '-y', str(movie),
    ], check=True)
    with pytest.raises(ValueError, match='video|frame|timeline'):
        check(movie, receipt, audio=True)
    assert json.loads(receipt.read_text())['full_decode'] == 'failed'


def test_delayed_video_is_rejected_despite_full_audio_duration(tmp_path):
    movie, receipt = tmp_path / 'delayed.mp4', tmp_path / 'receipt.json'
    subprocess.run([
        'ffmpeg', '-v', 'error', '-itsoffset', '0.5', '-f', 'lavfi', '-i',
        'testsrc2=size=96x54:rate=15:duration=1.5', '-f', 'lavfi', '-i',
        'sine=frequency=440:sample_rate=48000:duration=2', '-fps_mode', 'passthrough',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ac', '1', '-y', str(movie),
    ], check=True)
    with pytest.raises(ValueError, match='video|frame|timeline'):
        check(movie, receipt, audio=True)
    assert json.loads(receipt.read_text())['full_decode'] == 'failed'


def test_missing_frame_in_full_length_video_is_rejected(tmp_path):
    movie, receipt = tmp_path / 'gap.mp4', tmp_path / 'receipt.json'
    subprocess.run([
        'ffmpeg', '-v', 'error', '-f', 'lavfi', '-i',
        'testsrc2=size=96x54:rate=15:duration=2', '-f', 'lavfi', '-i',
        'sine=frequency=440:sample_rate=48000:duration=2',
        '-vf', r'select=not(eq(n\,10))', '-fps_mode', 'passthrough',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ac', '1', '-y', str(movie),
    ], check=True)
    with pytest.raises(ValueError, match='video|frame|timeline'):
        check(movie, receipt, audio=True)
    assert json.loads(receipt.read_text())['full_decode'] == 'failed'


@pytest.mark.parametrize('fault', ['late_start', 'gap', 'missing'])
def test_video_timeline_rejects_discontinuous_or_incomplete_frames(fault):
    frames = [{'best_effort_timestamp': i * 1000} for i in range(30)]
    if fault == 'late_start':
        for frame in frames:
            frame['best_effort_timestamp'] += 100
    elif fault == 'gap':
        frames[15]['best_effort_timestamp'] += 100
    else:
        frames.pop(15)
    with pytest.raises(ValueError, match='Video frame'):
        check_video_timeline(frames, '1/15000', 15, 2)


@pytest.mark.parametrize('status', ['failed', 'passed'])
@pytest.mark.parametrize('pending_playback', [False, True])
def test_finalizer_rejects_a_stale_or_failed_strict_receipt(tmp_path, monkeypatch, status, pending_playback):
    root = tmp_path / 'animations'
    slug = '01_demo'
    out = root / 'output' / slug
    out.mkdir(parents=True)
    (root / 'data').mkdir()
    fixture = root / 'data' / 'manim_fixtures.json'
    fixture.write_text('{}')
    (out / f'{slug}_timing.json').write_text(json.dumps({'duration_seconds': 2}))
    movie = out / f'{slug}_preview.mp4'
    movie.write_bytes(b'video')
    video_hash = hashlib.sha256(movie.read_bytes()).hexdigest()
    probe = {'full_decode': 'passed', 'visual_review': 'passed', 'sha256': video_hash}
    for quality in ('preview', 'final'):
        (out / f'{slug}_{quality}_probe.json').write_text(json.dumps(probe))
    strict = {'verification_version': 2, 'full_decode': status, 'sha256': video_hash,
              'audio_expected': False}
    (out / f'{slug}_preview_strict_decode_v3.json').write_text(json.dumps(strict))
    monkeypatch.setattr(finalize_film, 'ROOT', root)
    monkeypatch.setattr(finalize_film, 'FIXTURE_HASH', hashlib.sha256(fixture.read_bytes()).hexdigest())
    argv = ['finalize_film.py', '--slug', slug, '--scene', 'x.py', '--review-note', 'test']
    if pending_playback:
        argv.append('--allow-pending-playback')
    monkeypatch.setattr(sys, 'argv', argv)
    with pytest.raises(ValueError, match='strict decode'):
        finalize_film.main()
    assert not (out / f'{slug}_keyframes').exists()


def test_pending_package_cannot_pass_review_without_explicit_option_and_frame_evidence():
    record = {'visual_review': 'pending', 'playback_review': 'pending'}
    with pytest.raises(ValueError, match='visual review'):
        finalize_film.require_visual_review(record, allow_pending_playback=True)
    record['frame_review'] = 'passed'
    with pytest.raises(ValueError, match='visual review'):
        finalize_film.require_visual_review(record)
    finalize_film.require_visual_review(record, allow_pending_playback=True)
    record['frame_review'] = 'failed'
    with pytest.raises(ValueError, match='visual review'):
        finalize_film.require_visual_review(record, allow_pending_playback=True)
