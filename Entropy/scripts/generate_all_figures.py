#!/usr/bin/env python3
"""
Generate all 6 figures for Post 4: Entropy Monitoring.

Usage:
    python scripts/generate_all_figures.py

Outputs to figures/ directory.
"""
import subprocess
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
FIGURES_DIR = PROJECT_ROOT / "figures"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


def run_notebook():
    """Execute the simulation notebook and extract figures."""
    notebook = NOTEBOOKS_DIR / "entropy_simulation.ipynb"
    if not notebook.exists():
        print(f"ERROR: Notebook not found at {notebook}")
        sys.exit(1)

    print("=" * 60)
    print("Running entropy simulation notebook...")
    print("=" * 60)

    # Execute notebook using jupyter nbconvert
    result = subprocess.run(
        [
            sys.executable, "-m", "jupyter", "nbconvert",
            "--to", "notebook",
            "--execute",
            "--ExecutePreprocessor.timeout=300",
            "--output", "entropy_simulation_executed.ipynb",
            str(notebook),
        ],
        capture_output=True,
        text=True,
        cwd=str(FIGURES_DIR),  # Execute with CWD = figures/ so .png files land there
    )

    if result.returncode != 0:
        print(f"Notebook execution failed:\n{result.stderr}")
        # Try alternative: run as script
        print("\nFalling back to script extraction...")
        run_notebook_as_script()
    else:
        print("Notebook executed successfully.")
        # Clean up the executed notebook copy
        executed = FIGURES_DIR / "entropy_simulation_executed.ipynb"
        if executed.exists():
            executed.unlink()


def run_notebook_as_script():
    """Extract Python code from notebook and run it."""
    import json

    notebook = NOTEBOOKS_DIR / "entropy_simulation.ipynb"
    with open(notebook) as f:
        nb = json.load(f)

    code_cells = []
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            source = "".join(cell["source"])
            code_cells.append(source)

    script = "\n\n".join(code_cells)

    # Replace plt.show() with plt.close() for non-interactive execution
    script = script.replace("plt.show()", "plt.close('all')")

    # Add matplotlib backend setting at the top
    script = "import matplotlib\nmatplotlib.use('Agg')\n\n" + script

    script_path = FIGURES_DIR / "_temp_simulation.py"
    with open(script_path, "w") as f:
        f.write(script)

    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        cwd=str(FIGURES_DIR),
    )

    print(result.stdout)
    if result.returncode != 0:
        print(f"Script execution failed:\n{result.stderr}")
    else:
        print("Simulation figures generated successfully.")

    script_path.unlink(missing_ok=True)


def run_pof_script():
    """Generate the PoF integration figure."""
    pof_script = SCRIPTS_DIR / "generate_pof_figure.py"
    if not pof_script.exists():
        print(f"ERROR: PoF script not found at {pof_script}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Running PoF integration script...")
    print("=" * 60)

    # Read and modify script to use Agg backend and save to figures/
    with open(pof_script) as f:
        code = f.read()

    code = "import matplotlib\nmatplotlib.use('Agg')\n\n" + code
    code = code.replace("plt.show()", "plt.close('all')")

    temp = FIGURES_DIR / "_temp_pof.py"
    with open(temp, "w") as f:
        f.write(code)

    result = subprocess.run(
        [sys.executable, str(temp)],
        capture_output=True,
        text=True,
        cwd=str(FIGURES_DIR),
    )

    print(result.stdout)
    if result.returncode != 0:
        print(f"PoF script failed:\n{result.stderr}")
    else:
        print("PoF integration figure generated successfully.")

    temp.unlink(missing_ok=True)


def verify_outputs():
    """Check that all expected figures exist."""
    expected = [
        "entropy_budget.png",
        "entropy_three_signatures.png",
        "entropy_main.png",
        "entropy_decomposition.png",
        "entropy_sensitivity.png",
        "entropy_pof_integration.png",
    ]

    print("\n" + "=" * 60)
    print("Verifying outputs...")
    print("=" * 60)

    all_ok = True
    for fname in expected:
        path = FIGURES_DIR / fname
        if path.exists():
            size_kb = path.stat().st_size / 1024
            print(f"  ✓ {fname} ({size_kb:.0f} KB)")
        else:
            print(f"  ✗ {fname} — MISSING")
            all_ok = False

    if all_ok:
        print(f"\nAll {len(expected)} figures generated in {FIGURES_DIR}/")
    else:
        print("\nSome figures are missing. Check the error messages above.")

    return all_ok


if __name__ == "__main__":
    FIGURES_DIR.mkdir(exist_ok=True)

    run_notebook()
    run_pof_script()
    success = verify_outputs()

    sys.exit(0 if success else 1)
