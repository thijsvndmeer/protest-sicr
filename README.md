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

## Parameter Sets

### Parameter set q(1)

| Parameter | Value |
| --- | --- |
| β1 | 0.0103 × 10⁻⁹ |
| β2 | 0.2393 × 10⁻⁶ |
| χ | 0.0085 × 10⁻² |
| n | 1.5885 |
| C0 | 22966 |
| δ1 | 0.0783 |
| δ2 | 0.5362 × 10⁻³ |
| F1 | 246.56 × 10³ |
| F2 | 5441.3 × 10⁶ |

### Parameter set q(2)

| Parameter | Value |
| --- | --- |
| β1 | 0.0194 × 10⁻⁹ |
| β2 | 0.1045 × 10⁻⁶ |
| χ | 0.0163 × 10⁻² |
| n | 1.4993 |
| C0 | 27975 |
| δ1 | 0.0684 |
| δ2 | 0.2167 × 10⁻³ |
| F1 | 250.66 × 10³ |
| F2 | 4712.57 × 10⁶ |

### Why these parameters are chosen

| Parameter | Why it is chosen |
| --- | --- |
| β1 | Captures baseline mobilisation pressure at low protest intensity and is calibrated to keep early dynamics realistic. |
| β2 | Controls nonlinear mobilisation growth from social contagion effects, so it is tuned to match observed escalation. |
| χ | Represents the strength of repression in reducing active mobilisation, so it is chosen to reflect demobilisation pressure. |
| n | Sets the nonlinearity of transmission/saturation dynamics and is selected for stable, identifiable fits. |
| C0 | Sets the initial scale of committed participants and anchors the model to observed starting conditions. |
| δ1 | Governs direct retirement/disengagement under pressure and is chosen to reproduce decline speed in participation. |
| δ2 | Adds higher-order retirement effects at larger protest sizes to capture stronger late-stage demobilisation. |
| F1 | Controls repression-response saturation in the first forcing term and is calibrated to match intervention sensitivity. |
| F2 | Controls repression-response saturation in the second forcing term and is calibrated for high-intensity regime behavior. |

## GitHub Pages

The Jupyter Book is automatically built and deployed on every push to `main` via GitHub Actions. To enable it, go to your repo **Settings → Pages** and set the source to **GitHub Actions**.

## Assumptions & Limitations
- **Data Proxy**: The Iran 2022 dataset provides the cumulative number of arrested individuals as opposed to crowd counts. We proxy the number of active protesters using the daily difference in arrests and an arbitrary scalar.
- **Fixed Parameters**: To avoid identifiability issues on a short dataset, recovery rate `gamma` and the nonlinearity exponent `n` are fixed during fitting.
