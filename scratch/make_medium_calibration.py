import json

notebook_path = 'analysis.ipynb'
print("Loading notebook...")
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

modified = False
for cell in nb.get('cells', []):
    if cell.get('cell_type') == 'code':
        source = cell.get('source', [])
        for i, line in enumerate(source):
            if 'popsize=5, maxiter=5, tol=1e-3' in line:
                print(f"Found target line: {line.strip()}")
                new_line = line.replace('popsize=5, maxiter=5, tol=1e-3', 'popsize=10, maxiter=40, tol=1e-4')
                source[i] = new_line
                print(f"Replaced with: {new_line.strip()}")
                modified = True

if modified:
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    print("Notebook modified to medium settings.")
else:
    print("No matching calibration settings found in notebook cells.")
