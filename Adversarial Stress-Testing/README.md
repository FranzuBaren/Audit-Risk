# 🎯 Adversarial Stress-Testing: The Corporate "Turing Test"

**Monte Carlo Failure-Cascade Simulation with Strategic Adversary**

Post 5 of 6 — *Audit 2.0 in the Age of Non-Deterministic Systems*

[![Substack](https://img.shields.io/badge/Substack-kunskap-orange?logo=substack)](https://kunskap.substack.com)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## What This Does

Models an enterprise as a **directed dependency graph** (19 nodes, 33 edges) and stress-tests it two ways:

1. **Scenario Monte Carlo** — 10,000 simulations × 6 compound crisis scenarios (60,000 total)
2. **Strategic Adversary** — A synthetic agent that *optimally* selects which nodes to attack to maximize cascade damage

### Key Findings (from the synthetic pharma enterprise)

| Finding | Detail |
|---------|--------|
| **Batch Release** | Present in **100%** of major failures — a topological singularity |
| **Adversary k=1** | API Gateway alone → 44% expected damage |
| **Adversary k=5** | 5 nodes → 79% of organization down |
| **Hidden correlation** | API Supplier + Batch Release co-fail in 49% of Black Swan sims |
| **Detection gap** | Monte Carlo finds *convergence points*; adversary finds *leverage points* — different vulnerabilities |

## Quick Start

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/audit2-adversarial.git
cd audit2-adversarial

# Install dependencies
pip install -r requirements.txt

# Run the full simulation (~3 min)
python src/run_simulation.py

# Or open the notebook
jupyter notebook notebooks/adversarial_stress_test.ipynb
```

## Project Structure

```
audit2-adversarial/
├── README.md
├── LICENSE
├── requirements.txt
├── setup.py
│
├── src/
│   ├── __init__.py
│   ├── graph.py            # Enterprise dependency graph definition
│   ├── scenarios.py        # Stress scenario definitions
│   ├── cascade.py          # CascadeEngine — Monte Carlo simulation
│   ├── adversary.py        # StrategicAdversary — synthetic red team
│   ├── metrics.py          # Bottleneck, co-failure, threat score computation
│   ├── plotting.py         # All 9 figures (premium design system)
│   └── run_simulation.py   # End-to-end CLI runner
│
├── notebooks/
│   └── adversarial_stress_test.ipynb   # Interactive notebook with all figures
│
├── figures/                # Generated PNG outputs (300 DPI)
│
└── docs/
    └── post5_adversarial_stress_testing.md   # The Substack post
```

## Adapting to Your Enterprise

The simulation is designed to be modified. To model your own organization:

1. **Edit `src/graph.py`** — Replace the synthetic pharma nodes/edges with your own
2. **Edit `src/scenarios.py`** — Define stress scenarios relevant to your industry
3. **Run** — Everything else (engine, adversary, figures) adapts automatically

```python
from src.graph import build_graph
from src.cascade import CascadeEngine
from src.adversary import StrategicAdversary

# Your custom graph
G = build_graph()  # modify this function

# Run Monte Carlo
engine = CascadeEngine(G, seed=42)
result = engine.run_scenario(your_scenario, N=10000)

# Run adversary
adversary = StrategicAdversary(G, seed=42)
budget_curve = adversary.budget_curve(max_k=5)
```

## The Series

This repository accompanies Post 5 of the quarterly series on **Audit 2.0 in the Age of Non-Deterministic Systems**:

| Post | Title | Instrument |
|------|-------|-----------|
| 1 | [Auditing, or Ensuring Smooth Trips into a Stochastic World](https://kunskap.substack.com/p/auditing-or-ensuring-smooth-trips) | Error-Correcting Code |
| 2 | [The Geometry of Risk](https://kunskap.substack.com/p/the-geometry-of-risk-mapping-the) | Topological Stability Index |
| 3 | [Stochastic Governance](https://kunskap.substack.com/p/stochastic-governance-from-checklists) | Bayesian PoF |
| 4 | Entropy Audits *(link TBD)* | Shannon Entropy Budget |
| **5** | **Adversarial Stress-Testing** *(this repo)* | **Monte Carlo + Red Team** |
| 6 | The Anti-Fragile Manifesto *(coming soon)* | Resilience Index |

## License

MIT — see [LICENSE](LICENSE).

---

*Francesco Orsi · [kunskap.substack.com](https://kunskap.substack.com)*
