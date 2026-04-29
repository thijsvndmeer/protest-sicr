import numpy as np
from scipy.integrate import solve_ivp
from .model import sicr_rhs

def make_P_func(protest_days):
    """
    Creates a smoothed indicator function P(t) that is ~1 around protest days and ~0 elsewhere.
    Using tanh for smoothness to prevent LSODA from stalling.
    """
    def P(t):
        val = 0.0
        for pd in protest_days:
            val += 0.5 * (np.tanh(10 * (t - (pd - 0.5))) - np.tanh(10 * (t - (pd + 0.5))))
        return min(1.0, val)
    return P

def simulate_sicr(y0, params, t_span, protest_days=None, t_eval=None):
    if protest_days is None:
        def P(t): return 0.0
    else:
        P = make_P_func(protest_days)
        
    sol = solve_ivp(
        fun=lambda t, y: sicr_rhs(t, y, params, P),
        t_span=t_span,
        y0=y0,
        t_eval=t_eval,
        method='LSODA',
        rtol=1e-7,
        atol=1e-7
    )
    
    # Conservation check
    N0 = sum(y0)
    for i in range(len(sol.t)):
        Nt = np.sum(sol.y[:, i])
        if not np.isclose(N0, Nt, rtol=1e-5):
            raise ValueError(f"Population not conserved at t={sol.t[i]}. N0={N0}, Nt={Nt}")
            
    return sol
