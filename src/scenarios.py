import numpy as np
import json
import os
import pandas as pd
from .simulate import simulate_sicr
from .fit import load_data

def run_scenarios():
    (t_fr, N_fr, _), (t_ir, N_ir, _) = load_data()
    
    with open('results/france_params.json', 'r') as f:
        params_fr = json.load(f)
    with open('results/iran_params.json', 'r') as f:
        params_ir = json.load(f)
        
    y0_fr = [4000000, max(1, N_fr[0]*0.1), max(1, N_fr[0]*0.9), 0]
    y0_ir = [6000000, max(1, N_ir[0]*0.1), max(1, N_ir[0]*0.9), 0]
    
    results = {}
    
    # S0: Baseline
    sol_fr = simulate_sicr(y0_fr, params_fr, [0, t_fr[-1]], protest_days=t_fr)
    sol_ir = simulate_sicr(y0_ir, params_ir, [0, t_ir[-1]], protest_days=t_ir)
    results['S0'] = {
        'france': {'t': sol_fr.t.tolist(), 'N': (sol_fr.y[1]+sol_fr.y[2]).tolist()},
        'iran': {'t': sol_ir.t.tolist(), 'N': (sol_ir.y[1]+sol_ir.y[2]).tolist()}
    }
    
    # S1: Repression sweep (varying eps12 for France)
    s1_results = []
    base_eps12_fr = params_fr[8]
    for mult in np.linspace(0, 5, 10):
        p = params_fr.copy()
        p[8] = base_eps12_fr * mult
        try:
            sol = simulate_sicr(y0_fr, p, [0, t_fr[-1]], protest_days=t_fr)
            if sol.success:
                s1_results.append({'mult': mult, 'peak_N': np.max(sol.y[1]+sol.y[2])})
        except: pass
    results['S1'] = s1_results
    
    # S2: Regime swap (Iran parameters to France, France to Iran)
    p_fr_swap = params_fr.copy()
    p_fr_swap[5] = params_ir[5] # gamma
    p_fr_swap[8] = params_ir[8] # eps12
    p_fr_swap[9] = params_ir[9] # eps22
    try:
        sol_fr_swap = simulate_sicr(y0_fr, p_fr_swap, [0, t_fr[-1]], protest_days=t_fr)
        results['S2_fr'] = {'t': sol_fr_swap.t.tolist(), 'N': (sol_fr_swap.y[1]+sol_fr_swap.y[2]).tolist()}
    except: pass
    
    p_ir_swap = params_ir.copy()
    p_ir_swap[5] = params_fr[5]
    p_ir_swap[8] = params_fr[8]
    p_ir_swap[9] = params_fr[9]
    try:
        sol_ir_swap = simulate_sicr(y0_ir, p_ir_swap, [0, t_ir[-1]], protest_days=t_ir)
        results['S2_ir'] = {'t': sol_ir_swap.t.tolist(), 'N': (sol_ir_swap.y[1]+sol_ir_swap.y[2]).tolist()}
    except: pass
    
    # S3: Backlash (b1 = b10 + kappa * eps12)
    s3_results = []
    b10 = params_fr[0]
    kappa = max(b10 * 10, 1e-4) # arbitrary for U-shape illustration
    for eps12 in np.linspace(0, 1.0, 20):
        p = params_fr.copy()
        p[8] = eps12
        p[0] = b10 + kappa * eps12
        try:
            sol = simulate_sicr(y0_fr, p, [0, t_fr[-1]], protest_days=t_fr)
            if sol.success:
                s3_results.append({'eps12': eps12, 'peak_N': np.max(sol.y[1]+sol.y[2])})
        except: pass
    results['S3'] = s3_results
    
    # S4: Re-entry shock
    half_t = t_fr[-1] / 2.0
    p_stage1 = params_fr.copy()
    p_stage1[5] = 0.0
    try:
        sol_stage1 = simulate_sicr(y0_fr, p_stage1, [0, half_t], protest_days=[d for d in t_fr if d <= half_t])
        y0_stage2 = sol_stage1.y[:, -1]
        sol_stage2 = simulate_sicr(y0_stage2, params_fr, [half_t, t_fr[-1]], protest_days=[d for d in t_fr if d > half_t])
        
        t_s4 = np.concatenate([sol_stage1.t, sol_stage2.t[1:]])
        N_s4 = np.concatenate([sol_stage1.y[1]+sol_stage1.y[2], sol_stage2.y[1, 1:]+sol_stage2.y[2, 1:]])
        results['S4'] = {'t': t_s4.tolist(), 'N': N_s4.tolist()}
    except: pass
    
    os.makedirs('results', exist_ok=True)
    with open('results/scenarios.json', 'w') as f:
        json.dump(results, f)

if __name__ == "__main__":
    run_scenarios()
