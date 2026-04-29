from src.fit import fit_model
from src.sensitivity import run_sensitivity
from src.scenarios import run_scenarios
from src.plots import generate_plots

def main():
    print("=== 1. Fitting Model ===")
    print("Fitting France...")
    fit_model("france")
    print("Fitting Iran...")
    fit_model("iran")

    print("\n=== 2. Sensitivity Analysis ===")
    run_sensitivity("france")
    run_sensitivity("iran")

    print("\n=== 3. Running Scenarios ===")
    run_scenarios()

    print("\n=== 4. Generating Plots ===")
    generate_plots()

    print("Pipeline completed. Check results/ directory.")

if __name__ == '__main__':
    main()
