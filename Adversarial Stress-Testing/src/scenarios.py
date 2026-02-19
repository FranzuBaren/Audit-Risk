"""Stress scenario definitions.

Each scenario represents a compound crisis with node-specific shock multipliers
and a global stress factor. Modify these to represent threats relevant to your
industry.
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Scenario:
    """A compound stress scenario.

    Attributes:
        name: Full descriptive name.
        short: Short label for plots (≤6 chars).
        desc: One-line description.
        shocks: Node-specific shock multipliers (multiplicative on base_prob).
        global_stress: Global stress factor applied to all cascade propagation.
        color: Plot color.
    """
    name: str
    short: str
    desc: str
    shocks: Dict[str, float] = field(default_factory=dict)
    global_stress: float = 1.0
    color: str = "#9E9E9E"


# ── Color palette for scenarios ───────────────────────────────────────────────
SC_COLORS = {
    "BASE":   "#9E9E9E",
    "CYBER":  "#3B6CB5",
    "SUPPLY": "#7B4BBF",
    "DI":     "#D13B40",
    "EXODUS": "#C4852C",
    "BLACK":  "#2D2D2D",
}


def get_scenarios() -> list[Scenario]:
    """Return the default set of 6 stress scenarios."""
    return [
        Scenario(
            "Baseline", "BASE", "Normal operations, no external shocks.",
            {}, 1.0, SC_COLORS["BASE"],
        ),
        Scenario(
            "Cyber + Key-Person", "CYBER",
            "Ransomware event coinciding with IT admin absence.",
            {"Cloud": 5, "IT_Admin": 8, "API_GW": 3},
            1.3, SC_COLORS["CYBER"],
        ),
        Scenario(
            "Supply + Regulatory", "SUPPLY",
            "API supplier restriction during regulatory inspection.",
            {"API_Sup": 10, "Reg_Sub": 3, "RA_Lead": 2, "Data_Int": 2.5},
            1.5, SC_COLORS["SUPPLY"],
        ),
        Scenario(
            "Data Integrity Crisis", "DI",
            "EBR audit trail gaps cascade through quality systems.",
            {"EBR": 6, "Data_Int": 8, "QP_Lead": 4, "Batch_Rel": 5, "LIMS": 2.5},
            1.4, SC_COLORS["DI"],
        ),
        Scenario(
            "Talent Exodus", "EXODUS",
            "Key staff departures during ERP migration.",
            {"QA_Manager": 7, "IT_Admin": 6, "ERP": 4, "API_GW": 3.5,
             "Chg_Ctrl": 4, "Dev_Handl": 3},
            1.6, SC_COLORS["EXODUS"],
        ),
        Scenario(
            "Black Swan", "BLACK",
            "Pandemic + cyber + regulatory compound event.",
            {"API_Sup": 12, "Cloud": 4, "CRO": 5, "IT_Admin": 3, "API_GW": 4,
             "Reg_Sub": 3.5, "SC_Planner": 4},
            2.0, SC_COLORS["BLACK"],
        ),
    ]
