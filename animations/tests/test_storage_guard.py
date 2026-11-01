"""The renderer must enforce the user's 5-GiB storage reserve."""
import signal
import sys
from types import SimpleNamespace
import pytest
import render


def test_low_storage_prevents_render_before_process_launch(monkeypatch):
    monkeypatch.setattr(render.shutil, 'disk_usage', lambda _: SimpleNamespace(free=render.RESERVE-1))
    monkeypatch.setattr(sys, 'argv', ['render.py','--goal','01','--quality','preview'])
    monkeypatch.setattr(render.subprocess, 'Popen', lambda *a, **k: pytest.fail('renderer launched'))
    with pytest.raises(SystemExit, match='5 GiB'):
        render.main()


def test_guard_targets_only_the_renderer_process_group(monkeypatch):
    sent=[]
    class Process:
        pid=98765
        def poll(self): return None
        def wait(self,timeout=None): return 0
    monkeypatch.setattr(render.os, 'killpg', lambda pid, sig: sent.append((pid,sig)))
    render.stop_render(Process())
    assert sent == [(98765,signal.SIGTERM)]


def test_coordinate_clinical_cut_enforces_extra_headroom(monkeypatch):
    monkeypatch.setattr(render.shutil, 'disk_usage',
                        lambda _: SimpleNamespace(free=render.RESERVE + render.CLINICAL_HEADROOM - 1))
    monkeypatch.setattr(sys, 'argv', ['render.py', '--goal', '02', '--cut', 'clinical'])
    monkeypatch.setattr(render.subprocess, 'Popen', lambda *a, **k: pytest.fail('renderer launched'))
    with pytest.raises(SystemExit, match='256 MiB'):
        render.main()
