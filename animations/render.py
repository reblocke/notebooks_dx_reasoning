"""Render one production scene with a measured free-space guard."""
import argparse
import importlib
import json
import os
import signal
from pathlib import Path
import shutil
import subprocess
import sys
import time
from core.provenance import capture_render_sources, digest
from core.films import resolve_film

ROOT = Path(__file__).resolve().parent
RESERVE = 5 * 2**30
CLINICAL_HEADROOM = 256 * 2**20


def clinical_timing(goal):
    if goal in ('05', '06'):
        data = importlib.import_module(f'core.story{goal}_clinical').story()
        return data['final_hold_seconds'], data['events']
    if goal == '01':
        return 7, [
            {'id': 'observe_exudative', 'start': 26, 'settled': 26.8},
            {'id': 'normalize', 'start': 28.8, 'settled': 29.8},
            {'id': 'final_hold', 'start': 46.6, 'settled': 47},
        ]
    if goal == '02':
        return 5, [
            {'id': 'probability_update', 'start': 16.4, 'settled': 17.9},
            {'id': 'odds_coordinates', 'start': 23, 'settled': 23.4},
            {'id': 'log_odds_coordinates', 'start': 30, 'settled': 30.4},
            {'id': 'inverse_update', 'start': 38.4, 'settled': 39.9},
            {'id': 'final_hold', 'start': 42.6, 'settled': 43},
        ]
    if goal == '03':
        return 6, [
            {'id': 'area_A', 'start': 6, 'settled': 6.4},
            {'id': 'all_areas', 'start': 14, 'settled': 14.4},
            {'id': 'rare_sweep', 'start': 23.4, 'settled': 26},
            {'id': 'observed_update', 'start': 39.4, 'settled': 42},
            {'id': 'final_hold', 'start': 47.6, 'settled': 48},
        ]
    if goal == '04':
        events = []
        for name, start in [('convergence', 16), ('reopening', 24),
                            ('substitution', 32), ('persistent_ambiguity', 40)]:
            for i in range(4):
                t = start + 1 + 19*i/15
                events.append({'id': f'{name}_E{i+1}', 'start': t, 'settled': t+.4})
        events.append({'id': 'final_hold', 'start': 65, 'settled': 65})
        return 7, events
    raise ValueError('Unsupported clinical goal')


def apply_clinical_timing(timing, cues, narration, goal):
    """Bind each cut's review timing and actual speech intervals to its own cues."""
    timing['audio_expected'] = True
    timing['final_hold_seconds'], timing['events'] = clinical_timing(goal)
    timing['extra_keyframes'] = []
    if goal == '03':
        timing['extra_keyframes'] = [
            {'id': name, 'time': t} for name, t in
            [('area_A', 10), ('all_areas', 18), ('sweep_start', 23),
             ('sweep_mid', 24.7), ('sweep_end', 28), ('uniform', 34),
             ('concentrated', 37), ('finding_endpoint', 44)]]
    elif goal == '04':
        timing['extra_keyframes'] = [
            {'id': f'{name}_state_{i}', 'time': start+.5 if i == 0 else start+1+19*(i-1)/15+.6}
            for name, start in [('convergence',16), ('reopening',24),
                                ('substitution',32), ('persistent_ambiguity',40)]
            for i in range(5)]
        timing['extra_keyframes'] += [{'id': name, 'time': t} for name, t in
                                      [('centroid',8), ('concentrated_A',10.5), ('concentrated_B',14),
                                       ('substitution_equal_entropy',39), ('comparison',50),
                                       ('window_02',55), ('window_24',59), ('window_04',63)]]
    if goal in ('05', '06'):
        data = importlib.import_module(f'core.story{goal}_clinical').story()
        timing['extra_keyframes'] = data['extra_keyframes']
        timing['subtitle_intervals'] = narration['subtitle_intervals']
    intervals = narration['speech_intervals']
    if len(cues) != len(intervals) or len(cues) != len(timing['cues']):
        raise ValueError('Clinical timing and narration cue counts disagree')
    hold_start = cues[-1].start
    for cue, interval in zip(timing['cues'], intervals):
        if cue['beat_id'] != interval['beat_id']:
            raise ValueError('Clinical timing and narration cue IDs disagree')
        cue['narration_start'] = interval['start']
        cue['narration_end'] = interval['end']
        cue['caption_fade_in_start'] = 0 if cue['start'] == 0 else cue['start']
        cue['caption_fully_visible_at'] = min(cue['start'] + .4, hold_start)
        cue['caption_fade_out_start'] = cue['end'] if cue['end'] < cues[-1].end else None
        cue['caption_visible_end'] = cue['end']
    timing['cues'][-1]['caption_fade_in_start'] = hold_start - .4
    timing['cues'][-1]['caption_fully_visible_at'] = hold_start
    if goal == '06':
        timing['cues'][-1]['caption_fade_in_start'] = cues[-2].start
        timing['cues'][-1]['caption_fully_visible_at'] = cues[-2].start + .4
    if goal == '01':
        timing['cues'][3]['caption_fully_visible_at'] = cues[3].start + .8
    if goal == '04':
        timing['cues'][-1]['caption_fade_in_start'] = hold_start


