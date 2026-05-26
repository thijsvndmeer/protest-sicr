# Fixes Applied to `analysis.ipynb`

Based on TA feedback received 2026-05-26.

---

## Fix 1: Consistent Missing Data Handling (TA Point 1)

### Problem

The Iran and France datasets were handled asymmetrically with respect to missing data:

- **Iran**: The protest proxy `N_ir` was computed as `np.maximum(0, np.diff(cumulative_arrests)) * 50`. Days where the cumulative arrest count didn't change produced a diff of 0, and the single day with a negative diff (12/19/2022, −90) was clipped to 0. These zeros became 1 via `np.maximum(1, N_obs)` in the loss function, showing up as `log(1) = 0` on the log-scale plots. This implicitly treated missing/unreported data as "zero protest activity".

- **France**: The dataset had **no missing values** — every row has complete CGT and Ministry counts. No special handling was needed or applied.

The TA flagged this inconsistency: both datasets should be treated the same way.

### Fix Applied

**Dropped rows** where the Iran daily arrest change is ≤ 0 instead of filling with 0.

**Rationale**: A zero diff in the cumulative arrest tracker most likely means the tracker wasn't updated that day, not that zero arrests occurred. This is especially clear in the late stages of the dataset (Jan–Feb 2023), where the cumulative count is flat for days or weeks at a time — consistent with the protest tracker winding down reporting, not with zero protest activity.

**Impact**: 56 of 158 Iran data points were dropped (55 zero-diff + 1 negative-diff). The remaining 102 data points all have positive arrest changes and represent genuine observations.

**Code change** in data loading cell (`id=f3fadf66`):

```python
# Before (implicit fill with 0):
daily_arrests = np.maximum(0, np.diff(..., prepend=0))
N_ir = daily_arrests * 50.0

# After (drop missing):
daily_arrests_raw = np.diff(..., prepend=0)
valid_mask = daily_arrests_raw > 0
t_ir = t_ir_all[valid_mask]
N_ir = daily_arrests_raw[valid_mask] * 50.0
```

**Markdown update** in Section 1 (`id=section-setup`): Added explicit description of the dropping strategy and why both datasets are now treated consistently.

---

## Fix 2: γ (gamma) Value Typo in Markdown

### Problem

The parameter calibration table (Section 3, `id=section-fitting`) stated γ = 0.01, but the actual code in both `sicr.py` and the notebook `fit_model` function uses γ = 0.05.

### Fix Applied

Changed the markdown table from `0.01` to `0.05` to match the code.

---

## Fix 3: Cache Invalidation

### Problem

The fitted parameters were cached in `results/fitted_params.json`. Since the Iran data changed (56 rows dropped), the old fitted parameters are invalid.

### Fix Applied

- Backed up old cache to `results/fitted_params_pre_fix.json`
- Removed `results/fitted_params.json`
- Cleared all code cell outputs and execution counts

**Action required**: Re-run the entire notebook to re-fit both models with the cleaned data. The fitting step uses differential evolution with `workers=-1` and may take several minutes.

---

## Summary of Changed Files

| File | Change |
|------|--------|
| `analysis.ipynb` cell `section-setup` | Updated markdown to describe dropping strategy |
| `analysis.ipynb` cell `f3fadf66` | Drop zero/negative-diff Iran rows instead of filling with 0 |
| `analysis.ipynb` cell `section-fitting` | Fixed γ = 0.01 → 0.05 |
| `analysis.ipynb` all code cells | Cleared outputs (need re-run) |
| `results/fitted_params.json` | Removed (backed up to `fitted_params_pre_fix.json`) |
