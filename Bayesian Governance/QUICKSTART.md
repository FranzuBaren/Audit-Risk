# Quick Start Guide

## Get Running in 2 Minutes

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run the Simulation

```bash
python bayesian_governance_simulation.py
```

**Output**: Two PNG visualizations will be generated in the current directory:
- `bayesian_vs_checklist.png` - Main comparison
- `prior_sensitivity.png` - Prior convergence analysis

### Step 3: View the Results

The console will display:

```
======================================================================
SIMULATION SUMMARY: Bayesian vs Checklist Audit Performance
======================================================================

Scenario: 365 days of EBR monitoring
          Stress period: Days 150-250
          True baseline failure rate: 2%

DETECTION SPEED:
----------------
Bayesian (continuous):  Detected issue on Day 219
                       → Alert lag: 69 days after stress began

Checklist (quarterly):  Detected issue on Day 270
                       → Alert lag: 120 days after stress began

Detection advantage:    Bayesian detected 51 days earlier
...
```

## Interactive Exploration

For hands-on experimentation:

```bash
jupyter notebook interactive_exploration.ipynb
```

**Recommended starting points**:
1. **Part 1**: See how a single Bayesian update works
2. **Part 2**: Watch beliefs converge over time
3. **Part 4**: Real-world calibration exercise

## Modify Parameters

Edit these values in `bayesian_governance_simulation.py`:

```python
# Line ~450
results = run_simulation(
    days=365,              # Total simulation days
    daily_batches=50,      # Batches processed per day
    stress_start=150,      # When stress begins
    stress_end=250         # When stress ends
)
```

## Common Questions

**Q: Why is my Bayesian alert day different from the README?**  
A: The simulation uses random number generation. Run with `np.random.seed(42)` for reproducibility.

**Q: Can I test different stress scenarios?**  
A: Yes! Open the notebook and use Part 3: Scenario Explorer.

**Q: What if I want a different baseline failure rate?**  
A: Modify line ~22 in `bayesian_governance_simulation.py`:
```python
class ProcessState:
    def __init__(self, base_failure_rate=0.02):  # Change this value
```

## Understanding the Output

### Main Visualization (bayesian_vs_checklist.png)

**Top panel**: Continuous Bayesian monitoring
- **Black line**: True underlying failure rate (what's actually happening)
- **Blue line**: Bayesian PoF estimate (what the system believes)
- **Blue shaded area**: 95% credible interval (uncertainty bounds)
- **Orange dotted line**: When Bayesian system triggered alert

**Bottom panel**: Traditional quarterly audits
- **Green squares**: Audits that passed (Green status)
- **Red squares**: Audits that failed (Red/Amber status)
- **Gray dashed line**: Interpolation between audits (what checklist assumes)

### Key Insight

The **gap** between the orange dotted line (Bayesian alert) and the first red square (checklist alert) represents **actionable lead time** for intervention.

## Next Steps

1. **Read the full README.md** for mathematical details
2. **Run the notebook** for interactive learning
3. **Modify parameters** to match your use case
4. **Adapt the code** for your specific governance scenario

## Troubleshooting

**Import errors**: Ensure all packages in `requirements.txt` are installed

**Matplotlib backend issues**: Add to top of script:
```python
import matplotlib
matplotlib.use('Agg')  # For non-interactive backend
```

**NumPy version conflicts**: Use `pip install --upgrade numpy scipy`

---

**Ready to dig deeper?** → See README.md for full documentation
