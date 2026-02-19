"""Cascade engine for Monte Carlo failure-propagation simulation.

The engine takes an enterprise dependency graph and a stress scenario,
then runs N independent simulations. In each simulation:
  1. Nodes fail stochastically based on base probability × shock multipliers
  2. Failures cascade through the dependency graph (parent failure increases
     child failure probability proportional to edge coupling weight)
  3. Bottleneck tracking records which nodes appear in major failures

Usage:
    engine = CascadeEngine(G, seed=42)
    result = engine.run_scenario(scenario, N=10000)
"""

from collections import Counter
from typing import Set

import networkx as nx
import numpy as np

from .scenarios import Scenario


class CascadeEngine:
    """Monte Carlo cascade simulation engine."""

    def __init__(self, G: nx.DiGraph, seed: int = 42):
        self.G = G
        self.rng = np.random.default_rng(seed)

    def cascade_from(
        self,
        initial: Set[str],
        stress: float = 1.0,
        max_depth: int = 10,
    ) -> Set[str]:
        """Propagate failures from an initial set through the graph.

        Args:
            initial: Set of initially failed node names.
            stress: Global stress multiplier for cascade propagation.
            max_depth: Maximum cascade depth to prevent infinite loops.

        Returns:
            Complete set of failed nodes (initial + cascade).
        """
        failed = set(initial)
        for _ in range(max_depth):
            new_failures = set()
            for node in self.G.nodes():
                if node in failed:
                    continue
                for parent in self.G.predecessors(node):
                    if parent in failed:
                        weight = self.G[parent][node]["weight"]
                        if self.rng.random() < min(weight * stress * 0.5, 0.9):
                            new_failures.add(node)
                            break
            if not new_failures:
                break
            failed |= new_failures
        return failed

    def run_scenario(
        self,
        scenario: Scenario,
        N: int = 10000,
        major_threshold: float = 0.25,
    ) -> dict:
        """Run N Monte Carlo simulations for a given scenario.

        Args:
            scenario: Stress scenario with shock multipliers.
            N: Number of independent simulations.
            major_threshold: Fraction of org damage to classify as "major failure".

        Returns:
            Dictionary with:
              - scenario: The Scenario object
              - N: Number of simulations
              - scores: Per-node fragility scores
              - fracs: Array of damage fractions (length N)
              - cofail: Counter of co-failure pairs
              - n_major: Number of major failures
              - bn_count: Per-node count of appearances in major failures
        """
        node_fail_count = Counter()
        cofail = Counter()
        fracs = []
        bn_count = Counter()
        n_nodes = len(self.G.nodes())

        for _ in range(N):
            # Stochastic initial failures
            initial = set()
            for node in self.G.nodes():
                attrs = self.G.nodes[node]
                p = min(
                    attrs["bp"]
                    * attrs["sm"]
                    * scenario.shocks.get(node, 1.0)
                    * scenario.global_stress,
                    0.95,
                )
                if self.rng.random() < p:
                    initial.add(node)

            # Cascade propagation
            failed = self.cascade_from(initial, scenario.global_stress)
            frac = len(failed) / n_nodes
            fracs.append(frac)

            # Track per-node failures
            for node in failed:
                node_fail_count[node] += 1

            # Track co-failure pairs
            failed_sorted = sorted(failed)
            for i, a in enumerate(failed_sorted):
                for b in failed_sorted[i + 1 :]:
                    cofail[(a, b)] += 1

            # Track bottleneck appearances in major failures
            if frac >= major_threshold:
                for node in failed:
                    bn_count[node] += 1

        # Compute scores
        n_major = sum(1 for f in fracs if f >= major_threshold)
        scores = {}
        for node in self.G.nodes():
            p_fail = node_fail_count[node] / N
            reach = len(nx.descendants(self.G, node))
            scores[node] = {
                "p_fail": p_fail,
                "reach": reach,
                "fragility": p_fail * (1 + reach / n_nodes),
                "bn_rate": bn_count[node] / max(n_major, 1),
            }

        return {
            "scenario": scenario,
            "N": N,
            "scores": scores,
            "fracs": np.array(fracs),
            "cofail": cofail,
            "n_major": n_major,
            "bn_count": bn_count,
        }
