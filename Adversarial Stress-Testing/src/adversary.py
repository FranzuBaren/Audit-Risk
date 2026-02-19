"""Strategic adversary — synthetic red team agent.

The adversary reasons about the graph topology to find the optimal set of k
nodes to knock out in order to maximize expected organizational damage.

For k ≤ 3: exhaustive evaluation of all C(n, k) combinations.
For k > 3: greedy selection (add node with maximum marginal damage).
Each candidate is evaluated with multiple Monte Carlo cascades.

Usage:
    adversary = StrategicAdversary(G, seed=42)
    budget_curve = adversary.budget_curve(max_k=5)
"""

from itertools import combinations
from typing import Set, Tuple

import networkx as nx
import numpy as np

from .cascade import CascadeEngine


class StrategicAdversary:
    """A synthetic agent that optimally selects attack targets."""

    def __init__(self, G: nx.DiGraph, seed: int = 42):
        self.G = G
        self.engine = CascadeEngine(G, seed)

    def evaluate_attack(
        self,
        targets: Set[str],
        n_sims: int = 800,
        stress: float = 1.5,
    ) -> float:
        """Estimate expected damage from knocking out a set of targets.

        Args:
            targets: Set of node names to disable.
            n_sims: Number of Monte Carlo cascades for estimation.
            stress: Stress multiplier for cascade propagation.

        Returns:
            Expected fraction of organization damaged.
        """
        n_nodes = len(self.G.nodes())
        damages = [
            len(self.engine.cascade_from(targets, stress)) / n_nodes
            for _ in range(n_sims)
        ]
        return float(np.mean(damages))

    def find_optimal(
        self,
        k: int,
        n_sims: int = 800,
        stress: float = 1.5,
    ) -> Tuple[Set[str], float]:
        """Find the optimal k-node attack strategy.

        For k ≤ 3: exhaustive search over all C(n, k) combinations.
        For k > 3: greedy optimization (add best marginal node iteratively).

        Args:
            k: Attack budget (number of nodes to knock out).
            n_sims: Monte Carlo samples per candidate evaluation.
            stress: Stress multiplier.

        Returns:
            Tuple of (optimal target set, expected damage fraction).
        """
        nodes = list(self.G.nodes())

        if k <= 3:
            # Exhaustive search
            best_damage, best_targets = 0.0, None
            combos = list(combinations(nodes, k))
            print(f"    Evaluating {len(combos)} combinations (k={k})...")
            for combo in combos:
                damage = self.evaluate_attack(set(combo), n_sims, stress)
                if damage > best_damage:
                    best_damage = damage
                    best_targets = set(combo)
            return best_targets, best_damage

        else:
            # Greedy selection
            selected = set()
            for step in range(k):
                best_node, best_damage = None, 0.0
                for node in nodes:
                    if node in selected:
                        continue
                    candidate = selected | {node}
                    damage = self.evaluate_attack(candidate, n_sims, stress)
                    if damage > best_damage:
                        best_damage = damage
                        best_node = node
                print(f"    Step {step+1}: +{best_node} -> {best_damage:.1%}")
                selected.add(best_node)
            return selected, best_damage

    def budget_curve(
        self,
        max_k: int = 5,
        n_sims: int = 800,
        stress: float = 1.5,
    ) -> list[dict]:
        """Run the adversary for budgets k=1 through max_k.

        Returns:
            List of dicts with keys: k, targets, damage.
        """
        results = []
        for k in range(1, max_k + 1):
            print(f"  Budget k={k}:")
            targets, damage = self.find_optimal(k, n_sims, stress)
            results.append({"k": k, "targets": targets, "damage": damage})
            print(f"    Optimal: {targets} -> {damage:.1%}")
        return results
