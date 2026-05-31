# AGENTS

## Project purpose
This repository contains interactive teaching notebooks for Bayesian diagnostic reasoning, log-odds evidence, and coherent multiclass likelihood-ratio updates.

## Data constraints
- The notebooks use synthetic examples and hand-entered teaching parameters.
- Do not add patient-level data, PHI, private clinical cases, identifiable screenshots, or proprietary teaching materials.
- If a future dataset is added, include a codebook with variable names, units, allowed values, missingness conventions, and provenance.

## How to orient quickly
- Start with `README.md` for Binder links, file inventory, run order, and dependencies.
- Use `display_reasoning.ipynb` for foundational visual explanations.
- Use `coherent_multi_class.ipynb` for the main multiclass likelihood-ratio demonstration.
- Use `log_odds_evidence_applet.ipynb` for the focused Voila app.

## Local workflow
Create a Python 3.11 environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter lab
```

For smoke tests, prefer opening notebooks and running low-cost cells rather than reworking notebook outputs broadly.

## Binder workflow
Binder uses:

- `runtime.txt` for Python version.
- `requirements.txt` for packages.
- `postBuild` for widget and Voila setup.

When changing dependencies or launch notebooks, verify at least one Binder or local Voila path if feasible.

## Verification before publishing changes
- Run `git diff --check`.
- Ensure Markdown code fences render correctly.
- Do not commit `.ipynb_checkpoints/`, local virtual environments, or executed notebooks unless output changes are intentional.
