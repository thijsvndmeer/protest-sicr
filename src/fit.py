import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution
import json
import os
from .simulate import simulate_sicr

def load_data():
    # France
    df_fr = pd.read_csv('data/france_2023_weekly.csv')
    df_fr['date'] = pd.to_datetime(df_fr['date'])
    t_fr = (df_fr['date'] - df_fr['date'].min()).dt.days.values
    N_fr = df_fr['mid'].values
    
    # Iran
    df_ir = pd.read_csv('data/iran_2022_weekly.csv')
    df_ir['Date'] = pd.to_datetime(df_ir['Date'])
    t_ir = (df_ir['Date'] - df_ir['Date'].min()).dt.days.values
    
    # Iran arrests are cumulative.
    arrests = df_ir['Number of Individuals Arrested'].values
    daily_arrests = np.diff(arrests, prepend=0)
    # Filter out negative diffs and smooth
    daily_arrests = np.maximum(0, daily_arrests)
    # Assume 1 arrest ~ 50 protesters on average (arbitrary scaling for proxy)
    N_ir = daily_arrests * 50.0 
    
    return (t_fr, N_fr, df_fr['date'].min()), (t_ir, N_ir, df_ir['Date'].min())

def loss(params, t_obs, N_obs, S0, protest_days):
    y0 = [S0, max(1, N_obs[0]*0.1), max(1, N_obs[0]*0.9), 0] # S, I, C, R
    
    # run simulation
    try:
        sol = simulate_sicr(y0, params, [0, t_obs[-1]+10], protest_days=protest_days, t_eval=t_obs)
        if not sol.success or len(sol.y[0]) != len(t_obs):
            return 1e9
        
        N_sim = sol.y[1] + sol.y[2] # I + C
        # log-space loss
        residuals = np.log(N_obs + 1) - np.log(N_sim + 1)
        return np.sum(residuals**2)
    except Exception:
        return 1e9

def fit_model(country="france"):
    (t_fr, N_fr, min_date_fr), (t_ir, N_ir, min_date_ir) = load_data()
    
    if country == "france":
        t_obs = t_fr
        N_obs = N_fr
        S0 = 4000000
        protest_days = t_fr # 14 national days of action
    else:
        t_obs = t_ir
        N_obs = N_ir
        S0 = 6000000
        protest_days = t_ir # continuous daily protests reported
        
    bounds = [
        (1e-9, 1e-5),   # b1
        (1e-9, 1e-5),   # b2
        (0.01, 1.0),    # chi
        (0.001, 0.5),   # d11
        (0.001, 0.5),   # d21
        (0.01, 0.01001),# gamma (fixed roughly)
        (1e4, 1e6),     # C0
        (4.0, 4.00001), # n (fixed roughly)
        (0.0, 1.0),     # eps12
        (0.0, 0.5),     # eps22
    ]
    
    print(f"Starting fitting for {country}...")
    result = differential_evolution(
        loss, bounds, args=(t_obs, N_obs, S0, protest_days),
        seed=42, popsize=15, maxiter=50, # Reduced for speed in pipeline building
        polish=True, workers=1, tol=1e-2,
    )
    print(f"Fit completed. Success: {result.success}, Loss: {result.fun}")
    
    # Save parameters
    os.makedirs('results', exist_ok=True)
    with open(f'results/{country}_params.json', 'w') as f:
        json.dump(list(result.x), f)
        
    return result.x

if __name__ == "__main__":
    fit_model("france")
    fit_model("iran")
