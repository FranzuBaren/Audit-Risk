"""Derived metrics: bottleneck rates, co-failure, composite threat scores."""

from collections import Counter
from typing import Dict, List

import networkx as nx
import numpy as np


def compute_bottleneck_rates(
    results: List[dict],
    G: nx.DiGraph,
    exclude_baseline: bool = True,
) -> Dict[str, float]:
    """Aggregate bottleneck rates across scenarios.

    Args:
        results: List of run_scenario() outputs.
        G: The enterprise graph.
        exclude_baseline: If True, skip the first scenario (Baseline).

    Returns:
        Dict mapping node name to bottleneck rate (0.0–1.0).
    """
    stressed = results[1:] if exclude_baseline else results
    agg_bn = Counter()
    total_major = sum(r["n_major"] for r in stressed)

    for r in stressed:
        for node, count in r["bn_count"].items():
            agg_bn[node] += count

    return {
        node: agg_bn[node] / max(total_major, 1)
        for node in G.nodes()
    }


def compute_adversary_frequency(
    budget_results: List[dict],
    G: nx.DiGraph,
) -> Counter:
    """Count how often each node is targeted across budget levels.

    Returns:
        Counter mapping node name to targeting count.
    """
    freq = Counter()
    for r in budget_results:
        for node in r["targets"]:
            freq[node] += 1
    return freq


def compute_composite_threat(
    G: nx.DiGraph,
    results: List[dict],
    budget_results: List[dict],
    bn_rates: Dict[str, float],
    adv_freq: Counter,
    weights: tuple = (0.4, 0.3, 0.3),
) -> Dict[str, float]:
    """Compute composite threat score per node.

    Combines three normalized signals:
      - Fragility from Black Swan scenario (last result)
      - Adversary targeting frequency
      - Bottleneck rate

    Args:
        weights: Tuple of (fragility_weight, adversary_weight, bottleneck_weight).

    Returns:
        Dict mapping node name to composite threat score.
    """
    w_frag, w_adv, w_bn = weights

    # Fragility from worst-case scenario
    frag_vals = {
        n: results[-1]["scores"][n]["fragility"]
        for n in G.nodes()
    }
    frag_max = max(frag_vals.values()) or 1e-9

    # Adversary frequency
    adv_max = max(adv_freq.values()) if adv_freq else 1

    threat = {}
    for n in G.nodes():
        f_norm = frag_vals[n] / frag_max
        a_norm = adv_freq.get(n, 0) / max(adv_max, 1)
        b_norm = bn_rates.get(n, 0)
        threat[n] = w_frag * f_norm + w_adv * a_norm + w_bn * b_norm

    return threat
