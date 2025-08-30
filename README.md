# Notebooks for Diagnostic Reasoning (Medicine)

Notebooks demonstrating coherent multi‑class Bayesian updating and related concepts.

## Launch online (Binder)

> The first build can take several minutes while Binder builds the image from `requirements.txt`.

**JupyterLab (editable notebook)**  
[![Binder](https://mybinder.org/badge_logo.svg)](
https://mybinder.org/v2/gh/reblocke/notebooks_dx_reasoning/HEAD?labpath=coherent_multi_class.ipynb
)

**Voila app (read‑only app view)**  
[![Binder](https://mybinder.org/badge_logo.svg)](
https://mybinder.org/v2/gh/reblocke/notebooks_dx_reasoning/HEAD?urlpath=voila/render/coherent_multi_class.ipynb
)

> Prefer reproducibility? Pin to a commit or tag instead of `HEAD`:
> ```
> https://mybinder.org/v2/gh/reblocke/notebooks_dx_reasoning/<COMMIT_OR_TAG>?labpath=coherent_multi_class.ipynb
> https://mybinder.org/v2/gh/reblocke/notebooks_dx_reasoning/<COMMIT_OR_TAG>?urlpath=voila/render/coherent_multi_class.ipynb
> ```

## What’s inside

- `coherent_multi_class.ipynb`: OVR‑coherent projection demo and explanation.
- `.binder/requirements.txt`: runtime deps (NumPy, SciPy, matplotlib, ipywidgets, voila, optional scienceplots).
- `.binder/postBuild`: enables widgets/voila extensions at build time.

## Local run

**With Docker (recommended)**
```bash
docker run -it --rm -p 8888:8888 \
  -v "$PWD":/home/jovyan/work \
  jupyter/scipy-notebook:python-3.11
# open Jupyter URL from the logs; open coherent_multi_class.ipynb
This notebook contains a full explanation of related/foundational concepts: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/reblocke/notebooks_dx_reasoning/HEAD?filepath=display_reasoning.ipynb)
