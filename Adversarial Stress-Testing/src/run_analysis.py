#!/usr/bin/env python3
"""
run_analysis.py — Complete Post 5 adversarial stress-test pipeline.

Runs:
1. Monte Carlo cascade simulation (10,000 scenarios)
2. Cascade Fragility Index computation
3. Node criticality and amplification analysis
4. Adversarial targeted-attack simulation
5. Sensitivity analysis (contagion sweep + node tornado)
6. Intervention scenario comparison

Usage:
    cd post5
    python src/run_analysis.py

Author: Francesco Orsi, PhD | kunskap.substack.com
"""

import sys
import os

# Add src to path so cascade package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cascade import (
    CascadeEngine,
    CascadeMetrics,
    SensitivityAnalyzer,
    AdversarialAnalyzer,
)
from cascade.models import build_pharma_graph, build_pharma_interventions

N_SIMULATIONS = 10_000
SEED = 42


def main():
    # ── 1. Build the graph ───────────────────────────────────────
    print("Building pharmaceutical supply chain graph...")
    graph = build_pharma_graph()
    warnings = graph.validate()
    print(graph.summary())
    if warnings:
        print(f"\n⚠ Validation warnings:")
        for w in warnings:
            print(f"  - {w}")

    # ── 2. Run Monte Carlo ───────────────────────────────────────
    print(f"\nRunning {N_SIMULATIONS:,} Monte Carlo simulations...")
    engine = CascadeEngine(graph, seed=SEED)
    result = engine.run(N_SIMULATIONS)
    print(f"Done. Terminal cascade rate: {result.terminal_cascade_rate:.1%}")

    # ── 3. Compute metrics ───────────────────────────────────────
    metrics = CascadeMetrics(graph, result)
    metrics.print_report()

    # ── 4. Adversarial analysis ──────────────────────────────────
    print("\n")
    adv = AdversarialAnalyzer(graph, N_SIMULATIONS, SEED)
    adv.print_report()

    # ── 5. Intervention scenarios ────────────────────────────────
    print(f"\n{'='*60}")
    print("INTERVENTION SCENARIOS")
    print(f"{'='*60}")
    print(f"\n  Baseline CFI: {adv.baseline_cfi:.2f}")

    interventions = build_pharma_interventions(graph)
    scenarios = adv.compare_interventions(interventions)

    for s in scenarios:
        print(f"\n  {s.name}")
        print(f"    {s.description}")
        print(f"    CFI: {s.cfi:.2f}  (−{s.cfi_reduction_pct:.0f}%)")
        print(f"    TCR: {s.tcr:.1%}  (−{s.tcr_reduction_pp:.1f} pp)")

    # ── 6. Sensitivity analysis ──────────────────────────────────
    print("\n")
    sensitivity = SensitivityAnalyzer(graph, N_SIMULATIONS, SEED)
    report = sensitivity.full_analysis()
    sensitivity.print_report(report)

    # ── Done ─────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
