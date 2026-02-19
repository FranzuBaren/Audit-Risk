#!/usr/bin/env python3
"""End-to-end adversarial stress-test runner.

Usage:
    python -m src.run_simulation          # from project root
    python src/run_simulation.py          # direct execution

Outputs 9 publication-quality figures to figures/ and prints a full audit report.
"""

import os
import sys
import time
from collections import Counter

import numpy as np

# Allow both `python src/run_simulation.py` and `python -m src.run_simulation`
if __name__ == "__main__" and not __package__:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.graph import build_graph, get_layout
from src.scenarios import get_scenarios
from src.cascade import CascadeEngine
from src.adversary import StrategicAdversary
from src.metrics import (
    compute_bottleneck_rates,
    compute_adversary_frequency,
    compute_composite_threat,
)
from src.plotting import (
    fig1_graph, fig2_heatmap, fig3_ridgeplot, fig4_bottleneck,
    fig5_adversary, fig6_cascade, fig7_cofailure, fig8_dotstrip,
    fig9_threatmap,
)


def main():
    t0 = time.time()
    outdir = "figures"
    os.makedirs(outdir, exist_ok=True)

    # ── Build graph ───────────────────────────────────────────────────────
    print("Building enterprise dependency graph...")
    G = build_graph()
    pos = get_layout(G)
    print(f"  {G.number_of_nodes()} nodes, {G.number_of_edges()} edges\n")

    # ── Scenario Monte Carlo ──────────────────────────────────────────────
    scenarios = get_scenarios()
    engine = CascadeEngine(G, seed=42)
    results = []

    print("Running 60,000 scenario simulations...")
    for sc in scenarios:
        r = engine.run_scenario(sc, N=10000)
        results.append(r)
        fracs = r["fracs"]
        print(f"  [{sc.short:6s}] mean={fracs.mean():.1%}  "
              f"P95={np.percentile(fracs, 95):.0%}  "
              f"major={r['n_major']}")

    # ── Strategic Adversary ───────────────────────────────────────────────
    print("\nRunning strategic adversary (this takes 1-2 minutes)...")
    adversary = StrategicAdversary(G, seed=42)
    budget_results = adversary.budget_curve(max_k=5, n_sims=800, stress=1.5)

    # ── Derived metrics ───────────────────────────────────────────────────
    print("\nComputing derived metrics...")
    bn_rates = compute_bottleneck_rates(results, G)
    adv_freq = compute_adversary_frequency(budget_results, G)
    threat = compute_composite_threat(G, results, budget_results, bn_rates, adv_freq)

    stressed = [r for r in results if r["scenario"].short != "BASE"]
    total_major = sum(r["n_major"] for r in stressed)

    # ── Generate figures ──────────────────────────────────────────────────
    print(f"\nGenerating 9 figures to {outdir}/...")
    fig1_graph(G, pos, outdir)
    print("  ✓ fig1_graph.png")
    fig2_heatmap(G, results, outdir)
    print("  ✓ fig2_heatmap.png")
    fig3_ridgeplot(results, outdir)
    print("  ✓ fig3_ridgeplot.png")
    fig4_bottleneck(G, bn_rates, total_major, outdir)
    print("  ✓ fig4_bottleneck.png")
    fig5_adversary(G, budget_results, outdir)
    print("  ✓ fig5_adversary.png")
    fig6_cascade(G, pos, budget_results, outdir)
    print("  ✓ fig6_cascade.png")
    fig7_cofailure(G, pos, results, outdir)
    print("  ✓ fig7_cofailure.png")
    fig8_dotstrip(G, results, outdir)
    print("  ✓ fig8_dotstrip.png")
    fig9_threatmap(G, pos, results, threat, bn_rates, adv_freq, budget_results, outdir)
    print("  ✓ fig9_threatmap.png")

    # ── Audit report ──────────────────────────────────────────────────────
    elapsed = time.time() - t0
    print(f"\n{'='*66}")
    print(f" COMPLETE AUDIT FINDINGS  ({elapsed:.0f}s elapsed)")
    print(f"{'='*66}")

    print("\n─── A. SCENARIO MONTE CARLO ─────────────────────────────────────")
    for r in results[1:]:
        s = r["scenario"]
        fracs = r["fracs"]
        print(f"\n  {s.name}:")
        print(f"    mean={fracs.mean():.1%}  P95={np.percentile(fracs, 95):.0%}  "
              f"major failures={r['n_major']}")
        top3 = sorted(r["scores"].items(), key=lambda x: x[1]["fragility"], reverse=True)[:3]
        for n, v in top3:
            print(f"    {n:18s} frag={v['fragility']:.3f}  "
                  f"P(fail)={v['p_fail']:.1%}  "
                  f"bottleneck={v['bn_rate']:.0%}")

    print("\n─── B. STRATEGIC ADVERSARY ──────────────────────────────────────")
    for r in budget_results:
        print(f"  k={r['k']}: {r['targets']} -> {r['damage']:.1%}")

    print("\n─── C. STRUCTURAL BOTTLENECKS ───────────────────────────────────")
    for n, rate in sorted(bn_rates.items(), key=lambda x: -x[1])[:8]:
        print(f"  {n:18s} [{G.nodes[n]['category']:7s}]  "
              f"in {rate:.0%} of major failures")

    print("\n─── D. CO-FAILURE PAIRS (Black Swan) ───────────────────────────")
    cofail = results[-1]["cofail"]
    N_bs = results[-1]["N"]
    top_cf = sorted(cofail.items(), key=lambda x: x[1], reverse=True)[:5]
    for (a, b), c in top_cf:
        print(f"  {a} + {b}: {c/N_bs:.1%}")

    print("\n─── E. COMPOSITE THREAT (Top 10) ───────────────────────────────")
    for n, t in sorted(threat.items(), key=lambda x: -x[1])[:10]:
        print(f"  {n:18s} [{G.nodes[n]['category']:7s}]  threat={t:.3f}")

    print(f"\n{'='*66}")
    print(f"  9 figures saved to {outdir}/")
    print(f"  Total simulations: 60,000 Monte Carlo + adversary analysis")
    print(f"  Runtime: {elapsed:.0f}s")
    print(f"{'='*66}")


if __name__ == "__main__":
    main()
