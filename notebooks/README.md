# Notebooks

`eda_mimii_fan.ipynb` is the exploratory notebook behind Sections IV and V of the HIT401 interim report: clip inventory, waveforms and spectrograms, band energies, windowing, and the initial Mahalanobis distance test on fan id_00 (Fig. 4-1 and the threshold-sweep table). It is committed with its outputs.

## Requirements

Python 3.11 or later with `numpy`, `pandas`, `matplotlib`, `scipy` and `scikit-learn`, plus Jupyter. These are not part of the backend's `uv` environment; install them into any environment, for example:

```bash
pip install numpy pandas matplotlib scipy scikit-learn jupyterlab
```

## Data

The notebook reads the MIMII fan recordings at 6 dB SNR (Purohit et al., 2019, https://zenodo.org/record/3384388) from `data/6_dB/fan/id_XX/{normal,abnormal}/`. The dataset is not in the repository. Fetch it from the repository root with:

```bash
python scripts/fetch_mimii.py --type fan --snr 6
```

## Run

From the repository root:

```bash
jupyter lab notebooks/eda_mimii_fan.ipynb
```

Run all cells in order. The distance test takes under a minute on a laptop.
