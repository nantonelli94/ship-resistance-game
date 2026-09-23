"""
ship_config.py — Modelos de configuración del buque
====================================================

Define las dataclasses para configurar el buque y sus secciones.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class SectionConfig:
    """Configuración de una sección del buque."""
    name: str
    length: float
    weight_empty: float
    capacity: float
    current_load: float = 0.0
    is_ballast: bool = False
    _x_center: float = 0.0
    _buoyancy: float = 0.0

    @property
    def x_center(self) -> float:
        """Posición del centro de la sección."""
        return self._x_center

    @x_center.setter
    def x_center(self, value: float):
        self._x_center = value

    @property
    def total_weight(self) -> float:
        """Peso total de la sección (estructura + carga)."""
        return self.weight_empty + abs(self.current_load)

    def set_load(self, load: float) -> None:
        """Establece la carga con validación."""
        if abs(load) > self.capacity:
            raise ValueError(
                f"Carga {load/1000:.1f} kN excede capacidad {self.capacity/1000:.1f} kN"
            )
        self.current_load = load


@dataclass
class ShipConfig:
    """Configuración completa del buque."""
    name: str
    length_overall: float
    beam: float
    depth: float
    draft_design: float
    displacement: float
    sections: List[SectionConfig] = field(default_factory=list)
    deck_breadth_ratio: float = 0.85
    keel_breadth_ratio: float = 0.15
    moment_of_inertia_zz: float = 0.0
    y_deck: float = 0.0
    y_keel: float = 0.0
    sea_state: int = 0
