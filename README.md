# Comparative SICR Modelling of Protest Demobilisation
### France 2023 vs Iran 2022 — Complexity Project

This project implements the SICR (Susceptible-Informed-Committed-Retired) ODE-based protest model (Alsulami et al., 2022), extended with state repression mechanisms (Petrovskii et al., 2025). It uses differential evolution for model calibration against real-world data to evaluate robustness.

## Repository Structure

```
├── analysis.ipynb        # Core notebook: SICR model, fitting, and plots
├── _config.yml           # Jupyter Book configuration
├── _toc.yml              # Jupyter Book table of contents
├── data/
│   ├── france_2023_weekly.csv
│   └── iran_2022_weekly.csv
├── results/              # Auto-generated fitted parameters (cached)
│   └── fitted_params.json
├── requirements.txt
└── .github/workflows/    # CI: auto-builds & deploys to GitHub Pages
```

## Setup

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Analysis

Launch the notebook from the repo root:
```bash
jupyter notebook analysis.ipynb
```

The notebook contains the full pipeline: ODE system, `differential_evolution` fitting, and comparative visualisations for both datasets. Fitted parameters are automatically cached to `results/fitted_params.json` so subsequent runs skip the expensive calibration step. Delete that file to re-fit from scratch.

## GitHub Pages

The Jupyter Book is automatically built and deployed on every push to `main` via GitHub Actions. To enable it, go to your repo **Settings → Pages** and set the source to **GitHub Actions**.

## Assumptions & Limitations
- **Data Proxy**: The Iran 2022 dataset provides the cumulative number of arrested individuals as opposed to crowd counts. We proxy the number of active protesters using the daily difference in arrests and an arbitrary scalar.
- **Fixed Parameters**: To avoid identifiability issues on a short dataset, recovery rate `gamma` and the nonlinearity exponent `n` are fixed during fitting.
