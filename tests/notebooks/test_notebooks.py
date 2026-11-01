"""Kernel execution and actual registered callbacks, separate from numerical tests."""

import json
from pathlib import Path
import sys

import nbformat
from nbclient import NotebookClient
import pytest

ROOT = Path(__file__).resolve().parents[2]
WIDGETS = {
    "coherent_multi_class": {13: "core_ovr"},
    "display_reasoning": {69: "display_qual", 71: "display_cont"},
    "multi_class": {1: "multi_common", 2: "multi_ovr"},
    "multi_class_cont": {
        1: "cont_common",
        3: "cont_mixed",
        5: "cont_ovr",
        6: "cont_scores",
    },
    "log_odds_evidence_applet": {},
}

BOOTSTRAP = r"""
import contextlib, io
import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets
_uis, _before = {}, {}

def _walk(widget):
    yield widget
    for child in getattr(widget, 'children', ()):
        yield from _walk(child)

def _click(ui, setting='nontrivial'):
    all_widgets = list(_walk(ui))
    count = next(w for w in all_widgets if isinstance(w, widgets.IntSlider) and w.description == 'Diagnoses')
    if setting != 'default': count.value = 3
    rows = [w for w in _walk(ui) if isinstance(w, widgets.VBox) and
            len(w.children) >= 3 and isinstance(w.children[0], widgets.Text)]
    if setting != 'default':
        for i, row in enumerate(rows):
            prior = row.children[1]
            if isinstance(prior, widgets.Dropdown):
                prior.value = ['LIKELY', 'UNLIKELY', 'UNCERTAIN'][i]
                for feature in row.children[2:]: feature.value = 0
                row.children[[2, 3, 4][i]].value = 1
            else:
                prior.value = 0. if setting == 'invalid' else [.5, .3, .2][i]
                row.children[2].value = [4., 3., 2.][i]
    plots = []
    show = plt.show
    plt.show = lambda *a, **k: plots.append(plt.gcf())
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            next(w for w in _walk(ui) if isinstance(w, widgets.Button) and w.description == 'Calculate').click()
    finally:
        plt.show = show
    if setting == 'invalid':
        assert 'Cannot calculate:' in output.getvalue(), output.getvalue()
        assert not plots, 'invalid inputs displayed a normal plot'
        return None
    assert len(plots) == 1, output.getvalue()
    bars = plots[0].axes[0].patches
    post = np.array([bar.get_height() for bar in bars[1::2]])
    assert len(post) == count.value
    assert np.isclose(post.sum(), 1)
    plt.close(plots[0])
    return post
"""


