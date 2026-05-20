"""
SICR compartmental protest model — improved with recruitment forcing.
"""
import numpy as np
from scipy.integrate import solve_ivp


def make_P_func(protest_days):
    """Vectorised protest-day indicator using precomputed tanh terms."""
    pd_arr = np.asarray(protest_days, dtype=np.float64)
    lo = 10.0 * (-(pd_arr - 0.5))
    hi = 10.0 * (-(pd_arr + 0.5))
    def P(t):
        val = 0.5 * np.sum(np.tanh(10.0 * t + lo) - np.tanh(10.0 * t + hi))
        return min(1.0, val)
    return P


def sicr_rhs(t, y, params, P_func):
    # Enforce non-negativity to prevent numerical instability and overflow
    S = max(0.0, y[0])
    I = max(0.0, y[1])
    C = max(0.0, y[2])
    R = max(0.0, y[3])
    
    if len(params) == 10:
        b1, b2, chi, d11, d21, gamma, C0, n, eps12, eps22 = params
        eps0 = 0.0
    else:
        b1, b2, chi, d11, d21, gamma, C0, n, eps0, eps12, eps22 = params
    Pt = P_func(t)
    
    # Recruitment enhancement on protest days
    b_eff = 1.0 + eps0 * Pt
    inflow = S * (b1 * b_eff * I + b2 * b_eff * C)
    
    # Repression/Exit enhancement on protest days
    d11_eff = d11 + eps12 * Pt
    omega = (d21 + eps22 * Pt) / (1.0 + ((I + C) / C0)**n)
    
    dS = -inflow + gamma * R
    dI = inflow - chi * I - d11_eff * I
    dC = chi * I - C * omega
    dR = d11_eff * I + C * omega - gamma * R
    return [dS, dI, dC, dR]


def simulate_sicr(y0, params, t_span, protest_days, t_eval=None, dense_output=False):
    P_func = make_P_func(protest_days)
    return solve_ivp(
        sicr_rhs, t_span, y0, args=(params, P_func),
        method='LSODA', t_eval=t_eval, rtol=1e-4, atol=1e-6,
        dense_output=dense_output
    )


def loss(params, t_obs, N_obs, S0, protest_days):
    """Loss function for differential_evolution."""
    full_params = list(params)
    # Mapping for 11 parameters:
    # bounds provides 9: b1, b2, chi, d11, d21, C0, eps0, eps12, eps22
    # Insert fixed parameters:
    if len(params) == 8:
        full_params.insert(5, 0.010)   # fixed gamma
        full_params.insert(7, 4.0)     # fixed n
    else:
        full_params.insert(5, 0.010)   # fixed gamma
        full_params.insert(7, 4.0)     # fixed n
    
    y0 = [S0, max(1, N_obs[0] * 0.1), max(1, N_obs[0] * 0.9), 0]
    try:
        sol = simulate_sicr(y0, full_params, [0, t_obs[-1] + 10],
                            protest_days=protest_days, t_eval=t_obs, dense_output=True)
    except Exception:
        return 1e9
    if not sol.success or len(sol.t) != len(t_obs):
        return 1e9
    N_sim = np.maximum(1, sol.y[1] + sol.y[2])
    N_obs_safe = np.maximum(1, N_obs)
    
    # Base loss: Mean Squared Error of logs at observed days
    loss_val = np.mean((np.log(N_sim) - np.log(N_obs_safe)) ** 2)
    
    # Penalize unrealistic spikes using the continuous solution
    t_check = np.linspace(0, t_obs[-1] + 10, 200)
    sol_check = sol.sol(t_check)
    I_C_check = sol_check[1] + sol_check[2]
    
    max_observed = np.max(N_obs)
    max_fitted = np.max(I_C_check)
    
    if max_fitted > 1.2 * max_observed:
        loss_val += 1000.0 * (max_fitted / (1.2 * max_observed) - 1.0)**2
        
    return loss_val