def stop_render(process):
    """Stop only the renderer and encoders launched in its own process group."""
    if process.poll() is None:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--goal", choices=["preflight", "01", "02", "03", "04", "05", "06"], required=True)
    parser.add_argument("--quality", choices=["preview", "final"], default="preview")
    parser.add_argument("--cut", choices=["original", "clinical"], default=None)
    args = parser.parse_args()
    try:
        film = resolve_film(args.goal, args.cut)
    except ValueError as exc:
        parser.error(str(exc))
    clinical = film.narrated
    if digest(ROOT/film.fixture_path) != film.fixture_hash:
        raise ValueError('Scientific fixture differs from the registered approved identity')
    free = shutil.disk_usage(ROOT).free
    if free < RESERVE:
        raise SystemExit("Render blocked: at least 5 GiB free is required.")
    if clinical and free < RESERVE + CLINICAL_HEADROOM:
        raise SystemExit('Clinical render blocked: the 5 GiB reserve plus 256 MiB working space is required.')
    slug, source, scene = film.slug, film.scene, film.scene_class
    if args.goal != 'preflight':
        from core.cues import write_sidecars
        data = importlib.import_module(film.story_module).story()
        cues = data['cues']
        output = ROOT / "output" / slug
        if clinical:
            output.mkdir(parents=True, exist_ok=True)
        else:
            write_sidecars(cues, output, slug)
        timing = {
            "duration_seconds": cues[-1].end,
            "final_hold_seconds": cues[-1].end-cues[-1].start-1,
            "cues": [{**vars(cue), **({'review_time': 169} if args.goal == '03' and cue.beat_id == 'E08' else {}), "caption_fade_in_start": cue.start + .4,
                      "caption_fully_visible_at": cue.start + 1,
                      "caption_fade_out_start": cue.end if i < len(cues)-1 else None,
                      "caption_visible_end": cue.end + .4 if i < len(cues)-1 else cue.end}
                     for i, cue in enumerate(cues)],
            "events": ([
                {"id": "observe_E", "start": 30, "settled": 31},
                {"id": "select_joint_masses", "start": 49, "settled": 51.4},
                {"id": "normalize", "start": 69, "settled": 71.4},
                {"id": "rewind_perspective", "start": 122, "settled": 123},
                {"id": "branch_comparison", "start": 134, "settled": 135},
                {"id": "return_to_observed_E", "start": 180, "settled": 181},
            ] if args.goal == "01" else ([
                {"id": "probability_update", "start": 32, "settled": 37.4},
                {"id": "odds_replay", "start": 74, "settled": 79.4},
                {"id": "log_odds_replay", "start": 120, "settled": 125.4},
                {"id": "inverse_update", "start": 151, "settled": 156.4},
            ] if args.goal == "02" else ([
                {"id": "A_rectangle_reveal", "start": 16, "settled": 18},
                {"id": "three_area_highlights", "start": 66, "settled": 68.4},
                {"id": "hypothetical_sweep", "start": 120, "settled": 130},
                {"id": "observed_finding_update", "start": 183, "settled": 191},
            ] if args.goal == "03" else [ {"id":f"{name}_E{i+1}", "start":start+1+i*4.6+.6, "settled":start+1+i*4.6+3.6} for name,start in [("convergence",65),("reopening",100),("substitution",135),("ambiguity",170)] for i in range(4)]))),
            "extra_keyframes": ([{"id":"uniform", "time":169},
                                  {"id":"concentrated", "time":176},
                                  {"id":"area_A", "time":66.4},
                                  {"id":"area_B", "time":67.2},
                                  {"id":"area_C", "time":68.0},
                                  {"id":"sweep_start", "time":118},
                                  {"id":"sweep_end", "time":135},
                                  {"id":"finding_endpoint", "time":195}]
                                 if args.goal == "03" else ([{"id":f"{name}_state_{i}","time":start+1 if i==0 else start+1+(i-1)*4.6+3.8} for name,start in [("convergence",65),("reopening",100),("substitution",135),("ambiguity",170)] for i in range(5)] + [{"id":"centroid","time":19},{"id":"concentrated_A","time":25},{"id":"concentrated_B","time":37},{"id":"window_02","time":240},{"id":"window_24","time":252},{"id":"window_04","time":265}] if args.goal == "04" else [])),
        }
        if clinical:
            from core.narration import make_narration, write_narrated_sidecars
            narration = make_narration(cues, output, slug, segments=data.get('speech_segments'))
            write_narrated_sidecars(cues, narration, output, slug)
            apply_clinical_timing(timing, cues, narration, args.goal)
        (output / f"{slug}_timing.json").write_text(json.dumps(timing, indent=2) + "\n")
    output = ROOT / "output" / slug
    output.mkdir(parents=True, exist_ok=True)
    resolution, fps = ((854, 480), 15) if args.quality == "preview" else ((1920, 1080), 30)
    name = f"{slug}_{'1080p30' if args.quality == 'final' and args.goal != 'preflight' else args.quality}"
    command = [sys.executable, "-B", "-m", "manim", "--renderer", "cairo", "--disable_caching",
               "--config_file", str(ROOT / "manim.cfg"), "--media_dir", str(output / "media"),
               "--resolution", ",".join(map(str, resolution)), "--fps", str(fps),
               "--output_file", name, str(ROOT / "scenes" / source), scene]
    free_before_launch = shutil.disk_usage(ROOT).free
    required_before_launch = RESERVE + (CLINICAL_HEADROOM if clinical else 0)
    if free_before_launch < required_before_launch:
        raise SystemExit("Render blocked: preparation fell below the required starting space.")
    samples = [free, free_before_launch]
    status = "failed"
    mux_command = None
    render_sources = capture_render_sources(ROOT, output, slug, source, clinical, args.quality)
    snapshot = Path(render_sources['snapshot'])
    samples.append(shutil.disk_usage(ROOT).free)
    if samples[-1] < required_before_launch:
        raise SystemExit('Render blocked: input snapshot fell below the required starting space.')
    command[command.index('--config_file') + 1] = str(snapshot / 'manim.cfg')
    command[-2] = str(snapshot / 'scenes' / source)
    process = subprocess.Popen(command, cwd=snapshot, start_new_session=True)
    try:
        while process.poll() is None:
            samples.append(shutil.disk_usage(ROOT).free)
            if samples[-1] < RESERVE:
                stop_render(process)
                raise RuntimeError("Render stopped: free space fell below 5 GiB.")
            time.sleep(.5)
        if process.returncode:
            raise RuntimeError(f"Manim exited with status {process.returncode}.")
        samples.append(shutil.disk_usage(ROOT).free)
        if samples[-1] < RESERVE:
            raise RuntimeError("Render completed below the required 5 GiB reserve.")
        rendered = list((output / "media/videos").glob(f"**/{name}.mp4"))
        if len(rendered) != 1:
            raise RuntimeError("Expected exactly one complete preflight export.")
        if clinical:
            mux_command = ['ffmpeg', '-v', 'error', '-xerror', '-i', str(rendered[0]),
                           '-i', str(snapshot / f'{slug}_narration.wav'), '-map', '0:v:0',
                           '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac', '-ar', '48000',
                           '-ac', '1', '-b:a', '128k', '-t', str(cues[-1].end), '-movflags', '+faststart',
                           '-y', str(output / f'{name}.mp4')]
            mux = subprocess.Popen(mux_command, cwd=ROOT, start_new_session=True)
            try:
                while mux.poll() is None:
                    samples.append(shutil.disk_usage(ROOT).free)
                    if samples[-1] < RESERVE:
                        stop_render(mux)
                        raise RuntimeError('Audio mux stopped: free space fell below 5 GiB.')
                    time.sleep(.5)
                if mux.returncode:
                    raise RuntimeError(f'Audio mux exited with status {mux.returncode}.')
            finally:
                if mux.poll() is None:
                    stop_render(mux)
        else:
            shutil.copy2(rendered[0], output / f"{name}.mp4")
        samples.append(shutil.disk_usage(ROOT).free)
        if samples[-1] < RESERVE:
            raise RuntimeError("Export completed below the required 5 GiB reserve.")
        status = "complete"
    finally:
        if process.poll() is None:
            stop_render(process)
        (output / f"{name}_storage.json").write_text(json.dumps({
            "render_sources": render_sources,
            "video_sha256": digest(output / f'{name}.mp4') if status == 'complete' else None,
            "command": command, "mux_command": mux_command, "free_bytes_before": free,
            "minimum_sampled_free_bytes": min(samples),
            "free_bytes_after": shutil.disk_usage(ROOT).free,
            "reserve_bytes": RESERVE, "sampling_seconds": .5,
            "returncode": process.returncode, "status": status,
        }, indent=2) + "\n")


if __name__ == "__main__":
    main()
