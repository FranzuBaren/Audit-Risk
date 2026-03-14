"""
cascade.metrics — Derived resilience metrics from simulation results.

Computes:
- Cascade Fragility Index (CFI) and its components (TCR, BC, MCV)
- Node systemic criticality and fragility amplification factors
- Conditional terminal failure probabilities
- Pairwise co-occurrence matrix
- Bimodality coefficient (Sarle's)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
from scipy.stats import kurtosis, skew

from cascade.engine import BatchResult
from cascade.graph import DependencyGraph


@dataclass
class NodeCriticality:
    """Full criticality profile for a single node."""
    name: str
    base_failure_probability: float
    total_failure_count: int        # times this node failed across all sims
    terminal_involvement_count: int  # times it appeared in terminal-failure scenarios
    systemic_criticality_pct: float  # % of terminal scenarios it participated in
    conditional_terminal_pct: float  # P(terminal | this node fails)
    amplification_factor: float      # systemic_criticality / base_probability


@dataclass
class CFIComponents:
    """Cascade Fragility Index and its decomposition."""
    cfi: float
    terminal_cascade_rate: float  # TCR
    bimodality_coefficient: float  # BC (Sarle's)
    minimum_cut_vulnerability: float  # MCV = min_cut_size / n_nodes
    min_cut_size: int
    n_nodes: int

    @property
    def zone(self) -> str:
        if self.cfi < 1.5:
            return "Resilient"
        elif self.cfi < 3.0:
            return "Fragile"
        else:
            return "Critical"


class CascadeMetrics:
    """
    Compute all derived metrics from a simulation BatchResult.

    Parameters
    ----------
    graph : DependencyGraph
    result : BatchResult

    Examples
    --------
    >>> metrics = CascadeMetrics(graph, result)
    >>> cfi = metrics.cascade_fragility_index()
    >>> print(f"CFI = {cfi.cfi:.1f} ({cfi.zone})")
    """

    def __init__(self, graph: DependencyGraph, result: BatchResult):
        self.graph = graph
        self.result = result

    # ── Cascade Fragility Index ──────────────────────────────────

    def bimodality_coefficient(self) -> float:
        """
        Sarle's bimodality coefficient: BC = (skewness² + 1) / kurtosis.

        Uses Pearson's kurtosis (not excess). Values > 0.555 suggest
        bimodality. A perfectly bimodal distribution approaches 1.0.
        """
        depths = self.result.cascade_depths
        if len(depths) < 4:
            return 0.0
        s = skew(depths)
        k = kurtosis(depths, fisher=False)  # Pearson kurtosis
        if k == 0:
            return 0.0
        return (s ** 2 + 1) / k

    def cascade_fragility_index(self) -> CFIComponents:
        """
        Compute the Cascade Fragility Index (CFI).

        CFI = TCR × BC / MCV

        Where:
        - TCR = Terminal Cascade Rate (fraction of sims where terminal fails)
        - BC  = Bimodality Coefficient (all-or-nothing failure signature)
        - MCV = Minimum Cut Vulnerability (min_cut_size / n_nodes)

        Higher CFI = more structurally fragile.
        """
        tcr = self.result.terminal_cascade_rate
        bc = self.bimodality_coefficient()

        min_cut = self.graph.minimum_node_cut()
        min_cut_size = len(min_cut) if min_cut else self.graph.n_nodes
        mcv = min_cut_size / self.graph.n_nodes

        cfi = tcr * bc / mcv if mcv > 0 else float("inf")

        return CFIComponents(
            cfi=cfi,
            terminal_cascade_rate=tcr,
            bimodality_coefficient=bc,
            minimum_cut_vulnerability=mcv,
            min_cut_size=min_cut_size,
            n_nodes=self.graph.n_nodes,
        )

    # ── Node-level metrics ───────────────────────────────────────

    def node_criticality(self) -> List[NodeCriticality]:
        """
        Compute full criticality profiles for all non-terminal nodes.

        Returns list sorted by amplification_factor (descending).
        """
        results = []
        tf = self.result.terminal_failures

        for node in self.graph.non_terminal_nodes:
            bp = self.graph.get_base_probability(node)
            total_fail = self.result.node_failure_counts.get(node, 0)
            terminal_inv = self.result.terminal_involvement.get(node, 0)

            systemic_pct = (terminal_inv / tf * 100) if tf > 0 else 0.0
            conditional_pct = (terminal_inv / total_fail * 100) if total_fail > 0 else 0.0
            bp_pct = bp * 100
            amplification = conditional_pct / bp_pct if bp_pct > 0 else 0.0

            results.append(NodeCriticality(
                name=node,
                base_failure_probability=bp,
                total_failure_count=total_fail,
                terminal_involvement_count=terminal_inv,
                systemic_criticality_pct=systemic_pct,
                conditional_terminal_pct=conditional_pct,
                amplification_factor=amplification,
            ))

        results.sort(key=lambda x: x.amplification_factor, reverse=True)
        return results

    # ── Co-occurrence matrix ─────────────────────────────────────

    def co_occurrence_matrix(self) -> Tuple[List[str], np.ndarray]:
        """
        Build the pairwise failure co-occurrence matrix.

        Returns (node_names, matrix) where matrix[i][j] is the
        percentage of terminal-failure scenarios in which both
        nodes i and j failed.
        """
        node_names = sorted(self.graph.non_terminal_nodes)
        n = len(node_names)
        matrix = np.zeros((n, n))
        tf = self.result.terminal_failures

        if tf == 0:
            return node_names, matrix

        for chain in self.result.terminal_chains:
            for i, ni in enumerate(node_names):
                for j, nj in enumerate(node_names):
                    if ni in chain and nj in chain:
                        matrix[i][j] += 1

        matrix = matrix / tf * 100
        return node_names, matrix

    # ── Cascade severity statistics ──────────────────────────────

    def cascade_severity_stats(self) -> Dict[str, float]:
        """Summary statistics for the cascade depth distribution."""
        d = self.result.cascade_depths
        return {
            "mean": float(np.mean(d)),
            "median": float(np.median(d)),
            "std": float(np.std(d)),
            "p5": float(np.percentile(d, 5)),
            "p25": float(np.percentile(d, 25)),
            "p75": float(np.percentile(d, 75)),
            "p95": float(np.percentile(d, 95)),
            "p99": float(np.percentile(d, 99)),
            "max": int(np.max(d)),
            "bimodality_coefficient": self.bimodality_coefficient(),
        }

    # ── Reporting ────────────────────────────────────────────────

    def print_report(self) -> None:
        """Print a comprehensive analysis report to stdout."""
        cfi = self.cascade_fragility_index()
        stats = self.cascade_severity_stats()
        nodes = self.node_criticality()

        print("=" * 70)
        print("ADVERSARIAL STRESS-TEST REPORT")
        print(f"  Simulations: {self.result.n_simulations:,}")
        print(f"  Graph: {self.graph.n_nodes} nodes, {self.graph.n_edges} edges")
        print(f"  Terminal node: {self.graph.terminal_node}")
        print("=" * 70)

        print(f"\n  CASCADE FRAGILITY INDEX: {cfi.cfi:.2f}  [{cfi.zone}]")
        print(f"    TCR = {cfi.terminal_cascade_rate:.1%}  "
              f"({self.result.terminal_failures:,}/{self.result.n_simulations:,})")
        print(f"    BC  = {cfi.bimodality_coefficient:.3f}")
        print(f"    MCV = {cfi.minimum_cut_vulnerability:.3f}  "
              f"(min cut = {cfi.min_cut_size} nodes)")

        print(f"\n  CASCADE SEVERITY")
        print(f"    Mean: {stats['mean']:.1f} nodes  |  "
              f"P95: {stats['p95']:.0f} nodes  |  "
              f"Max: {stats['max']} nodes")
        print(f"    Bimodality: {stats['bimodality_coefficient']:.3f}")

        print(f"\n  NODE CRITICALITY (top 5)")
        print(f"  {'Node':<22} {'Base':>6} {'Systemic':>10} {'Cond P':>8} {'Amp':>6}")
        print(f"  {'-'*54}")
        for nc in nodes[:5]:
            print(f"  {nc.name:<22} {nc.base_failure_probability:>5.0%} "
                  f"{nc.systemic_criticality_pct:>9.1f}% "
                  f"{nc.conditional_terminal_pct:>7.1f}% "
                  f"×{nc.amplification_factor:>4.0f}")

        print(f"\n  TOP CO-FAILURE PAIRS")
        for (a, b), count in self.result.pairwise_co_failures.most_common(5):
            pct = count / self.result.terminal_failures * 100
            print(f"    {a} + {b}: {pct:.1f}%")
