"""Regenerate only the two corrected teaching attachments from the declared fixture."""

import base64
import io
import json
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from diagnostic_reasoning import bayesian_update_prob, ovr_project_posterior  # noqa: E402


def regenerate():
    fixture = json.loads((ROOT / "tests/fixtures/reference_cases.json").read_text())[
        "worked"
    ]
    p, lr = np.array(fixture["prior"]), np.array(fixture["ovr"])
    slices = np.array([bayesian_update_prob(a, b) for a, b in zip(p, lr)])
    naive = slices / slices.sum()
    raw_score = p * lr / (p @ lr)
    fitted = ovr_project_posterior(p, lr)
    implied = (naive / (1 - naive)) / (p / (1 - p))
    names, y = ["A", "B", "C"], np.arange(3)
    notebook_path = ROOT / "coherent_multi_class.ipynb"
    notebook = json.loads(notebook_path.read_text())
    previews = ROOT / "tmp/visual-qc"
    previews.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 11, "axes.titlesize": 12})

    for cell_index, attachment in [(7, "image-2.png"), (10, "image.png")]:
        fig, axes = plt.subplots(1, 2, figsize=(10, 4.4), layout="constrained")
        if cell_index == 7:
            axes[0].barh(
                y - 0.17,
                slices,
                0.32,
                label="Independent binary slice",
                color="#426d9c",
            )
            axes[0].barh(
                y + 0.17,
                naive,
                0.32,
                label="After dividing by slice sum",
                color="#b66a35",
                hatch="//",
            )
            axes[0].set_title("Binary slices change when normalized")
            axes[0].legend(loc="lower right", fontsize=9)
            axes[1].barh(y, raw_score, 0.5, color="#777777")
            axes[1].set_title("Different operation: normalize prior × raw OVR")
            for k, value in enumerate(raw_score):
                axes[1].text(value + 0.015, k, f"{value:.4f}", va="center")
            fig.suptitle("Same inputs, different naive operations", fontsize=14)
        else:
            for offset, values, label, marker in [
                (-0.15, p, "Prior", "s"),
                (0, naive, "Binary slices normalized", "x"),
                (0.15, fitted.posterior, "Coherent fit candidate", "o"),
            ]:
                axes[0].scatter(values, y + offset, label=label, marker=marker, s=50)
            axes[0].set_title("Compare posterior probabilities")
            axes[0].legend(loc="lower right", fontsize=9)
            axes[1].barh(
                y - 0.17, np.log(lr), 0.32, label="Input log OVR LR", color="#426d9c"
            )
            axes[1].barh(
                y + 0.17,
                np.log(fitted.fitted_ovr_lr),
                0.32,
                label="Fitted log OVR LR",
                color="#b66a35",
                hatch="//",
            )
            axes[1].set(
                xlabel="Natural-log LR", title="The fit adjusts incompatible LRs"
            )
            axes[1].axvline(0, color="gray", lw=0.8)
            axes[1].legend(loc="lower right", fontsize=9)
            fig.suptitle(
                f"Coherent candidate; data log-LR RMSE = {fitted.rmse_logLR:.6f}",
                fontsize=14,
            )
        for ax in axes:
            ax.set(yticks=y, yticklabels=names, ylim=(2.7, -0.7))
            ax.spines[["top", "right"]].set_visible(False)
        axes[0].set(xlim=(0, 1), xlabel="Probability")
        if cell_index == 7:
            axes[1].set(xlim=(0, 1), xlabel="Probability")
        data = io.BytesIO()
        fig.savefig(data, format="png", dpi=150)
        preview = previews / f"worked-cell-{cell_index}.png"
        preview.write_bytes(data.getvalue())
        plt.close(fig)
        cell = notebook["cells"][cell_index - 1]
        cell.setdefault("attachments", {})[attachment] = {
            "image/png": base64.b64encode(data.getvalue()).decode()
        }

    def values(a):
        return "(" + ", ".join(f"{x:.6f}" for x in a) + ")"

    notebook["cells"][6]["source"] = f"""### Worked comparison: binary normalization

The declared fixture is prior `(0.5,0.3,0.2)` and OVR LRs `(4,3,2)`. Independent binary slices are {values(slices)}, summing to {slices.sum():.9f}. Dividing by their sum gives {values(naive)}, with implied OVRs {values(implied)}. Every slice decreases here; normalization does not universally inflate unlikely diagnoses.

A different operation, normalizing `prior*raw_OVR`, gives {values(raw_score)}. That operation treats raw OVRs as common-reference likelihood scores and is not the correct OVR update. The panels distinguish these operations explicitly.

![Two different naive operations using the exact declared fixture.](attachment:image-2.png)
""".splitlines(keepends=True)
    notebook["cells"][9]["source"] = f"""### Coherent one-vs-rest fit candidate

We fit baseline-anchored scores with objective `0.5 * [sum(w_k*(fitted_logLR_k-input_logLR_k)^2) + reg*sum(nonbaseline_scores^2)]`. This specifies error on the natural-log LR scale; it does not establish a noise distribution or prove that fitting corrects bias.

For the same declared fixture, baseline 0, unit weights and `reg=1e-6`, fitted OVRs are {values(fitted.fitted_ovr_lr)} and posterior is {values(fitted.posterior)}. Unweighted data-only natural-log LR RMSE is {fitted.rmse_logLR:.9f}. Weighted data SSE is {fitted.diagnostics["weighted_data_sse"]:.9f}; ridge penalty is {fitted.diagnostics["ridge_penalty"]:.9g}.

The optimizer returns a coherent candidate, not a demonstrated minimum. Ridge is baseline-dependent shrinkage, not a universal numerical guarantee. Coherence does not establish empirical calibration.

![Coherent candidate compared with binary normalization, and raw versus fitted log OVR LRs.](attachment:image.png)
""".splitlines(keepends=True)
    notebook_path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    regenerate()
