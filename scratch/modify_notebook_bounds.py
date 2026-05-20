import json

notebook_path = 'analysis.ipynb'
print("Loading notebook...")
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

modified = False
for cell in nb.get('cells', []):
    if cell.get('cell_type') == 'code':
        source = cell.get('source', [])
        
        # Check if bounds definition is in cell
        has_bounds_cell = False
        for line in source:
            if 'bounds = [' in line or '(1e-10,' in line:
                has_bounds_cell = True
                break
                
        if has_bounds_cell:
            new_source = []
            skip_lines = 0
            for i, line in enumerate(source):
                if skip_lines > 0:
                    skip_lines -= 1
                    continue
                
                # Check for bounds block
                if 'bounds = [' in line:
                    print("Found bounds declaration start.")
                    new_source.append(line)
                    # We expect the next 2 lines to define bounds array
                    # Replace them with scaled bounds
                    new_source.append("        (1e-10, 5.0 / S0),    # b1 (scaled by S0)\n")
                    new_source.append("        (1e-11, 0.5 / S0),    # b2 (scaled by S0)\n")
                    new_source.append("        (0.001, 0.5), (0.01, 0.5), (0.01, 0.5),\n")
                    new_source.append("        (10000, S0*0.5), (0.0, 15.0), (0.0, 10.0), (0.0, 10.0)\n")
                    new_source.append("    ]\n")
                    
                    # Skip the original lines (usually 3 lines: the 2 bounds lines and the closing bracket)
                    # Let's count until we find the closing bracket
                    j = i + 1
                    while j < len(source) and ']' not in source[j]:
                        j += 1
                    skip_lines = j - i
                    modified = True
                    print(f"Skipping {skip_lines} lines of original bounds.")
                elif 'popsize=10, maxiter=40, tol=1e-4' in line:
                    print(f"Found target popsize line: {line.strip()}")
                    new_line = line.replace('popsize=10, maxiter=40, tol=1e-4', 'popsize=12, maxiter=100, tol=1e-4')
                    new_source.append(new_line)
                    modified = True
                elif 'polish=False, workers=-1' in line:
                    print(f"Found target polish line: {line.strip()}")
                    new_line = line.replace('polish=False, workers=-1', 'polish=True, workers=-1')
                    new_source.append(new_line)
                    modified = True
                else:
                    new_source.append(line)
            cell['source'] = new_source

if modified:
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    print("Notebook modified with scaled bounds and optimal calibration parameters.")
else:
    print("No matching bounds or settings found to modify.")
