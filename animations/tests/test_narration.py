import pytest

from core.narration import write_narrated_sidecars
from core.story01_clinical import story
from core.story02_clinical import story as coordinates_story


def test_narration_sidecars_follow_spoken_intervals(tmp_path):
    cues = story()['cues']
    intervals = [{'beat_id': cue.beat_id, 'start': cue.start + .1, 'end': cue.start + 2}
                 for cue in cues]
    write_narrated_sidecars(cues, {'speech_intervals': intervals}, tmp_path, 'clinical')
    srt = (tmp_path / 'clinical.srt').read_text()
    assert '00:00:00,100 --> 00:00:02,000' in srt
    assert '00:00:47,100 --> 00:00:49,000' in srt
    for cue in cues:
        assert cue.narration in srt
    intervals[0]['end'] = 10
    with pytest.raises(ValueError, match='beyond its cue'):
        write_narrated_sidecars(cues, {'speech_intervals': intervals}, tmp_path, 'clinical')


def test_coordinate_cut_sidecars_use_its_own_final_interval(tmp_path):
    cues = coordinates_story()['cues']
    intervals = [{'beat_id': cue.beat_id, 'start': cue.start + .1, 'end': cue.start + 2}
                 for cue in cues]
    write_narrated_sidecars(cues, {'speech_intervals': intervals}, tmp_path, 'coordinates')
    srt = (tmp_path / 'coordinates.srt').read_text()
    assert '00:00:43,100 --> 00:00:45,000' in srt
    assert all(cue.narration in srt for cue in cues)
