import copy
import hashlib
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import pytest
from core.films import resolve_film, FILMS
from core.cues import Cue, validate_cues
from core.subtitles import validate_segments, subtitle_rows
from core.narration import write_narrated_sidecars
from core.narration import make_narration
from core.provenance import capture_render_sources, input_names, digest, verify_render_sources
from scripts.finalize_film import fixture_contract, validate_segmented_tracks
from render import apply_clinical_timing, check_source_cadence

ROOT=Path(__file__).resolve().parents[1]


def test_concat_rounding_can_be_normalized_without_hiding_timeline_defects():
    # Real final export had a five-tick shift after a partial-movie boundary.
    frames=[{'best_effort_timestamp': i*512-(5 if i>=10 else 0)} for i in range(30)]
    result=check_source_cadence(frames,'1/15360',30,1)
    assert result['maximum_timestamp_error_seconds']==pytest.approx(5/15360)
    for altered in (frames[:-1],frames+[frames[-1]]):
        with pytest.raises(ValueError,match='frame count'):
            check_source_cadence(altered,'1/15360',30,1)
    for shift in (512,-512,32):
        altered=copy.deepcopy(frames);altered[10]['best_effort_timestamp']+=shift
        with pytest.raises(ValueError,match='cadence'):
            check_source_cadence(altered,'1/15360',30,1)


@pytest.mark.parametrize('goal',['05','06'])
def test_new_routes_timing_fixtures_and_source_isolation(goal,tmp_path):
    film=resolve_film(goal)
    assert film==resolve_film(goal,'clinical') and film.narrated
    with pytest.raises(ValueError):resolve_film(goal,'original')
    assert fixture_contract(film.slug,film.scene)==(film.fixture_path,film.fixture_hash)
    assert digest(ROOT/film.fixture_path)==film.fixture_hash
    data=importlib.import_module(film.story_module).story();cues=data['cues']
    assert len(cues)==(8 if goal=='05' else 12)
    validate_cues(cues,175 if goal=='05' else 180)
    validate_segments(cues,data['speech_segments'])
    narration={'speech_intervals':[{'beat_id':c.beat_id,'start':c.start+.1,'end':c.start+1} for c in cues],
               'subtitle_intervals':[]}
    timing={'cues':[vars(c).copy() for c in cues]}
    apply_clinical_timing(timing,cues,narration,goal)
    assert timing['final_hold_seconds']==7 and cues[-1].end-cues[-1].start==7
    assert timing['events']==data['events']
    assert timing['cues'][-1]['caption_fully_visible_at']<=cues[-1].start
    for event in data['events']:
        assert 0<=event['start']<=event['settled']<cues[-1].end
        for t in (event['start'],event['settled']):assert t*15==pytest.approx(round(t*15))
    output=tmp_path/'output';output.mkdir()
    for name in input_names(film.slug,True):(output/name).write_text('synthetic input')
    binding=capture_render_sources(ROOT,output,film.slug,film.scene,True,'preview')
    snapshot=Path(binding['snapshot']);record=json.loads((snapshot/'render_sources.json').read_text())
    assert record['source_sha256'][film.fixture_path]==film.fixture_hash
    other=resolve_film('06' if goal=='05' else '05')
    assert other.fixture_path not in record['source_sha256']
    code="""import importlib, pathlib, sys
root=pathlib.Path(sys.argv[1]); module=importlib.import_module(sys.argv[2]); module.story()
importlib.import_module('scenes.'+sys.argv[3])
for name,m in list(sys.modules.items()):
    if name.startswith(('core.','scenes.')) and getattr(m,'__file__',None):
        assert pathlib.Path(m.__file__).is_relative_to(root), (name,m.__file__)
"""
    subprocess.run([sys.executable,'-B','-c',code,str(snapshot),film.story_module,film.scene[:-3]],
                   cwd=tmp_path,env={**os.environ,'PYTHONPATH':str(snapshot)},check=True,capture_output=True)
    movie=output/'movie.mp4';movie.write_bytes(b'synthetic movie')
    storage={'render_sources':binding,'video_sha256':digest(movie)}
    verify_render_sources(storage,movie,output,slug=film.slug,scene=film.scene,audio_expected=True)
    (snapshot/film.fixture_path).write_text('{}')
    with pytest.raises(ValueError,match='snapshot changed'):
        verify_render_sources(storage,movie,output,slug=film.slug,scene=film.scene,audio_expected=True)


