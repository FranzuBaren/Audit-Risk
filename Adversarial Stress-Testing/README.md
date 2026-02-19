# 🎯 Adversarial Stress-Testing: The Corporate "Turing Test"

**Monte Carlo Failure-Cascade Simulation with Strategic Adversary for Enterprise Audit**

Post 5 of 6 — *Audit 2.0 in the Age of Non-Deterministic Systems*

[![Substack](https://img.shields.io/badge/Substack-kunskap-orange?logo=substack)](https://kunskap.substack.com)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## The Problem

Traditional audit is forensic. It investigates the past — sampling transactions, checking controls, reporting what went wrong. Even modern continuous monitoring (Bayesian updating, entropy budgets) is fundamentally *reactive*: it watches signals and updates beliefs about the present.

What none of these instruments answer is: **how could this organization fail in ways that have never happened before?**

A risk register lists individual nodes and scores them in isolation. But enterprise failure is rarely about a single node. It's about *cascades* — compound events where the failure of one component propagates through dependency chains, overwhelming controls that work perfectly in isolation. These cascading failure modes are invisible to node-level assessment because they emerge from **network topology**, not from individual node properties.

This project addresses that gap with two complementary techniques:

1. **Scenario Monte Carlo** — Stochastic simulation of failure cascades across plausible compound crises
2. **Strategic Adversary** — A synthetic agent that reasons about graph topology to find optimal attack strategies

Together, they constitute a computational red team for enterprise audit.

---

## Theoretical Foundation

### The Enterprise as a Directed Dependency Graph

We model the organization as a directed graph $G = (V, E)$ where:

- **Nodes** $V$ represent irreducible operational units: people, systems, processes, and external vendors
- **Edges** $E$ represent dependency: if $(u, v) \in E$ with weight $w_{uv}$, then $v$ depends on $u$, and $u$'s failure increases $v$'s failure probability proportionally to $w_{uv}$

Each node $v$ carries two intrinsic parameters:
- **Base failure probability** $p_v$: the probability of spontaneous failure per simulation step
- **Stress multiplier** $s_v$: how much worse the node performs under pressure

This graph-theoretic framing connects directly to the **enterprise manifold** described in [Post 2](https://kunskap.substack.com/p/the-geometry-of-risk-mapping-the) of the series. Points of high topological convergence (many incoming dependency paths) correspond to regions of high curvature on the manifold — places where small perturbations produce disproportionately large deformations.

### Cascade Propagation

Given a set of initially failed nodes $F_0 \subseteq V$, the cascade unfolds iteratively. At each step $t$, every non-failed node $v \notin F_t$ checks its parents: if any parent $u \in F_t$, node $v$ fails with probability $\min(w_{uv} \cdot \sigma \cdot 0.5, \ 0.9)$ where $\sigma$ is the scenario's global stress factor. The cascade terminates when no new failures occur (fixed point) or after a maximum depth.

This produces a final failure set $F^* \supseteq F_0$. The **damage fraction** is $|F^*| / |V|$.

### Scenario Monte Carlo

A scenario $\mathcal{S}$ defines:
- Node-specific shock multipliers $\{m_v^{\mathcal{S}}\}$ (e.g., IT_Admin gets $8\times$ under Cyber scenario)
- A global stress factor $\sigma^{\mathcal{S}}$

For each of $N = 10{,}000$ simulations, we sample initial failures stochastically:

$$v \in F_0 \iff U_v < \min(p_v \cdot s_v \cdot m_v^{\mathcal{S}} \cdot \sigma^{\mathcal{S}}, \ 0.95) \quad \text{where } U_v \sim \text{Uniform}(0, 1)$$

then propagate the cascade, recording the damage fraction. Across 6 scenarios this yields 60,000 simulated futures — an ensemble whose distributional properties reveal structural fragility invisible to point estimates.

### The Strategic Adversary

Random Monte Carlo explores the failure space uniformly. A real adversary doesn't. It *reasons* about topology, selecting targets that maximize cascade propagation.

The adversary solves a discrete optimization problem:

$$\text{arg}\max_{T \subseteq V, \ |T| = k} \quad \mathbb{E}\left[\frac{|F^*(T)|}{|V|}\right]$$

where $F^*(T)$ is the cascade closure from targeting set $T$, and the expectation is over Monte Carlo samples.

For $k \leq 3$: exhaustive evaluation of all $\binom{|V|}{k}$ combinations, each estimated with 800 cascade simulations. For $k > 3$: greedy selection — iteratively adding the node with maximum marginal damage.

This yields two complementary vulnerability signatures:

| | Monte Carlo | Strategic Adversary |
|---|---|---|
| **Finds** | Convergence points | Leverage points |
| **Meaning** | Nodes that *appear* in cascades (everything flows through them) | Nodes whose *removal initiates* maximum cascades |
| **Example** | Batch Release (100% of major failures) | IT Admin + DMS (61% damage from 2 nodes) |
| **Remediation** | Add redundancy, decouple dependencies | Harden infrastructure, cross-train key personnel |

A complete audit needs both perspectives.

---

## Key Findings

From the synthetic pharmaceutical enterprise (19 nodes, 33 edges):

### Scenario Monte Carlo (60,000 simulations)

| Scenario | Mean Damage | P95 | Major Failures |
|----------|------------|-----|----------------|
| Baseline | 2.1% | 11% | 252 |
| Cyber + Key-Person | 9.2% | 53% | 1,664 |
| Supply + Regulatory | 6.5% | 32% | 650 |
| Data Integrity Crisis | 5.7% | 32% | 754 |
| Talent Exodus | 13.5% | 58% | 2,469 |
| Black Swan | 17.2% | 58% | 2,587 |

### Strategic Adversary

| Budget $k$ | Optimal Targets | Expected Damage |
|-----------|----------------|----------------|
| 1 | API Gateway | 44% |
| 2 | IT Admin, DMS | 61% |
| 3 | IT Admin, DMS, Cloud | 73% |
| 4 | IT Admin, DMS, Cloud, CRO | 78% |
| 5 | IT Admin, DMS, Cloud, API GW, QA Manager | 79% |

### Three Audit Findings

**Finding 1: Batch Release is a topological singularity.** Present in 100% of major failures across all stressed scenarios. The topology of dependencies funnels every cascade through it. The recommendation is not "audit more frequently" but "redesign the dependency structure."

**Finding 2: The adversary targets infrastructure, not processes.** IT Admin, DMS, and Cloud are the leverage points — their removal cuts off multiple downstream paths simultaneously. Traditional audit under-invests in infrastructure-layer assurance.

**Finding 3: Co-failure correlations are invisible to risk registers.** API Supplier and Batch Release co-fail in 49% of Black Swan simulations. Batch Release and Regulatory Submissions co-fail at 27%. These correlations emerge from topology, not from individual node properties.

---

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/audit2-adversarial.git
cd audit2-adversarial

pip install -r requirements.txt

# Full simulation + all 9 figures (~30 seconds)
python src/run_simulation.py

# Or explore interactively
jupyter notebook notebooks/adversarial_stress_test.ipynb
```

## Project Structure

```
audit2-adversarial/
├── README.md
├── LICENSE                 # MIT
├── requirements.txt
├── setup.py
│
├── src/
│   ├── graph.py            # Enterprise dependency graph  ← EDIT THIS
│   ├── scenarios.py        # Stress scenario definitions  ← EDIT THIS
│   ├── cascade.py          # CascadeEngine (Monte Carlo core)
│   ├── adversary.py        # StrategicAdversary (synthetic red team)
│   ├── metrics.py          # Bottleneck, co-failure, composite threat
│   ├── plotting.py         # 9 publication-quality figures
│   └── run_simulation.py   # CLI runner
│
├── notebooks/
│   └── adversarial_stress_test.ipynb
│
├── figures/                # Pre-generated outputs (300 DPI)
│
└── docs/
    └── post5_adversarial_stress_testing.md
```

## Adapting to Your Enterprise

The framework is designed to be modified. Two files control the entire model:

**`src/graph.py`** — Replace the synthetic pharma nodes and edges with your own operational dependencies. Each node needs a name, category, base failure probability, and stress multiplier. Each edge needs a source, target, and coupling weight (0–1).

**`src/scenarios.py`** — Define compound stress scenarios relevant to your industry. Each scenario specifies which nodes get shocked (and by how much) and a global stress factor.

Everything else — the cascade engine, adversary, metrics, and all 9 figures — adapts automatically.

```python
from src.graph import build_graph
from src.cascade import CascadeEngine
from src.adversary import StrategicAdversary

G = build_graph()                                # your custom graph
engine = CascadeEngine(G, seed=42)
result = engine.run_scenario(your_scenario, N=10000)

adversary = StrategicAdversary(G, seed=42)
budget_curve = adversary.budget_curve(max_k=5)   # find your leverage points
```

### Calibration Notes

The synthetic enterprise uses parameters chosen for pedagogical clarity. When adapting to a real organization:

- **Base failure probabilities** should reflect historical incident rates (annualized, converted to per-simulation-step probabilities)
- **Coupling weights** should reflect actual dependency strength — a weight of 0.9 means "if the parent fails, the child almost certainly degrades." These are judgment calls informed by operational experience, BIA assessments, and incident correlation data
- **Stress multipliers** capture how much worse a node performs under pressure. IT infrastructure with no redundancy has high multipliers; well-staffed processes with backup personnel have low ones
- **Scenario shocks** should map to your threat landscape. Run a workshop with risk owners to define 4–6 plausible compound events

The model's value is not in the absolute numbers (which depend on calibration) but in the **relative ranking** of vulnerabilities and the **structural patterns** (bottlenecks, leverage points, co-failure correlations) that emerge from topology.

---

## The Series

This repository accompanies Post 5 of the quarterly series **Audit 2.0 in the Age of Non-Deterministic Systems**:

| # | Post | Instrument | Core Idea |
|---|------|-----------|-----------|
| 1 | [Auditing, or Ensuring Smooth Trips into a Stochastic World](https://kunskap.substack.com/p/auditing-or-ensuring-smooth-trips) | Error-Correcting Code | Audit as the counter-entropic force preserving Strategic Intent |
| 2 | [The Geometry of Risk](https://kunskap.substack.com/p/the-geometry-of-risk-mapping-the) | Topological Stability Index | Risk has a shape; manifold curvature predicts crises 30–40 days ahead |
| 3 | [Stochastic Governance](https://kunskap.substack.com/p/stochastic-governance-from-checklists) | Bayesian PoF | Continuous belief updating via Beta-Binomial conjugacy replaces static dashboards |
| 4 | Entropy Audits *(link TBD)* | Shannon Entropy Budget | Measuring information loss in bits; 114-day detection advantage |
| **5** | **Adversarial Stress-Testing** *(this repo)* | **Monte Carlo + Red Team** | **60,000 simulated futures reveal structural fragility** |
| 6 | The Anti-Fragile Manifesto *(coming soon)* | Resilience Index | Jensen's Inequality, convex design, the Auditor as Risk Architect |

---

## License

MIT — see [LICENSE](LICENSE).

## Author

Francesco Orsi · [kunskap.substack.com](https://kunskap.substack.com)
