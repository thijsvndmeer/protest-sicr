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

| Parameter | Description / Physical Rationale |
| --- | --- |
| $\beta_1$ | Transmission rate from Susceptible ($S$) to Informed ($I$) via contact with Informed individuals. Captures baseline mobilisation from active protesters. |
| $\beta_2$ | Transmission rate from Susceptible ($S$) to Informed ($I$) via contact with Committed ($C$) individuals. Captures social contagion from fully committed participants. |
| $\chi$ | Transition rate from Informed ($I$) to Committed ($C$) (representing protesters committing to the movement). |
| $\delta_{11}$ | Baseline exit rate of Informed individuals to Retired ($R$). |
| $\delta_{21}$ | Baseline exit rate of Committed individuals to Retired ($R$). |
| $\gamma$ | Recovery rate from Retired ($R$) back to Susceptible ($S$), representing how quickly tired/arrested protesters re-enter the pool of potential participants. |
| $C_0$ | Solidarity capacity threshold. When $I+C \gg C_0$, crowd solidarity reduces the disengagement/exit rate of Committed individuals. |
| $n$ | Nonlinearity exponent governing the steepness of the crowd solidarity effect. |
| $\epsilon_0$ | Recruitment enhancement factor on protest days (boosts transmission rates $\beta_1, \beta_2$). |
| $\epsilon_{12}$ | Protest-day exit/repression enhancement factor for Informed individuals. |
| $\epsilon_{22}$ | Protest-day exit/repression enhancement factor for Committed individuals. |

## GitHub Pages

The Jupyter Book is automatically built and deployed on every push to `main` via GitHub Actions. To enable it, go to your repo **Settings → Pages** and set the source to **GitHub Actions**.

## Assumptions & Limitations
- **Data Proxy**: The Iran 2022 dataset provides the cumulative number of arrested individuals as opposed to crowd counts. We proxy the number of active protesters using the daily difference in arrests and an arbitrary scalar.
- **Iran Data Zero-Arrest Artifact**: On days when no new arrests are added to the cumulative count (a flat trend), the daily difference is exactly `0`. When plotting on a log-scale, these zero-value days are capped at $1.0$ (via `np.maximum(1, N_ir)`), which creates the horizontal band of observed points visible at the bottom of the Iran chart.
- **Fixed Parameters**: To avoid identifiability issues on a short dataset, the nonlinearity exponent $n$ (fixed at `4.0`) and the recovery rate $\gamma$ (fixed at `0.05`) are fixed during fitting.