@pytest.mark.parametrize("name", WIDGETS)
def test_fresh_kernel_and_retained_callbacks(name, tmp_path, monkeypatch):
    # An explicit temporary kernelspec prevents accidental execution in another Python.
    kernel_dir = tmp_path / "kernels" / "diagnostic-repair-tests"
    kernel_dir.mkdir(parents=True)
    (kernel_dir / "kernel.json").write_text(
        json.dumps(
            {
                "argv": [
                    sys.executable,
                    "-m",
                    "ipykernel_launcher",
                    "-f",
                    "{connection_file}",
                ],
                "display_name": "Diagnostic repair tests",
                "language": "python",
            }
        )
    )
    monkeypatch.setenv("JUPYTER_PATH", str(tmp_path))
    book = nbformat.read(ROOT / f"{name}.ipynb", as_version=4)
    originals = list(book.cells)
    cells = [nbformat.v4.new_code_cell(BOOTSTRAP)]
    for index, cell in enumerate(originals, 1):
        cells.append(cell)
        if name == "display_reasoning" and index == 52:
            cells.append(nbformat.v4.new_code_cell("_binary_ui = predictor_wrapper.widget"))
        if name == "log_odds_evidence_applet" and index == 9:
            cells.append(nbformat.v4.new_code_cell("_bins_ui = panel_qualitative_bins()"))
        if index in WIDGETS[name]:
            tag = WIDGETS[name][index]
            cells.append(
                nbformat.v4.new_code_cell(f"""
_uis['{tag}'] = widget_{tag}
_click(_uis['{tag}'], 'default')
_before['{tag}'] = _click(_uis['{tag}'])
""")
            )
    checks = """
for tag, ui in _uis.items():
    np.testing.assert_allclose(_click(ui), _before[tag], atol=1e-10,
        err_msg=f'{tag} changed after later cells executed')
    rows = [w for w in _walk(ui) if isinstance(w, widgets.VBox) and len(w.children) >= 3 and isinstance(w.children[0], widgets.Text)]
    if not isinstance(rows[0].children[1], widgets.Dropdown):
        _click(ui, 'invalid')
        _click(ui)
"""
    if name == "multi_class_cont":
        later = {i: originals[i - 1].source for i in (5, 6)}
        checks += f"""
for order in [(5, 6), (6, 5)]:
    for index in order: exec({later!r}[index])
    for tag, ui in _uis.items():
        np.testing.assert_allclose(_click(ui), _before[tag], atol=1e-10)
mixed = _uis['cont_mixed']
method = next(w for w in _walk(mixed) if isinstance(w, widgets.Dropdown) and w.description == 'Method')
method.value = 'softmax_scores'
_click(mixed)
assert all(w.description == 'LR vs ref:' for w in _walk(mixed)
           if isinstance(w, widgets.FloatLogSlider) and w.description != 'Reg (L2)')
# Inject an extreme input through the actual callback without widening UI ranges.
original_normalize = normalize_priors
original_show = plt.show
plots, output = [], io.StringIO()
try:
    normalize_priors = lambda *a, **k: original_normalize([1e-200, 1e200], **k)
    plt.show = lambda *a, **k: plots.append(plt.gcf())
    with contextlib.redirect_stdout(output):
        next(w for w in _walk(mixed) if isinstance(w, widgets.Button)).click()
    assert 'numerical range' in output.getvalue(), output.getvalue()
    assert not plots
finally:
    normalize_priors = original_normalize
    plt.show = original_show
method.value = 'ovr_projection'
_click(mixed)
with contextlib.redirect_stdout(io.StringIO()):
    p, likelihood = np.array([.5, .3, .2]), np.array([.4, .2, .1])
    diagnoses = [dict(name=str(i), pretest=p[i], loglr=np.log(likelihood[i])) for i in range(3)]
    common = generalized_predictor_wrapper_cont_mixed(diagnoses, method='softmax_scores')
    for i, row in enumerate(diagnoses):
        rest = np.arange(3) != i
        row['loglr'] = np.log(likelihood[i] / np.average(likelihood[rest], weights=p[rest]))
    ovr = generalized_predictor_wrapper_cont_mixed(diagnoses, reg=0)
expected = p * likelihood / np.sum(p * likelihood)
np.testing.assert_allclose(common['predicted_probs'], expected, atol=1e-9)
np.testing.assert_allclose(ovr['predicted_probs'], expected, atol=1e-9)
"""
    if name == "coherent_multi_class":
        checks += """
from types import SimpleNamespace
original_solver = ovr_project_posterior
plots = []
original_show = plt.show
try:
    plt.show = lambda *a, **k: plots.append(plt.gcf())
    ovr_project_posterior = lambda *a, **k: SimpleNamespace(success=False,
        diagnostics={'fit_status': 'optimizer_failed'}, message='forced fitting failure')
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        next(w for w in _walk(_uis['core_ovr']) if isinstance(w, widgets.Button)).click()
    assert 'forced fitting failure' in output.getvalue()
    assert not plots
finally:
    ovr_project_posterior = original_solver
    plt.show = original_show
for scale in ['linear', 'log', 'odds']:
    bayesian_update_plot(.5, [2], scale=scale)
"""
    if name == "log_odds_evidence_applet":
        checks += """
limits = []
for prior, lr in [(.99, 10), (.01, .1), (.5, 2)]:
    fig, post = make_update_rulers(prior, lr)
    limits.append(fig.axes[1].get_xlim())
    x = fig.axes[1].collections[0].get_offsets()[:, 0]
    assert min(x) > limits[-1][0] and max(x) < limits[-1][1]
    fig.canvas.draw()
    plt.close(fig)
assert limits[0] == limits[1] == limits[2]
assert float(fmt_lr(lr_for_probability_move(.99, .01))) > 0
assert category_for_probability(.37) == 'Unlikely'
"""
    if name == "display_reasoning":
        checks += """
def _check_binary(ui):
    controls = {w.description: w for w in ui.children if hasattr(w, 'value')}
    with contextlib.redirect_stdout(io.StringIO()):
        controls['qual_pretest'].value = 'HIGHLY_LIKELY'
        for key in ['major_positive', 'major_negative', 'minor_positive', 'minor_negative']:
            controls[key].value = 0
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        controls['major_negative'].value = 3
    assert 'corresponds to: LIKELY' in output.getvalue(), output.getvalue()
_check_binary(_binary_ui)
"""
        checks += f"exec({originals[51].source!r})\n_check_binary(_binary_ui)\n_check_binary(predictor_wrapper.widget)\n"
    if name == "log_odds_evidence_applet":
        checks += """
def _check_bins(ui):
    controls = {w.description: w for w in _walk(ui) if hasattr(w, 'value') and hasattr(w, 'description')}
    captured = []
    original_display = globals()['display']
    globals()['display'] = captured.append
    try:
        controls['Start'].value = 0
        controls['Major +'].value = 0
        controls['Major -'].value = 2
        controls['Minor +'].value = 5
        controls['Minor -'].value = 1
        captured.clear()
        controls['Show thresholds'].value = not controls['Show thresholds'].value
    finally:
        globals()['display'] = original_display
    table = captured[1].data
    assert '>Unlikely (18.2%)' in table, table
    points = captured[0].axes[0].collections[0].get_offsets()[:, 0]
    assert points[-1] == -1.5, points
_check_bins(_bins_ui)
"""
        checks += f"exec({originals[8].source!r})\n_check_bins(_bins_ui)\n_check_bins(panel_qualitative_bins())\n"
    cells.append(nbformat.v4.new_code_cell(checks))
    book.cells = cells
    NotebookClient(
        book,
        kernel_name="diagnostic-repair-tests",
        timeout=120,
        resources={"metadata": {"path": str(ROOT)}},
    ).execute()


def test_standalone_ovr_cell():
    source = (
        nbformat.read(ROOT / "multi_class_cont.ipynb", as_version=4).cells[4].source
    )
    # Fresh namespace, including no Layout import from an earlier notebook cell.
    from IPython.display import display

    namespace = {"display": display}
    exec(compile(source, "standalone_ovr_cell", "exec"), namespace)
    assert namespace["widget_cont_ovr"] is not None
