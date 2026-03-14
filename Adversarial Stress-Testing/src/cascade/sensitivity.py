"""
cascade.sensitivity — Sensitivity analysis for cascade models.

Quantifies how robust the simulation findings are to:
1. Global contagion weight estimation error (±30%)
2. Individual node failure probability uncertainty (2× perturbation)

Produces data for the sensitivity figure (contagion sweep + tornado chart).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

from cascade.engine import CascadeEngine
from cascade.graph import DependencyGraph
from cascade.metrics import CascadeMetrics, CFIComponents


@dataclass
class PerturbationPoint:
    """Result of a single perturbation experiment."""
    factor: float          # multiplicative factor applied (e.g., 0.7, 1.0, 1.3)
    perturbation_pct: int  # human-readable: -30, 0, +30
    tcr: float
    cfi: float


@dataclass
class NodeSensitivityPoint:
    """Result of doubling one node's failure probability."""
    node: str
    original_probability: float
    perturbed_probability: float
    baseline_tcr: float
    perturbed_tcr: float
    delta_tcr_pp: float  # change in TCR in percentage points


@dataclass
class SensitivityReport:
    """Complete sensitivity analysis output."""
    contagion_sweep: List[PerturbationPoint]
    node_tornado: List[NodeSensitivityPoint]
    baseline_tcr: float
    baseline_cfi: float

    @property
    def tcr_range(self) -> Tuple[float, float]:
        """Min and max TCR across the contagion sweep."""
        tcrs = [p.tcr for p in self.contagion_sweep]
        return min(tcrs), max(tcrs)

    @property
    def most_sensitive_node(self) -> str:
        """Node whose doubling produces the largest TCR increase."""
        return max(self.node_tornado, key=lambda x: x.delta_tcr_pp).node


class SensitivityAnalyzer:
    """
    Run sensitivity analyses on a cascade model.

    Parameters
    ----------
    graph : DependencyGraph
        The baseline organizational model.
    n_simulations : int
        Simulations per experiment.
    seed : int
        Random seed for reproducibility.

    Examples
    --------
    >>> analyzer = SensitivityAnalyzer(graph, n_simulations=10_000)
    >>> report = analyzer.full_analysis()
    >>> print(f"TCR range: {report.tcr_range}")
    """

    def __init__(
        self,
        graph: DependencyGraph,
        n_simulations: int = 10_000,
        seed: int = 42,
    ):
        self.graph = graph
        self.n_sims = n_simulations
        self.seed = seed

        # Run baseline
        engine = CascadeEngine(graph, seed=seed)
        self._baseline_result = engine.run(n_simulations)
        self._baseline_metrics = CascadeMetrics(graph, self._baseline_result)
        self._baseline_cfi = self._baseline_metrics.cascade_fragility_index()

    @property
    def baseline_tcr(self) -> float:
        return self._baseline_result.terminal_cascade_rate

    @property
    def baseline_cfi(self) -> float:
        return self._baseline_cfi.cfi

    def contagion_weight_sweep(
        self,
        factors: List[float] = None,
    ) -> List[PerturbationPoint]:
        """
        Perturb ALL contagion weights by a multiplicative factor.

        Tests whether structural findings (node rankings, bimodality,
        min cut) are robust to estimation error in contagion weights.

        Parameters
        ----------
        factors : list of float
            Multiplicative factors to apply. Default: [0.7, 0.8, ..., 1.3]
        """
        if factors is None:
            factors = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]

        results = []
        G = self.graph.nx_graph

        for factor in factors:
            # Build perturbed graph
            perturbed = self.graph.copy()
            for src, dst in G.edges:
                old_w = G.edges[src, dst]["contagion"]
                new_w = min(old_w * factor, 0.99)
                perturbed._graph.edges[src, dst]["contagion"] = new_w

            # Simulate
            engine = CascadeEngine(perturbed, seed=self.seed)
            batch = engine.run(self.n_sims)
            metrics = CascadeMetrics(perturbed, batch)
            cfi = metrics.cascade_fragility_index()

            results.append(PerturbationPoint(
                factor=factor,
                perturbation_pct=int((factor - 1) * 100),
                tcr=batch.terminal_cascade_rate,
                cfi=cfi.cfi,
            ))

        return results

    def node_failure_tornado(
        self,
        nodes: List[str] = None,
        multiplier: float = 2.0,
    ) -> List[NodeSensitivityPoint]:
        """
        For each node, multiply its base failure probability and
        measure the impact on the terminal cascade rate.

        Parameters
        ----------
        nodes : list of str
            Nodes to test. Default: all non-terminal with base prob > 0.
        multiplier : float
            Factor to apply to each node's base probability.
        """
        if nodes is None:
            nodes = [
                n for n in self.graph.non_terminal_nodes
                if self.graph.get_base_probability(n) > 0
            ]

        results = []
        for node in nodes:
            original_p = self.graph.get_base_probability(node)
            perturbed_p = min(original_p * multiplier, 0.50)

            perturbed_graph = self.graph.with_modified_node(node, perturbed_p)
            engine = CascadeEngine(perturbed_graph, seed=self.seed)
            batch = engine.run(self.n_sims)

            delta = (batch.terminal_cascade_rate - self.baseline_tcr) * 100

            results.append(NodeSensitivityPoint(
                node=node,
                original_probability=original_p,
                perturbed_probability=perturbed_p,
                baseline_tcr=self.baseline_tcr,
                perturbed_tcr=batch.terminal_cascade_rate,
                delta_tcr_pp=delta,
            ))

        results.sort(key=lambda x: x.delta_tcr_pp)
        return results

    def full_analysis(
        self,
        contagion_factors: List[float] = None,
        tornado_nodes: List[str] = None,
    ) -> SensitivityReport:
        """Run both contagion sweep and node tornado."""
        sweep = self.contagion_weight_sweep(contagion_factors)
        tornado = self.node_failure_tornado(tornado_nodes)

        return SensitivityReport(
            contagion_sweep=sweep,
            node_tornado=tornado,
            baseline_tcr=self.baseline_tcr,
            baseline_cfi=self.baseline_cfi,
        )

    def print_report(self, report: SensitivityReport = None) -> None:
        """Print a human-readable sensitivity report."""
        if report is None:
            report = self.full_analysis()

        print("=" * 60)
        print("SENSITIVITY ANALYSIS")
        print("=" * 60)

        print(f"\n  Baseline TCR: {report.baseline_tcr:.1%}")
        print(f"  Baseline CFI: {report.baseline_cfi:.2f}")

        print(f"\n  CONTAGION WEIGHT SWEEP (±30%)")
        lo, hi = report.tcr_range
        print(f"  TCR range: {lo:.1%} to {hi:.1%}")
        for p in report.contagion_sweep:
            marker = " ◀ baseline" if p.perturbation_pct == 0 else ""
            print(f"    {p.perturbation_pct:+4d}%: TCR = {p.tcr:.1%}, "
                  f"CFI = {p.cfi:.2f}{marker}")

        print(f"\n  NODE SENSITIVITY TORNADO (2× base probability)")
        for ns in sorted(report.node_tornado, key=lambda x: -x.delta_tcr_pp):
            print(f"    {ns.node:<22} {ns.original_probability:.0%} → "
                  f"{ns.perturbed_probability:.0%}: "
                  f"ΔTCR = {ns.delta_tcr_pp:+.1f} pp")

        print(f"\n  Most sensitive node: {report.most_sensitive_node}")
