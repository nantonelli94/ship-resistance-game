"""
simulation_result.py — Resultados de simulación
================================================

Define las estructuras de datos para almacenar los resultados
del cálculo de esfuerzos y tensiones.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class StressResult:
    """Resultado de tensiones en una sección."""
    x: float
    shear_force: float
    bending_moment: float
    stress_deck: float
    stress_keel: float
    stress_max: float
    status: str


@dataclass
class SimulationResult:
    """Resultado completo de la simulación."""
    sections: List[StressResult]
    max_stress: float
    max_stress_position: float
    total_weight: float
    buoyancy: float
    net_force: float
    gm_estimate: float
    status: str
    warnings: List[str] = field(default_factory=list)
