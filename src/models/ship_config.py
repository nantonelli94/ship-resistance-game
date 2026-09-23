"""
ship_config.py — Ship configuration models
============================================

Defines dataclasses for configuring the ship and its sections.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class SectionConfig:
    """Configuration of a ship section."""
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
        """Center position of the section."""
        return self._x_center

    @x_center.setter
    def x_center(self, value: float):
        self._x_center = value

    @property
    def total_weight(self) -> float:
        """Total weight of the section (structure + load)."""
        return self.weight_empty + abs(self.current_load)

    def set_load(self, load: float) -> None:
        """Set load with validation."""
        if abs(load) > self.capacity:
            raise ValueError(
                f"Load {load/1000:.1f} kN exceeds capacity {self.capacity/1000:.1f} kN"
            )
        self.current_load = load


@dataclass
class ShipConfig:
    """Complete ship configuration."""
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
