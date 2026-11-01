"""One timing source for burned-in captions, narration and sidecars."""
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Cue:
    beat_id: str
    start: float
    end: float
    caption: str
    narration: str


def validate_cues(cues, duration):
    if not cues or cues[0].start != 0 or cues[-1].end != duration:
        raise ValueError('cues must cover the complete film')
    for index, cue in enumerate(cues):
        if cue.end <= cue.start or not cue.caption or not cue.narration:
            raise ValueError('each cue needs positive duration, caption and narration')
        if index and cue.start != cues[index-1].end:
            raise ValueError('cue intervals must be contiguous')
    if len({cue.beat_id for cue in cues}) != len(cues):
        raise ValueError('beat IDs must be unique')


def timestamp(seconds, separator):
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3600000)
    minutes, milliseconds = divmod(milliseconds, 60000)
    secs, milliseconds = divmod(milliseconds, 1000)
    return f'{hours:02d}:{minutes:02d}:{secs:02d}{separator}{milliseconds:03d}'


def write_sidecars(cues, output, slug):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    validate_cues(cues, cues[-1].end)
    srt, vtt = [], ['WEBVTT\n']
    narration = [f'# Narration: {slug}', '', 'Full narration and description track. The film burns in the shorter captions.', '']
    for number, cue in enumerate(cues, 1):
        srt.append(f'{number}\n{timestamp(cue.start, ",")} --> {timestamp(cue.end, ",")}\n{cue.narration}\n')
        vtt.append(f'{cue.beat_id}\n{timestamp(cue.start, ".")} --> {timestamp(cue.end, ".")}\n{cue.narration}\n')
        narration.extend([f'## {cue.beat_id} ({timestamp(cue.start, ".")}–{timestamp(cue.end, ".")})', '', cue.narration, ''])
    (output / f'{slug}.srt').write_text('\n'.join(srt), encoding='utf-8')
    (output / f'{slug}.vtt').write_text('\n'.join(vtt), encoding='utf-8')
    (output / f'{slug}_narration.md').write_text('\n'.join(narration), encoding='utf-8')
