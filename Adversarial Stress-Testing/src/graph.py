"""Enterprise dependency graph definition.

Modify this file to model your own organization. The rest of the framework
(cascade engine, adversary, plotting) adapts automatically.
"""

from dataclasses import dataclass
import networkx as nx


@dataclass
class OrgNode:
    """A node in the enterprise dependency graph.

    Attributes:
        name: Human-readable name.
        category: One of 'person', 'system', 'process', 'vendor'.
        base_prob: Base failure probability per simulation step.
        stress_mult: How much worse this node gets under stress (multiplier).
    """
    name: str
    category: str
    base_prob: float
    stress_mult: float


# ── Node definitions ──────────────────────────────────────────────────────────
# Modify these to represent your own enterprise.

NODES = {
    # People
    "QP_Lead":     OrgNode("Qualified Person",       "person",  0.008, 1.5),
    "QA_Manager":  OrgNode("QA Manager",             "person",  0.006, 1.3),
    "IT_Admin":    OrgNode("IT Infra Admin",          "person",  0.007, 1.8),
    "RA_Lead":     OrgNode("RA Lead",                 "person",  0.005, 1.2),
    "SC_Planner":  OrgNode("Supply Chain Planner",    "person",  0.006, 1.4),
    # Systems
    "ERP":         OrgNode("ERP (SAP)",               "system",  0.003, 2.0),
    "LIMS":        OrgNode("LIMS",                    "system",  0.004, 1.6),
    "EBR":         OrgNode("E-Batch Records",         "system",  0.004, 1.5),
    "DMS":         OrgNode("Doc Mgmt System",         "system",  0.003, 1.3),
    "EDC":         OrgNode("E-Data Capture",          "system",  0.005, 1.7),
    "API_GW":      OrgNode("API Integration Gateway", "system",  0.006, 2.2),
    # Processes
    "Batch_Rel":   OrgNode("Batch Release",           "process", 0.004, 1.5),
    "Dev_Handl":   OrgNode("Deviation Handling",      "process", 0.005, 1.4),
    "Chg_Ctrl":    OrgNode("Change Control",          "process", 0.004, 1.3),
    "Data_Int":    OrgNode("Data Integrity",          "process", 0.003, 1.6),
    "Reg_Sub":     OrgNode("Regulatory Submissions",  "process", 0.005, 1.4),
    # Vendors
    "API_Sup":     OrgNode("API Supplier",            "vendor",  0.008, 2.5),
    "Cloud":       OrgNode("Cloud Infrastructure",    "vendor",  0.002, 1.8),
    "CRO":         OrgNode("CRO",                     "vendor",  0.006, 1.5),
}


# ── Edge definitions ──────────────────────────────────────────────────────────
# Each tuple: (source, target, coupling_weight)
# Meaning: target depends on source; source failure increases target failure
# probability by coupling_weight * stress.

EDGES = [
    # API Gateway → core systems
    ("API_GW", "ERP",       0.90),
    ("API_GW", "LIMS",      0.85),
    ("API_GW", "EBR",       0.90),
    # ERP downstream
    ("ERP",    "Batch_Rel", 0.70),
    ("ERP",    "SC_Planner",0.60),
    ("ERP",    "Reg_Sub",   0.50),
    # LIMS downstream
    ("LIMS",   "Batch_Rel", 0.85),
    ("LIMS",   "Data_Int",  0.80),
    # EBR downstream
    ("EBR",    "Batch_Rel", 0.90),
    ("EBR",    "Data_Int",  0.85),
    ("EBR",    "Dev_Handl", 0.60),
    # People → processes
    ("QP_Lead",    "Batch_Rel", 0.95),
    ("QA_Manager", "Dev_Handl", 0.80),
    ("QA_Manager", "Chg_Ctrl",  0.70),
    ("IT_Admin",   "API_GW",    0.90),
    ("IT_Admin",   "ERP",       0.50),
    ("IT_Admin",   "LIMS",      0.50),
    ("RA_Lead",    "Reg_Sub",   0.85),
    ("SC_Planner", "API_Sup",   0.40),
    # Process → process
    ("Dev_Handl",  "Batch_Rel", 0.60),
    ("Chg_Ctrl",   "EBR",       0.50),
    ("Chg_Ctrl",   "LIMS",      0.40),
    ("Data_Int",   "Batch_Rel", 0.80),
    ("Data_Int",   "Reg_Sub",   0.70),
    # Vendors
    ("API_Sup",    "Batch_Rel", 0.85),
    ("Cloud",      "ERP",       0.60),
    ("Cloud",      "LIMS",      0.50),
    ("Cloud",      "EDC",       0.70),
    ("CRO",        "EDC",       0.60),
    ("CRO",        "Reg_Sub",   0.50),
    # DMS cross-cutting
    ("DMS",        "Dev_Handl", 0.60),
    ("DMS",        "Chg_Ctrl",  0.70),
    ("DMS",        "Reg_Sub",   0.50),
]


def build_graph() -> nx.DiGraph:
    """Build the enterprise dependency graph.

    Returns:
        A NetworkX DiGraph with node attributes (name, category, bp, sm)
        and edge attribute (weight).
    """
    G = nx.DiGraph()

    for key, node in NODES.items():
        G.add_node(
            key,
            name=node.name,
            category=node.category,
            bp=node.base_prob,
            sm=node.stress_mult,
        )

    for source, target, weight in EDGES:
        G.add_edge(source, target, weight=weight)

    return G


def get_layout(G: nx.DiGraph, seed: int = 42) -> dict:
    """Compute a stable spring layout for the graph."""
    return nx.spring_layout(G, k=3.0, iterations=200, seed=seed)
