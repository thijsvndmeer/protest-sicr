import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution
from scipy.integrate import solve_ivp
from sicr import sicr_rhs, make_P_func

# Load Data
df_fr = pd.read_csv('data/france_2023_weekly.csv')
df_fr['date'] = pd.to_datetime(df_fr['date'])
t_fr = (df_fr['date'] - df_fr['date'].min()).dt.days.values
N_fr = df_fr['mid'].values

def simulate_sicr_dense(y0, params, t_span, protest_days, t_eval=None, dense_output=False):
    P_func = make_P_func(protest_days)
    return solve_ivp(
        sicr_rhs, t_span, y0, args=(params, P_func),
        method='LSODA', t_eval=t_eval, rtol=1e-4, atol=1e-6,
        dense_output=dense_output
    )

def loss_dense(params, t_obs, N_obs, S0, protest_days):
    full_params = list(params)
    full_params.insert(5, 0.010)   # fixed gamma
    full_params.insert(7, 4.0)     # fixed n
    
    y0 = [S0, max(1, N_obs[0] * 0.1), max(1, N_obs[0] * 0.9), 0]
    try:
        sol = simulate_sicr_dense(y0, full_params, [0, t_obs[-1] + 10],
                                  protest_days=protest_days, t_eval=t_obs, dense_output=True)
    except Exception:
        return 1e9
        
    if sol.status != 0:
        return 1e9
        
    I_C = sol.y[1] + sol.y[2]
    I_C = np.maximum(1.0, I_C)
    
    # Base loss
    base_loss = np.mean((np.log(I_C) - np.log(N_obs))**2)
    
    # Dense check
    t_check = np.linspace(0, t_obs[-1] + 10, 200)
    sol_check = sol.sol(t_check)
    I_C_check = sol_check[1] + sol_check[2]
    
    max_observed = np.max(N_obs)
    max_fitted = np.max(I_C_check)
    
    penalty = 0.0
    if max_fitted > 1.2 * max_observed:
        penalty += 1000.0 * (max_fitted / (1.2 * max_observed) - 1.0)**2
        
    return base_loss + penalty

def fit_model_large_penalty(name, t_obs, N_obs, S0, protest_days):
    bounds = [
        (1e-10, 5.0 / S0),    # b1
        (1e-11, 0.5 / S0),    # b2
        (0.001, 0.5), 
        (0.01, 0.5), 
        (0.01, 0.5),
        (10000, S0 * 0.5), 
        (0.0, 15.0), 
        (0.0, 10.0), 
        (0.0, 10.0)
    ]
    
    result = differential_evolution(
        loss_dense, bounds, args=(t_obs, N_obs, S0, protest_days),
        seed=42, popsize=10, maxiter=50, tol=1e-4,
        polish=True, workers=-1, updating="deferred"
    )
    
    full_params = list(result.x)
    full_params.insert(5, 0.010)
    full_params.insert(7, 4.0)
    return full_params, result.fun

if __name__ == '__main__':
    print("Running large penalty optimization for France...")
    params, final_loss = fit_model_large_penalty("France", t_fr, N_fr, 30000000, t_fr)
    print("Optimized params:", params)
    print("Final loss:", final_loss)
    
    # Simulate to check values
    y0 = [30000000, max(1, N_fr[0]*0.1), max(1, N_fr[0]*0.9), 0]
    t_dense = np.arange(0, t_fr[-1] + 10, 1.0)
    sol = simulate_sicr_dense(y0, params, [0, t_fr[-1] + 10], protest_days=t_fr, dense_output=True)
    sol_dense = sol.sol(t_dense)
    I_C = sol_dense[1] + sol_dense[2]
    print(f"Max observed: {np.max(N_fr)}")
    print(f"Max fitted: {np.max(I_C)}")
    print("Fitted values at observation times:")
    for t, obs in zip(t_fr, N_fr):
        fit_val = sol.sol(t)[1] + sol.sol(t)[2]
        print(f"  Day {t:3d}: Obs={obs:9.1f}, Fit={fit_val:9.1f}")
