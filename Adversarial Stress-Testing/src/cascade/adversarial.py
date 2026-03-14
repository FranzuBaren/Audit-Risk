"""
cascade.adversarial — Adversarial analysis and intervention planning.

Implements:
1. Targeted attack simulation (force high-centrality nodes to fail)
2. Fragility multiplier (adversarial TCR / random TCR)
3. Intervention scenario comparison (modify graph, re-simulate, compare CFI)
4. Betweenness centrality ranking
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

import numpy as np

from cascade.engine import CascadeEngine, BatchResult
from cascade.graph import DependencyGraph
from cascade.metrics import CascadeMetrics, CFIComponents


@dataclass
class AdversarialResult:
    """Result of a targeted vs. random failure comparison."""
    random_tcr: float
    adversarial_tcr: float
    fragility_multiplier: float
    targeted_nodes: List[str]
    betweenness_ranking: List[Tuple[str, float]]


@dataclass
class InterventionScenario:
    """Result of re-simulating with a modified graph."""
    name: str
    description: str
    cfi: float
    tcr: float
    cfi_reduction_pct: float  # relative to baseline
    tcr_reduction_pp: float   # in percentage points
    modifications: Dict[str, str]  # human-readable list of changes


class AdversarialAnalyzer:
    """
    Adversarial analysis: targeted attacks and intervention planning.

    Parameters
    ----------
    graph : DependencyGraph
    n_simulations : int
    seed : int

    Examples
    --------
    >>> adv = AdversarialAnalyzer(graph, n_simulations=10_000)
    >>> result = adv.targeted_attack(top_n=3)
    >>> print(f"Fragility multiplier: {result.fragility_multiplier:.1f}×")
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

        # Baseline
        engine = CascadeEngine(graph, seed=seed)
        self._baseline = engine.run(n_simulations)
        self._baseline_metrics = CascadeMetrics(graph, self._baseline)
        self._baseline_cfi = self._baseline_metrics.cascade_fragility_index()

    @property
    def baseline_tcr(self) -> float:
        return self._baseline.terminal_cascade_rate

    @property
    def baseline_cfi(self) -> float:
        return self._baseline_cfi.cfi

    # ── Betweenness centrality ───────────────────────────────────

    def betweenness_ranking(self) -> List[Tuple[str, float]]:
        """
        Rank all non-terminal nodes by betweenness centrality.

        Betweenness measures how often a node sits on the shortest
        path between other pairs. High betweenness = high leverage
        for an attacker.
        """
        btw = self.graph.betweenness_centrality()
        ranking = [
            (node, val) for node, val in btw.items()
            if node != self.graph.terminal_node
        ]
        ranking.sort(key=lambda x: x[1], reverse=True)
        return ranking

    # ── Targeted attack ──────────────────────────────────────────

    def targeted_attack(self, top_n: int = 3) -> AdversarialResult:
        """
        Simulate an attack that forces the top-N betweenness nodes
        to fail, then run Monte Carlo to measure cascading impact.

        Computes the fragility multiplier: adversarial_TCR / random_TCR.
        """
        ranking = self.betweenness_ranking()
        targets = [node for node, _ in ranking[:top_n]]

        engine = CascadeEngine(self.graph, seed=self.seed)
        adv_result = engine.run(
            self.n_sims, forced_failures=set(targets)
        )

        adv_tcr = adv_result.terminal_cascade_rate
        frag_mult = adv_tcr / self.baseline_tcr if self.baseline_tcr > 0 else float("inf")

        return AdversarialResult(
            random_tcr=self.baseline_tcr,
            adversarial_tcr=adv_tcr,
            fragility_multiplier=frag_mult,
            targeted_nodes=targets,
            betweenness_ranking=ranking,
        )

    # ── Intervention scenarios ───────────────────────────────────

    def simulate_intervention(
        self,
        name: str,
        description: str,
        modified_graph: DependencyGraph,
    ) -> InterventionScenario:
        """
        Simulate one intervention by running Monte Carlo on a
        modified graph and comparing to baseline.
        """
        engine = CascadeEngine(modified_graph, seed=self.seed)
        result = engine.run(self.n_sims)
        metrics = CascadeMetrics(modified_graph, result)
        cfi = metrics.cascade_fragility_index()

        cfi_reduction = (
            (self.baseline_cfi - cfi.cfi) / self.baseline_cfi * 100
            if self.baseline_cfi > 0 else 0.0
        )
        tcr_reduction = (self.baseline_tcr - result.terminal_cascade_rate) * 100

        return InterventionScenario(
            name=name,
            description=description,
            cfi=cfi.cfi,
            tcr=result.terminal_cascade_rate,
            cfi_reduction_pct=cfi_reduction,
            tcr_reduction_pp=tcr_reduction,
            modifications={},
        )

    def compare_interventions(
        self,
        scenarios: List[Tuple[str, str, DependencyGraph]],
    ) -> List[InterventionScenario]:
        """
        Run multiple intervention scenarios and return ranked results.

        Parameters
        ----------
        scenarios : list of (name, description, modified_graph) tuples
        """
        results = []
        for name, desc, graph in scenarios:
            results.append(self.simulate_intervention(name, desc, graph))
        results.sort(key=lambda x: x.cfi)
        return results

    # ── Reporting ────────────────────────────────────────────────

    def print_report(self) -> None:
        """Print comprehensive adversarial analysis."""
        attack = self.targeted_attack()
        min_cut = self.graph.minimum_node_cut()

        print("=" * 60)
        print("ADVERSARIAL ANALYSIS")
        print("=" * 60)

        print(f"\n  BETWEENNESS CENTRALITY (top 5)")
        for node, val in attack.betweenness_ranking[:5]:
            marker = " ← TARGET" if node in attack.targeted_nodes else ""
            print(f"    {node:<22} {val:.3f}{marker}")

        print(f"\n  TARGETED ATTACK (top {len(attack.targeted_nodes)} nodes)")
        print(f"    Targets: {attack.targeted_nodes}")
        print(f"    Random TCR:      {attack.random_tcr:.1%}")
        print(f"    Adversarial TCR: {attack.adversarial_tcr:.1%}")
        print(f"    Fragility Multiplier: {attack.fragility_multiplier:.1f}×")

        print(f"\n  MINIMUM CUT SET")
        print(f"    Nodes: {min_cut}")
        print(f"    Size:  {len(min_cut)} of {self.graph.n_nodes} nodes")
        print(f"    A {len(min_cut)}-node cut in a {self.graph.n_nodes}-node "
              f"graph — infrastructure standard is 3+ node resilience")
