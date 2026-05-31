# Notebooks for Diagnostic Reasoning in Medicine

> Interactive notebooks and Binder/Voila applets demonstrating Bayesian diagnostic reasoning, log-odds evidence, and coherent multiclass likelihood-ratio updates.

## Links

- Repository: <https://github.com/reblocke/notebooks_dx_reasoning>
- Editable Binder notebook: [coherent multiclass notebook](https://mybinder.org/v2/gh/reblocke/notebooks_dx_reasoning/HEAD?labpath=coherent_multi_class.ipynb)
- Read-only Voila app: [coherent multiclass app](https://mybinder.org/v2/gh/reblocke/notebooks_dx_reasoning/HEAD?urlpath=voila/render/coherent_multi_class.ipynb)
- Log-odds evidence applet: [Voila applet](https://mybinder.org/v2/gh/reblocke/notebooks_dx_reasoning/HEAD?urlpath=voila/render/log_odds_evidence_applet.ipynb)

## Description

These notebooks are teaching and exploration materials for medical diagnostic reasoning. They use simulated examples and mathematical demonstrations to show how likelihood ratios move diagnostic probabilities, why one-vs-rest updates can become incoherent in multiclass settings, and how log-odds can serve as an evidence scale.

There are no patient-level data, clinical records, or protected health information in this repository.

## Authors, Funding, and Acknowledgments

- Maintainer: Brian W. Locke (`@reblocke`)
- ORCID: <https://orcid.org/0000-0002-3588-5238>
- Funding: no project-specific external funding is claimed for this teaching repository.

## File Inventory

| File | Purpose |
|---|---|
| `coherent_multi_class.ipynb` | Main notebook demonstrating coherent multiclass likelihood-ratio updating. |
| `log_odds_evidence_applet.ipynb` | Voila applet for exploring evidence on the log-odds scale. |
| `display_reasoning.ipynb` | Foundational visualization notebook for diagnostic reasoning concepts. |
| `multi_class.ipynb` | Earlier multiclass diagnostic reasoning exploration. |
| `multi_class_cont.ipynb` | Continuation notebook for multiclass reasoning intuition. |
| `requirements.txt` | Python package dependencies for Binder/local runs. |
| `runtime.txt` | Binder Python runtime pin. |
| `postBuild` | Binder setup for ipywidgets and Voila extensions. |

## Data and Codebook

The notebooks use synthetic examples and hand-entered teaching parameters. There are no tabular research datasets to document. Any new data file added later should include a codebook with variable names, units, allowed values, missing-value conventions, and provenance.

## Run Order

For most users:

1. Start with `display_reasoning.ipynb` for the broad visual explanation.
2. Open `coherent_multi_class.ipynb` for the main multiclass likelihood-ratio demonstration.
3. Use `log_odds_evidence_applet.ipynb` as a focused interactive applet.

The older `multi_class.ipynb` and `multi_class_cont.ipynb` notebooks are retained as exploratory background.

## Launch Online

The first Binder build can take several minutes while dependencies are installed from `requirements.txt`.

Editable JupyterLab:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/reblocke/notebooks_dx_reasoning/HEAD?labpath=coherent_multi_class.ipynb)

Read-only Voila app:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/reblocke/notebooks_dx_reasoning/HEAD?urlpath=voila/render/coherent_multi_class.ipynb)

For durable teaching links, replace `HEAD` in Binder URLs with a commit SHA or release tag.

## Local Run

Create an environment with Python 3.11, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter lab
```

Or use Docker:

```bash
docker run -it --rm -p 8888:8888 \
  -v "$PWD":/home/jovyan/work \
  jupyter/scipy-notebook:python-3.11
```

Open the Jupyter URL from the logs, then open `coherent_multi_class.ipynb`.

## Dependencies

Runtime requirements are listed in `requirements.txt`:

| Package | Role |
|---|---|
| `numpy`, `scipy` | Probability calculations and numerical work. |
| `matplotlib`, `scienceplots` | Plots and visual styling. |
| `ipywidgets` | Interactive notebook controls. |
| `voila` | Read-only app rendering from notebooks. |

Binder uses Python 3.11 from `runtime.txt`.

## Citation

This is a teaching repository rather than a peer-reviewed publication. If you reuse these notebooks, cite the repository URL and commit SHA or tag used.

Suggested citation:

> Locke BW. Notebooks for Diagnostic Reasoning in Medicine. GitHub repository. <https://github.com/reblocke/notebooks_dx_reasoning>.

## License

Code and original teaching text are released under the [MIT License](./LICENSE). Third-party package names and Binder badges remain under their respective owners' terms.

## Contributing

Issues and pull requests that improve clarity, mathematical correctness, accessibility, or reproducibility are welcome. Do not add patient data, private clinical cases, or identifiable screenshots.

## Contact

Maintainer: Brian W. Locke (`@reblocke`)
