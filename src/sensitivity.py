import numpy as np
import json
from SALib.sample import saltelli
from SALib.analyze import sobol
from .simulate import simulate_sicr
from .fit import load_data

def run_sensitivity(country="france"):
    (t_fr, N_fr, _), (t_ir, N_ir, _) = load_data()
    
    if country == "france":
        t_obs = t_fr
        N_obs = N_fr
        S0 = 4000000
        protest_days = t_fr
    else:
        t_obs = t_ir
        N_obs = N_ir
        S0 = 6000000
        protest_days = t_ir
        
    with open(f'results/{country}_params.json', 'r') as f:
        calibrated = np.array(json.load(f))
        
    problem = {
        'num_vars': 10,
        'names': ['b1', 'b2', 'chi', 'd11', 'd21', 'gamma', 'C0', 'n', 'eps12', 'eps22'],
        'bounds': []
    }
    
    for val in calibrated:
        if val == 0:
            problem['bounds'].append([0.0, 1e-4])
        else:
            problem['bounds'].append([val*0.5, val*1.5])
            
    # Proper analysis requires N >= 512. Use 1024.
    param_values = saltelli.sample(problem, 1024) 
    
    Y_peak = np.zeros([param_values.shape[0]])
    Y_total = np.zeros([param_values.shape[0]])
    Y_half = np.zeros([param_values.shape[0]])
    
    y0 = [S0, max(1, N_obs[0]*0.1), max(1, N_obs[0]*0.9), 0]
    
    for i, X in enumerate(param_values):
        try:
            sol = simulate_sicr(y0, X, [0, t_obs[-1]+10], protest_days=protest_days)
            if sol.success:
                N_t = sol.y[1] + sol.y[2]
                Y_peak[i] = np.max(N_t)
                Y_total[i] = np.trapz(N_t, sol.t)
                
                peak_idx = np.argmax(N_t)
                half_val = Y_peak[i] / 2.0
                post_peak_N = N_t[peak_idx:]
                post_peak_t = sol.t[peak_idx:]
                
                idx = np.where(post_peak_N < half_val)[0]
                if len(idx) > 0:
                    Y_half[i] = post_peak_t[idx[0]] - sol.t[peak_idx]
                else:
                    Y_half[i] = sol.t[-1] - sol.t[peak_idx]
            else:
                Y_peak[i], Y_total[i], Y_half[i] = 0, 0, 0
        except Exception:
            Y_peak[i], Y_total[i], Y_half[i] = 0, 0, 0
            
    Si_peak = sobol.analyze(problem, Y_peak)
    Si_total = sobol.analyze(problem, Y_total)
    Si_half = sobol.analyze(problem, Y_half)
    
    import os
    os.makedirs('results', exist_ok=True)
    with open(f'results/{country}_sensitivity.json', 'w') as f:
        json.dump({
            'peak_ST': Si_peak['ST'].tolist(),
            'total_ST': Si_total['ST'].tolist(),
            'half_ST': Si_half['ST'].tolist(),
            'names': problem['names']
        }, f)

if __name__ == "__main__":
    print("Running sensitivity for France...")
    run_sensitivity("france")
    print("Running sensitivity for Iran...")
    run_sensitivity("iran")