@pytest.mark.parametrize('goal',['preflight','01','02','03','04'])
def test_legacy_defaults_and_fixture_identity(goal):
    film=resolve_film(goal)
    assert film.cut=='original' and not film.narrated
    assert film.fixture_path=='data/manim_fixtures.json'
    assert film.fixture_hash=='d4204afd2e4ee8e8bcac9cd6d5842a4dbe172932a250930516d5f62b1922407b'
    if goal!='preflight':assert resolve_film(goal,'clinical').narrated
    else:
        with pytest.raises(ValueError):resolve_film(goal,'clinical')


def measured_example():
    cues=[Cue('C01',0,10,'Caption','One statement. Another statement.')]
    rows=[{'beat_id':'C01','segment_id':'C01_01','text':'One statement.','start':.1,'end':2},
          {'beat_id':'C01','segment_id':'C01_02','text':'Another statement.','start':2.12,'end':4}]
    record={'speech_intervals':[{'beat_id':'C01','start':.1,'end':4}],'subtitle_intervals':rows}
    return cues,record


def test_segmented_sidecars_follow_measured_phrases_and_validate_exact_text(tmp_path):
    cues,record=measured_example()
    write_narrated_sidecars(cues,record,tmp_path,'new')
    tracks=[(tmp_path/f'new.{ext}').read_text() for ext in ('srt','vtt')]
    assert '00:00:02,120 --> 00:00:04,000' in tracks[0]
    timing={'cues':[vars(c) for c in cues],'subtitle_intervals':record['subtitle_intervals']}
    validate_segmented_tracks(timing,record,tracks)
    for altered in [tracks[0].replace('One statement.','Another statement.'),tracks[0].replace('00:00:02,120','00:00:02,121')]:
        with pytest.raises(ValueError):validate_segmented_tracks(timing,record,[altered])


@pytest.mark.parametrize('fault',['missing','duplicate','overlap','outside','changed_text','speech_mismatch'])
def test_measured_subtitle_defects_are_rejected(fault):
    cues,record=measured_example();rows=record['subtitle_intervals']
    if fault=='missing':rows.pop()
    elif fault=='duplicate':rows[1]['segment_id']=rows[0]['segment_id']
    elif fault=='overlap':rows[1]['start']=1.9
    elif fault=='outside':rows[1]['end']=11
    elif fault=='changed_text':rows[1]['text']='Different claim.'
    else:record['speech_intervals'][0]['end']=5
    with pytest.raises(ValueError):subtitle_rows(cues,record)


def test_narration_reuse_binds_segmentation_voice_and_audio(tmp_path):
    cues,record=measured_example()
    segments={'C01':['One statement.','Another statement.']}
    audio=tmp_path/'new_narration.wav';audio.write_bytes(b'measured synthetic audio')
    record.update(voice='Samantha',rate_wpm=160,segmentation_version=1,
        cue_source_sha256=hashlib.sha256(json.dumps([vars(c) for c in cues],sort_keys=True).encode()).hexdigest(),
        segment_source_sha256=hashlib.sha256(json.dumps(segments,sort_keys=True).encode()).hexdigest(),
        audio_sha256=digest(audio))
    (tmp_path/'new_narration_audio.json').write_text(json.dumps(record))
    assert make_narration(cues,tmp_path,'new',segments=segments)==record
    with pytest.raises(ValueError,match='does not match'):
        make_narration(cues,tmp_path,'new',segments={'C01':['One statement. Another statement.']})
    with pytest.raises(ValueError,match='does not match'):
        make_narration(cues,tmp_path,'new',segments=segments,rate=170)
    audio.write_bytes(b'different audio')
    with pytest.raises(ValueError,match='does not match'):
        make_narration(cues,tmp_path,'new',segments=segments)
