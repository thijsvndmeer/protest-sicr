"""
Fix analysis.ipynb based on TA feedback:
1. Drop zero-diff rows from Iran data instead of filling with 0
2. Update markdown to explain consistent missing data handling
3. Fix gamma value in markdown (0.01 -> 0.05 to match code)
4. Clear all cell outputs/execution counts (data changed, need re-run)
"""
import json
import os
import shutil

NOTEBOOK_PATH = 'analysis.ipynb'
PARAMS_CACHE = 'results/fitted_params.json'
PARAMS_BACKUP = 'results/fitted_params_pre_fix.json'

# --- Load notebook ---
with open(NOTEBOOK_PATH, 'r') as f:
    nb = json.load(f)

# --- Fix Cell 1 (id=section-setup): Update data loading description ---
for cell in nb['cells']:
    if cell.get('id') == 'section-setup':
        cell['source'] = [
            "## 1. Setup & Data Loading\n",
            "\n",
            "We load two datasets representing contrasting protest contexts:\n",
            "\n",
            "- **France 2023** — Weekly protest turnout estimates (midpoint of CGT union and Ministry of Interior counts)\n",
            "  during the pension reform strikes. The movement saw repeated Saturday mobilisations over several months\n",
            "  ([Rouxel & Yon, 2023](https://doi.org/10.15173/glj.v14i2.5519)).\n",
            "  This dataset has **no missing values** — every mobilisation date has both CGT and Ministry counts.\n",
            "\n",
            "- **Iran 2022** — Daily cumulative arrest figures from the Mahsa Amini protests. Since direct crowd-size\n",
            "  data is unavailable, we proxy active protesters via the daily *change* in arrests, scaled by a constant\n",
            "  factor ([Monshipouri & Zamiri, 2023](https://doi.org/10.1111/mepo.12722)).\n",
            "  **Days where the cumulative arrest count did not change (zero or negative diff) are dropped**,\n",
            "  since a zero diff most likely indicates that the tracker did not update that day rather than that\n",
            "  zero arrests occurred. This removes 56 of 158 data points. Both datasets are thus treated\n",
            "  consistently: we only fit the model to time points with actual observed protest activity.\n",
        ]
        print("Fixed cell: section-setup")
        break

# --- Fix Cell 3 (id=f3fadf66): Drop zero-diff Iran rows ---
for cell in nb['cells']:
    if cell.get('id') == 'f3fadf66':
        cell['source'] = [
            "\n",
            "# ── France ──\n",
            "df_fr = pd.read_csv('data/france_2023_weekly.csv')\n",
            "df_fr['date'] = pd.to_datetime(df_fr['date'])\n",
            "t_fr = (df_fr['date'] - df_fr['date'].min()).dt.days.values\n",
            "N_fr = df_fr['mid'].values\n",
            "\n",
            "# ── Iran ──\n",
            "df_ir = pd.read_csv('data/iran_2022_weekly.csv')\n",
            "df_ir['Date'] = pd.to_datetime(df_ir['Date'])\n",
            "t_ir_all = (df_ir['Date'] - df_ir['Date'].min()).dt.days.values\n",
            "daily_arrests_raw = np.diff(df_ir['Number of Individuals Arrested'].values, prepend=0)\n",
            "\n",
            "# Drop days where the daily arrest change is <= 0.\n",
            "# A zero diff means no new arrests were reported that day, indicating\n",
            "# either no protest activity or (more likely) missing/unreported data.\n",
            "# This ensures consistent treatment with France (which has no missing data).\n",
            "valid_mask = daily_arrests_raw > 0\n",
            "t_ir = t_ir_all[valid_mask]\n",
            "N_ir = daily_arrests_raw[valid_mask] * 50.0  # Proxy scaling\n",
            "\n",
            "print(f'Iran: kept {valid_mask.sum()}/{len(valid_mask)} days with positive arrest changes')\n",
            "print(f'France: {len(N_fr)} data points (no missing data)')\n",
        ]
        cell['outputs'] = []
        cell['execution_count'] = None
        print("Fixed cell: f3fadf66 (data loading)")
        break

# --- Fix Cell 6 (id=section-fitting): gamma 0.01 -> 0.05 ---
for cell in nb['cells']:
    if cell.get('id') == 'section-fitting':
        new_source = []
        for line in cell['source']:
            new_source.append(line.replace('| 0.01 |', '| 0.05 |'))
        cell['source'] = new_source
        print("Fixed cell: section-fitting (gamma 0.01 -> 0.05)")
        break

# --- Clear all code cell outputs (data changed, everything needs re-run) ---
cleared = 0
for cell in nb['cells']:
    if cell.get('cell_type') == 'code':
        cell['outputs'] = []
        cell['execution_count'] = None
        cleared += 1
print(f"Cleared outputs from {cleared} code cells")

# --- Save notebook ---
with open(NOTEBOOK_PATH, 'w') as f:
    json.dump(nb, f, indent=1)
print(f"Saved {NOTEBOOK_PATH}")

# --- Backup and remove cached parameters (now invalid) ---
if os.path.exists(PARAMS_CACHE):
    shutil.copy2(PARAMS_CACHE, PARAMS_BACKUP)
    os.remove(PARAMS_CACHE)
    print(f"Backed up {PARAMS_CACHE} -> {PARAMS_BACKUP} and removed cache")
    print("NOTE: Re-run notebook to re-fit with cleaned data!")
else:
    print("No cached params to remove")
