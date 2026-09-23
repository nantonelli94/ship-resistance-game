"""
simulation_result.py — Simulation results
===========================================

Defines data structures for storing stress and load calculation results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class StressResult:
    """Stress result at a section."""
    x: float
    shear_force: float
    bending_moment: float
    stress_deck: float
    stress_keel: float
    stress_max: float
    status: str


@dataclass
class SimulationResult:
    """Complete simulation result."""
    sections: List[StressResult]
    max_stress: float
    max_stress_position: float
    total_weight: float
    buoyancy: float
    net_force: float
    gm_estimate: float
    status: str
    warnings: List[str] = field(default_factory=list)
