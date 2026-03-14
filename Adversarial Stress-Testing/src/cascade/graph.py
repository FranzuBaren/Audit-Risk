"""
cascade.graph — Dependency graph construction and structural analysis.

A DependencyGraph models an organization as a directed network where
nodes are operational units (people, systems, vendors, processes) and
edges represent dependency relationships with contagion weights.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import networkx as nx
import numpy as np


@dataclass
class NodeSpec:
    """Specification for a single node in the dependency graph."""
    name: str
    base_failure_probability: float
    description: str = ""
    category: str = ""  # e.g., "vendor", "system", "person", "process"

    def __post_init__(self):
        if not 0 <= self.base_failure_probability <= 1:
            raise ValueError(
                f"Node '{self.name}': base_failure_probability must be in [0, 1], "
                f"got {self.base_failure_probability}"
            )


@dataclass
class EdgeSpec:
    """Specification for a directed dependency edge."""
    source: str
    target: str
    contagion_weight: float
    description: str = ""

    def __post_init__(self):
        if not 0 <= self.contagion_weight <= 1:
            raise ValueError(
                f"Edge '{self.source}' → '{self.target}': contagion_weight must be "
                f"in [0, 1], got {self.contagion_weight}"
            )


class DependencyGraph:
    """
    An organizational dependency graph for cascade failure simulation.

    Wraps a NetworkX DiGraph with domain-specific semantics:
    - Nodes carry base failure probabilities (calibrated from operational data)
    - Edges carry contagion weights (how strongly failure propagates)
    - A designated terminal node represents the ultimate outcome (e.g., patient supply)

    Parameters
    ----------
    terminal_node : str
        Name of the terminal node — the outcome we're protecting.

    Examples
    --------
    >>> g = DependencyGraph(terminal_node="PATIENT_SUPPLY")
    >>> g.add_node("API_SUPPLIER", 0.08, category="vendor")
    >>> g.add_node("FORMULATION", 0.04, category="process")
    >>> g.add_edge("API_SUPPLIER", "FORMULATION", 0.95)
    """

    def __init__(self, terminal_node: str):
        self.terminal_node = terminal_node
        self._graph = nx.DiGraph()
        self._node_specs: Dict[str, NodeSpec] = {}
        self._edge_specs: Dict[Tuple[str, str], EdgeSpec] = {}

    # ── Construction ─────────────────────────────────────────────

    def add_node(
        self,
        name: str,
        base_failure_probability: float,
        description: str = "",
        category: str = "",
    ) -> None:
        """Add a node with its base failure probability."""
        spec = NodeSpec(name, base_failure_probability, description, category)
        self._node_specs[name] = spec
        self._graph.add_node(name, p_fail=base_failure_probability)

    def add_edge(
        self,
        source: str,
        target: str,
        contagion_weight: float,
        description: str = "",
    ) -> None:
        """Add a directed dependency edge with a contagion weight."""
        if source not in self._node_specs:
            raise ValueError(f"Source node '{source}' not in graph")
        if target not in self._node_specs:
            raise ValueError(f"Target node '{target}' not in graph")
        spec = EdgeSpec(source, target, contagion_weight, description)
        self._edge_specs[(source, target)] = spec
        self._graph.add_edge(source, target, contagion=contagion_weight)

    # ── Bulk construction ────────────────────────────────────────

    @classmethod
    def from_dicts(
        cls,
        nodes: Dict[str, float],
        edges: List[Tuple[str, str, float]],
        terminal_node: str,
    ) -> DependencyGraph:
        """
        Build a graph from simple dictionaries.

        Parameters
        ----------
        nodes : dict
            Mapping of node name → base failure probability.
        edges : list of (source, target, contagion_weight)
        terminal_node : str
        """
        g = cls(terminal_node=terminal_node)
        for name, p_fail in nodes.items():
            g.add_node(name, p_fail)
        for src, dst, w in edges:
            g.add_edge(src, dst, w)
        g.validate()
        return g

    @classmethod
    def from_csv(
        cls,
        nodes_path: str | Path,
        edges_path: str | Path,
        terminal_node: str,
    ) -> DependencyGraph:
        """
        Load a graph from two CSV files.

        nodes.csv: name, base_failure_probability, [category], [description]
        edges.csv: source, target, contagion_weight, [description]
        """
        g = cls(terminal_node=terminal_node)

        with open(nodes_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                g.add_node(
                    name=row["name"],
                    base_failure_probability=float(row["base_failure_probability"]),
                    category=row.get("category", ""),
                    description=row.get("description", ""),
                )

        with open(edges_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                g.add_edge(
                    source=row["source"],
                    target=row["target"],
                    contagion_weight=float(row["contagion_weight"]),
                    description=row.get("description", ""),
                )

        g.validate()
        return g

    # ── Validation ───────────────────────────────────────────────

    def validate(self) -> List[str]:
        """
        Validate graph structure and return warnings.

        Raises ValueError for fatal issues.
        Returns list of warning strings for non-fatal concerns.
        """
        warnings = []

        if self.terminal_node not in self._node_specs:
            raise ValueError(
                f"Terminal node '{self.terminal_node}' not found in graph"
            )

        if not nx.is_weakly_connected(self._graph):
            warnings.append(
                "Graph is not weakly connected — some nodes are isolated "
                "and will never participate in cascades"
            )

        # Check for cycles (unusual in dependency graphs)
        cycles = list(nx.simple_cycles(self._graph))
        if cycles:
            warnings.append(
                f"Graph contains {len(cycles)} cycle(s): {cycles[:3]}. "
                "Cycles create feedback loops in cascade propagation."
            )

        # Check terminal node is reachable
        sources = [n for n in self._graph.nodes if self._graph.in_degree(n) == 0]
        for source in sources:
            if not nx.has_path(self._graph, source, self.terminal_node):
                warnings.append(
                    f"Source node '{source}' has no path to terminal "
                    f"node '{self.terminal_node}'"
                )

        # Check for very high base probabilities
        for name, spec in self._node_specs.items():
            if spec.base_failure_probability > 0.30:
                warnings.append(
                    f"Node '{name}' has high base failure probability "
                    f"({spec.base_failure_probability:.0%}). "
                    "Verify this is calibrated from operational data."
                )

        return warnings

    # ── Structural queries ───────────────────────────────────────

    @property
    def nx_graph(self) -> nx.DiGraph:
        """Access the underlying NetworkX DiGraph."""
        return self._graph

    @property
    def node_names(self) -> List[str]:
        return list(self._graph.nodes)

    @property
    def non_terminal_nodes(self) -> List[str]:
        return [n for n in self._graph.nodes if n != self.terminal_node]

    @property
    def n_nodes(self) -> int:
        return len(self._graph.nodes)

    @property
    def n_edges(self) -> int:
        return len(self._graph.edges)

    def get_base_probability(self, node: str) -> float:
        return self._graph.nodes[node]["p_fail"]

    def get_contagion_weight(self, source: str, target: str) -> float:
        return self._graph.edges[source, target]["contagion"]

    def predecessors(self, node: str) -> List[str]:
        return list(self._graph.predecessors(node))

    def successors(self, node: str) -> List[str]:
        return list(self._graph.successors(node))

    def betweenness_centrality(self) -> Dict[str, float]:
        """Compute betweenness centrality for all nodes."""
        return nx.betweenness_centrality(self._graph)

    def minimum_node_cut(self) -> Set[str]:
        """
        Find the minimum set of nodes whose removal disconnects
        any source from the terminal node.
        """
        sources = [n for n in self._graph.nodes
                   if self._graph.in_degree(n) == 0]
        min_cut = None
        for source in sources:
            try:
                cut = nx.minimum_node_cut(
                    self._graph, source, self.terminal_node
                )
                if min_cut is None or len(cut) < len(min_cut):
                    min_cut = cut
            except nx.NetworkXError:
                continue
        return min_cut or set()

    # ── Modification (for interventions / sensitivity) ───────────

    def copy(self) -> DependencyGraph:
        """Return a deep copy of this graph."""
        new = DependencyGraph(terminal_node=self.terminal_node)
        for name, spec in self._node_specs.items():
            new.add_node(name, spec.base_failure_probability,
                         spec.description, spec.category)
        for (src, dst), spec in self._edge_specs.items():
            new.add_edge(src, dst, spec.contagion_weight, spec.description)
        return new

    def with_modified_edge(
        self, source: str, target: str, new_weight: float
    ) -> DependencyGraph:
        """Return a copy with one edge's contagion weight changed."""
        g = self.copy()
        g._graph.edges[source, target]["contagion"] = new_weight
        g._edge_specs[(source, target)] = EdgeSpec(
            source, target, new_weight,
            g._edge_specs[(source, target)].description
        )
        return g

    def with_modified_node(
        self, node: str, new_probability: float
    ) -> DependencyGraph:
        """Return a copy with one node's base failure probability changed."""
        g = self.copy()
        g._graph.nodes[node]["p_fail"] = new_probability
        old = g._node_specs[node]
        g._node_specs[node] = NodeSpec(
            node, new_probability, old.description, old.category
        )
        return g

    # ── Export ────────────────────────────────────────────────────

    def to_json(self) -> dict:
        """Serialize to a JSON-compatible dictionary."""
        return {
            "terminal_node": self.terminal_node,
            "nodes": {
                name: {
                    "base_failure_probability": spec.base_failure_probability,
                    "category": spec.category,
                    "description": spec.description,
                }
                for name, spec in self._node_specs.items()
            },
            "edges": [
                {
                    "source": spec.source,
                    "target": spec.target,
                    "contagion_weight": spec.contagion_weight,
                    "description": spec.description,
                }
                for spec in self._edge_specs.values()
            ],
        }

    def summary(self) -> str:
        """Return a human-readable summary of the graph."""
        lines = [
            f"DependencyGraph: {self.n_nodes} nodes, {self.n_edges} edges",
            f"Terminal node: {self.terminal_node}",
            f"Source nodes: {[n for n in self.node_names if self._graph.in_degree(n) == 0]}",
            f"Max base failure probability: "
            f"{max(s.base_failure_probability for s in self._node_specs.values()):.0%} "
            f"({max(self._node_specs.values(), key=lambda s: s.base_failure_probability).name})",
            f"Max contagion weight: "
            f"{max(s.contagion_weight for s in self._edge_specs.values()):.2f}",
        ]
        return "\n".join(lines)

    def __repr__(self) -> str:
        return (
            f"DependencyGraph(nodes={self.n_nodes}, edges={self.n_edges}, "
            f"terminal='{self.terminal_node}')"
        )
