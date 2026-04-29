import matplotlib.pyplot as plt
import seaborn as sns
import json
import pandas as pd
from .fit import load_data

def generate_plots():
    (t_fr, N_fr, date_fr), (t_ir, N_ir, date_ir) = load_data()
    
    with open('results/scenarios.json', 'r') as f:
        scenarios = json.load(f)
        
    with open('results/france_sensitivity.json', 'r') as f:
        sens_fr = json.load(f)
    with open('results/iran_sensitivity.json', 'r') as f:
        sens_ir = json.load(f)
        
    # Fig 1: Baseline fits
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.plot(t_fr, np.maximum(1, N_fr), 'o', label='Observed (France)')
    ax1.plot(scenarios['S0']['france']['t'], np.maximum(1, scenarios['S0']['france']['N']), label='Fitted')
    ax1.set_yscale('log')
    ax1.set_title('France 2023 Pension Protests')
    ax1.legend()
    
    ax2.plot(t_ir, np.maximum(1, N_ir), 'o', label='Observed (Iran)')
    ax2.plot(scenarios['S0']['iran']['t'], np.maximum(1, scenarios['S0']['iran']['N']), label='Fitted')
    ax2.set_yscale('log')
    ax2.set_title('Iran 2022 Mahsa Amini Protests')
    ax2.legend()
    plt.tight_layout()
    plt.savefig('results/fig1_baseline.png')
    
    # Fig 2: Sensitivity analysis
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    x = range(len(sens_fr['names']))
    ax1.bar(x, sens_fr['total_ST'])
    ax1.set_xticks(x, sens_fr['names'])
    ax1.set_title('France: Sensitivity')
    
    ax2.bar(x, sens_ir['total_ST'])
    ax2.set_xticks(x, sens_ir['names'])
    ax2.set_title('Iran: Sensitivity')
    plt.tight_layout()
    plt.savefig('results/fig2_sensitivity.png')
    
    # Fig 3: Dose-response (H1)
    if 'S1' in scenarios and len(scenarios['S1']) > 0:
        plt.figure()
        s1_df = pd.DataFrame(scenarios['S1'])
        plt.plot(s1_df['mult'], s1_df['peak_N'], marker='o')
        plt.xlabel('Repression Multiplier (eps12)')
        plt.ylabel('Peak Protesters')
        plt.title('H1: Repression Dose-Response')
        plt.savefig('results/fig3_dose_response.png')
        
    # Fig 4: Backlash U-Curve (H3)
    if 'S3' in scenarios and len(scenarios['S3']) > 0:
        plt.figure()
        s3_df = pd.DataFrame(scenarios['S3'])
        plt.plot(s3_df['eps12'], s3_df['peak_N'], marker='o', color='red')
        plt.xlabel('Repression Intensity (eps12)')
        plt.ylabel('Peak Protesters')
        plt.title('H3: Backlash U-Curve')
        plt.savefig('results/fig4_backlash.png')
        
    # Fig 5: Regime Swap (H2)
    if 'S2_fr' in scenarios and 'S2_ir' in scenarios:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        ax1.plot(scenarios['S0']['france']['t'], np.maximum(1, scenarios['S0']['france']['N']), label='Baseline France')
        ax1.plot(scenarios['S2_fr']['t'], np.maximum(1, scenarios['S2_fr']['N']), '--', label='France under Iran Repression')
        ax1.set_yscale('log')
        ax1.legend()
        
        ax2.plot(scenarios['S0']['iran']['t'], np.maximum(1, scenarios['S0']['iran']['N']), label='Baseline Iran')
        ax2.plot(scenarios['S2_ir']['t'], np.maximum(1, scenarios['S2_ir']['N']), '--', label='Iran under France Repression')
        ax2.set_yscale('log')
        ax2.legend()
        plt.tight_layout()
        plt.savefig('results/fig5_regime_swap.png')

if __name__ == "__main__":
    generate_plots()
