"""
cascade.models.pharma — Pharmaceutical supply chain dependency model.

The reference model from Kunskap Post 5: a mid-size European biotech
producing a specialty injectable. 12 nodes, from single-source API
vendor through to patient supply.

Based on the Intas Pharmaceuticals / cisplatin cascade failure case study.
"""

from cascade.graph import DependencyGraph

PHARMA_NODES = {
    "API_SUPPLIER":     0.08,
    "API_TRANSPORT":    0.06,
    "EXCIPIENT_A":      0.03,
    "EXCIPIENT_B":      0.03,
    "FORMULATION":      0.04,
    "QC_LAB":           0.05,
    "LIMS":             0.07,
    "LIMS_CONTRACTOR":  0.12,
    "QP_RELEASE":       0.03,
    "REGULATORY":       0.05,
    "DISTRIBUTION":     0.04,
    "PATIENT_SUPPLY":   0.01,
}

PHARMA_EDGES = [
    ("API_SUPPLIER",    "FORMULATION",    0.95),  # Single-source API → total dependency
    ("API_TRANSPORT",   "FORMULATION",    0.80),  # Logistics disruption
    ("EXCIPIENT_A",     "FORMULATION",    0.60),  # Primary excipient
    ("EXCIPIENT_B",     "FORMULATION",    0.30),  # Backup excipient (lower contagion)
    ("FORMULATION",     "QC_LAB",         0.90),  # No product → no QC
    ("QC_LAB",          "QP_RELEASE",     0.95),  # No QC → no release
    ("LIMS",            "QC_LAB",         0.85),  # LIMS down → lab paralyzed
    ("LIMS_CONTRACTOR", "LIMS",           0.70),  # Single undocumented contractor
    ("QP_RELEASE",      "DISTRIBUTION",   0.95),  # Regulatory gate → single path
    ("REGULATORY",      "FORMULATION",    0.50),  # Regulatory hold
    ("DISTRIBUTION",    "PATIENT_SUPPLY", 0.95),  # Distribution → patient
    ("FORMULATION",     "PATIENT_SUPPLY", 0.30),  # Direct formulation impact (lower)
]

TERMINAL_NODE = "PATIENT_SUPPLY"


def build_pharma_graph() -> DependencyGraph:
    """Build the reference pharmaceutical supply chain graph."""
    return DependencyGraph.from_dicts(
        nodes=PHARMA_NODES,
        edges=PHARMA_EDGES,
        terminal_node=TERMINAL_NODE,
    )


def build_pharma_interventions(
    base_graph: DependencyGraph,
) -> list:
    """
    Build the three intervention scenarios from Post 5.

    Returns list of (name, description, modified_graph) tuples.
    """
    return [
        (
            "Backup QP",
            "Add backup Qualified Person: QP→Distribution contagion 0.95 → 0.50",
            base_graph.with_modified_edge("QP_RELEASE", "DISTRIBUTION", 0.50),
        ),
        (
            "Diversify LIMS",
            "Diversify LIMS contract: Contractor→LIMS contagion 0.70 → 0.30",
            base_graph.with_modified_edge("LIMS_CONTRACTOR", "LIMS", 0.30),
        ),
        (
            "Both interventions",
            "Backup QP + Diversified LIMS contract",
            base_graph
            .with_modified_edge("QP_RELEASE", "DISTRIBUTION", 0.50)
            .with_modified_edge("LIMS_CONTRACTOR", "LIMS", 0.30),
        ),
    ]
