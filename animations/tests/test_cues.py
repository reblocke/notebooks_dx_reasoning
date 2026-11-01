import json
from pathlib import Path
from core.cues import Cue, validate_cues, write_sidecars
from core.story01 import story
import pytest


def test_story_timing_and_sidecars_match_fixture(tmp_path):
    data = story()
    cues = data['cues']
    assert [(c.beat_id,c.start,c.end) for c in cues] == [(b['beat_id'],b['start'],b['end']) for b in data['fixture']['beats']]
    assert cues[-1].end - cues[-1].start >= 7
    write_sidecars(cues, tmp_path, 'film')
    for ext in ('srt','vtt'):
        text=(tmp_path / ('film.'+ext)).read_text()
        for cue in cues: assert cue.narration in text
    assert '00:03:30,000' in (tmp_path/'film.srt').read_text()


def test_rejects_gaps_and_invalid_intervals():
    with pytest.raises(ValueError): validate_cues([Cue('A',0,2,'c','n'),Cue('B',3,4,'c','n')],4)
    with pytest.raises(ValueError): validate_cues([Cue('A',0,0,'c','n')],0)
