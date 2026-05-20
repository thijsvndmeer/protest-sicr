"""
SICR compartmental protest model — importable module for multiprocessing compatibility.
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
    S, I, C, R = y[0], y[1], y[2], y[3]
    b1, b2, chi, d11, d21, gamma, C0, n, eps12, eps22 = params
    Pt = P_func(t)
    omega = (d21 + eps22 * Pt) / (1.0 + ((I + C) / C0)**n)
    inflow = S * (b1 * I + b2 * C)
    d11_eff = d11 + eps12 * Pt
    dS = -inflow + gamma * R
    dI = inflow - chi * I - d11_eff * I
    dC = chi * I - C * omega
    dR = d11_eff * I + C * omega - gamma * R
    return [dS, dI, dC, dR]


def simulate_sicr(y0, params, t_span, protest_days, t_eval=None, rtol=1e-6, atol=1e-8):
    P_func = make_P_func(protest_days)
    return solve_ivp(
        sicr_rhs, t_span, y0, args=(params, P_func),
        method='LSODA', t_eval=t_eval, rtol=rtol, atol=atol
    )


def loss(params, t_obs, N_obs, S0, protest_days):
    """Loss function for differential_evolution — must be top-level for pickling.

    Expects 9 params: log(b1), log(b2), log(chi), log(d11), log(d21),
    log(C0), eps12, eps22, n.  First 6 are log-space; last 3 are linear.
    """
    log_b1, log_b2, log_chi, log_d11, log_d21, log_C0, eps12, eps22, n = params
    full_params = [
        np.exp(log_b1), np.exp(log_b2), np.exp(log_chi),
        np.exp(log_d11), np.exp(log_d21),
        0.010,            # fixed gamma
        np.exp(log_C0), n, eps12, eps22,
    ]
    y0 = [S0, max(1, N_obs[0] * 0.1), max(1, N_obs[0] * 0.9), 0]
    try:
        sol = simulate_sicr(y0, full_params, [0, t_obs[-1] + 10],
                            protest_days=protest_days, t_eval=t_obs,
                            rtol=1e-4, atol=1e-6)
    except Exception:
        return 1e9
    if not sol.success or len(sol.t) != len(t_obs):
        return 1e9
    N_sim = np.maximum(1, sol.y[1] + sol.y[2])
    N_obs_safe = np.maximum(1, N_obs)
    return np.mean((np.log(N_sim) - np.log(N_obs_safe)) ** 2)
