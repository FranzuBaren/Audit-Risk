# Post 5: Adversarial Stress-Testing

**Monte Carlo Failure Cascade Simulation over Pharmaceutical Supply Chain Dependency Graphs**

Read the full post: [Adversarial Stress-Testing — Finding Where Your Organization Breaks Before It Does](https://kunskap.substack.com/p/adversarial-stress-testing)

## Files

| File | Description |
|------|-------------|
| `src/simulation.py` | Core Monte Carlo cascade engine — runs 10,000 scenarios, computes node criticality, fragility amplification, co-occurrence matrix, cascade severity distribution, and top audit findings |
| `src/generate_figures.py` | Publication-quality figure generator (editorial white style, 300 DPI) — produces all 5 figures from the post |
| `post.md` | Full post text in Markdown |
| `figures/` | Pre-generated figures at 300 DPI |

## Usage

```bash
cd post5

# Run the full simulation with printed analysis
python src/simulation.py

# Regenerate all 5 publication figures
python src/generate_figures.py
```

## Figures

**Figure 1** — Dependency graph. Node color and size encode systemic criticality.

**Figure 2** — Bimodal cascade severity distribution. The hallmark of a fragile system: either nothing fails, or everything cascades.

**Figure 3** — Fragility amplification. The gap between base failure probability (navy marker) and conditional terminal impact (bar) reveals how topology multiplies risk.

**Figure 4** — Cascade Fragility Index dashboard with intervention scenarios. CFI = 2.7 (Fragile). Backup QP + diversified LIMS → 2.3 (−15%).

**Figure 5** — Sensitivity analysis. Left: contagion weight perturbation ±30%. Right: tornado chart showing per-node sensitivity.

## Adapting the Model

Edit the `nodes` and `edges` dictionaries in `simulation.py` to model your own organization. The cascade engine is graph-agnostic — only the topology changes.
