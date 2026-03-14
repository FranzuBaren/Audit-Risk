"""
cascade.engine — Monte Carlo cascade failure simulation.

Implements the contagion-based cascade model:
  p_shocked = 1 - (1 - p_base) * ∏(1 - w_i) for each failed predecessor i

Each simulation samples initial failures from base probabilities, then
propagates shocks through the dependency graph until equilibrium.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

import numpy as np

from cascade.graph import DependencyGraph


@dataclass
class SimulationResult:
    """Results from a single Monte Carlo simulation run."""
    failed_nodes: FrozenSet[str]
    terminal_failed: bool
    cascade_depth: int  # total nodes failed
    initial_failures: FrozenSet[str]  # nodes that failed from base probability
    propagation_rounds: int  # how many rounds the cascade took to stabilize


@dataclass
class BatchResult:
    """Aggregated results from a batch of Monte Carlo simulations."""
    n_simulations: int
    terminal_failures: int
    cascade_depths: List[int]
    node_failure_counts: Counter
    terminal_involvement: Counter  # node → count of terminal-failure scenarios it appeared in
    terminal_chains: List[FrozenSet[str]]  # sets of failed nodes in terminal scenarios
    pairwise_co_failures: Counter  # (node_a, node_b) → co-occurrence count
    individual_results: Optional[List[SimulationResult]] = None

    @property
    def terminal_cascade_rate(self) -> float:
        """Fraction of simulations where the terminal node failed."""
        return self.terminal_failures / self.n_simulations if self.n_simulations > 0 else 0.0

    @property
    def mean_cascade_depth(self) -> float:
        return float(np.mean(self.cascade_depths)) if self.cascade_depths else 0.0

    @property
    def p95_cascade_depth(self) -> float:
        return float(np.percentile(self.cascade_depths, 95)) if self.cascade_depths else 0.0


class CascadeEngine:
    """
    Monte Carlo cascade failure simulation engine.

    Given a DependencyGraph, runs N simulations where:
    1. Each node fails independently with its base probability
    2. Failed nodes propagate shocks to dependents via contagion weights
    3. Shocks compound multiplicatively for multiple failed predecessors
    4. Cascade propagates until no new failures occur (equilibrium)

    Parameters
    ----------
    graph : DependencyGraph
        The organizational dependency model.
    seed : int
        Random seed for reproducibility.

    Examples
    --------
    >>> engine = CascadeEngine(graph, seed=42)
    >>> result = engine.run(n_simulations=10_000)
    >>> print(f"Terminal cascade rate: {result.terminal_cascade_rate:.1%}")
    """

    def __init__(self, graph: DependencyGraph, seed: int = 42):
        self.graph = graph
        self.seed = seed

    def simulate_single(
        self,
        rng: np.random.Generator,
        forced_failures: Optional[Set[str]] = None,
    ) -> SimulationResult:
        """
        Run a single cascade simulation.

        Parameters
        ----------
        rng : numpy random generator
        forced_failures : optional set of node names to force-fail
            (used for adversarial analysis)

        Returns
        -------
        SimulationResult with full cascade details.
        """
        G = self.graph.nx_graph

        # Phase 1: Sample initial failures
        failed = set()
        if forced_failures:
            failed.update(forced_failures)

        for node in G.nodes:
            if node not in failed and rng.random() < G.nodes[node]["p_fail"]:
                failed.add(node)

        initial_failures = frozenset(failed)

        # Phase 2: Propagate cascade
        rounds = 0
        max_rounds = len(G.nodes)
        changed = True

        while changed and rounds < max_rounds:
            changed = False
            rounds += 1

            for node in G.nodes:
                if node in failed:
                    continue

                # Compute shocked probability from all failed predecessors
                p_survive = 1.0 - G.nodes[node]["p_fail"]
                for pred in G.predecessors(node):
                    if pred in failed:
                        w = G.edges[pred, node]["contagion"]
                        p_survive *= (1.0 - w)

                p_shocked = 1.0 - p_survive

                if rng.random() < p_shocked:
                    failed.add(node)
                    changed = True

        terminal_failed = self.graph.terminal_node in failed

        return SimulationResult(
            failed_nodes=frozenset(failed),
            terminal_failed=terminal_failed,
            cascade_depth=len(failed),
            initial_failures=initial_failures,
            propagation_rounds=rounds,
        )

    def run(
        self,
        n_simulations: int = 10_000,
        forced_failures: Optional[Set[str]] = None,
        store_individual: bool = False,
    ) -> BatchResult:
        """
        Run a batch of Monte Carlo cascade simulations.

        Parameters
        ----------
        n_simulations : int
            Number of independent simulations.
        forced_failures : optional set of node names
            Nodes forced to fail in every simulation (adversarial mode).
        store_individual : bool
            If True, store each individual SimulationResult (memory-heavy).

        Returns
        -------
        BatchResult with aggregated metrics and diagnostics.
        """
        rng = np.random.default_rng(self.seed)

        node_failure_counts = Counter()
        terminal_involvement = Counter()
        terminal_chains: List[FrozenSet[str]] = []
        cascade_depths: List[int] = []
        pairwise_co_failures = Counter()
        terminal_failures = 0
        individual_results = [] if store_individual else None

        for _ in range(n_simulations):
            result = self.simulate_single(rng, forced_failures)

            for node in result.failed_nodes:
                node_failure_counts[node] += 1

            cascade_depths.append(result.cascade_depth)

            if result.terminal_failed:
                terminal_failures += 1
                chain = result.failed_nodes - {self.graph.terminal_node}
                terminal_chains.append(chain)

                for node in chain:
                    terminal_involvement[node] += 1

                # Pairwise co-failures
                chain_sorted = sorted(chain)
                for i in range(len(chain_sorted)):
                    for j in range(i + 1, len(chain_sorted)):
                        pairwise_co_failures[
                            (chain_sorted[i], chain_sorted[j])
                        ] += 1

            if store_individual:
                individual_results.append(result)

        return BatchResult(
            n_simulations=n_simulations,
            terminal_failures=terminal_failures,
            cascade_depths=cascade_depths,
            node_failure_counts=node_failure_counts,
            terminal_involvement=terminal_involvement,
            terminal_chains=terminal_chains,
            pairwise_co_failures=pairwise_co_failures,
            individual_results=individual_results,
        )
