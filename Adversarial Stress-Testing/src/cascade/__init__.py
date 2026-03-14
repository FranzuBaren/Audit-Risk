"""
cascade — Adversarial stress-testing framework for organizational
dependency graphs.

Monte Carlo failure-cascade simulation, structural analysis, and
resilience metric computation for audit and GRC applications.

Author: Francesco Orsi, PhD | kunskap.substack.com
"""

from cascade.graph import DependencyGraph
from cascade.engine import CascadeEngine
from cascade.metrics import CascadeMetrics
from cascade.sensitivity import SensitivityAnalyzer
from cascade.adversarial import AdversarialAnalyzer

__version__ = "0.5.0"
__all__ = [
    "DependencyGraph",
    "CascadeEngine",
    "CascadeMetrics",
    "SensitivityAnalyzer",
    "AdversarialAnalyzer",
]
