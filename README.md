# Comparative SICR Modelling of Protest Demobilisation
### France 2023 vs Iran 2022 — Complexity Project

This project implements the SICR (Susceptible-Informed-Committed-Retired) ODE-based protest model (Alsulami et al., 2022), extended with state repression mechanisms (Petrovskii et al., 2025). It uses differential evolution for model calibration against real-world data and Sobol global sensitivity analysis to evaluate robustness.

## Directory Structure
- `data/`: Contains protest data for France (pension reform strikes 2023) and Iran (Mahsa Amini protests 2022).
- `src/`: Core Python modules for the model:
  - `model.py`: Implements the core SICR equations and state repression RHS.
  - `simulate.py`: Solves the ODE system using LSODA and validates population conservation.
  - `fit.py`: Calibrates model parameters using `scipy.optimize.differential_evolution`.
  - `sensitivity.py`: Sobol sensitivity analysis using `SALib`.
  - `scenarios.py`: Simulates various hypothesis testing scenarios (S0-S4).
  - `plots.py`: Generates the resulting figures.
- `results/`: Output directory where parameters, analysis json, and figures are saved.
- `notebooks/`: Jupyter notebooks for interactive data exploration.

## Setup Instructions

1. Ensure you have Python 3 installed.
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
## Running the Pipeline

To run the complete pipeline (Fitting -> Sensitivity -> Scenarios -> Plots):
```bash
python main.py
```

The resulting figures (`fig1_baseline.png`, `fig2_sensitivity.png`, etc.) will be saved into the `results/` directory.

## Assumptions & Limitations
- **Data Proxy**: The Iran 2022 dataset provides the cumulative number of arrested individuals as opposed to crowd counts. We proxy the number of active protesters using the daily difference in arrests and an arbitrary scalar.
- **Fixed Parameters**: To avoid identifiability issues on a short dataset, recovery rate `gamma` and the nonlinearity exponent `n` are fixed during fitting.
