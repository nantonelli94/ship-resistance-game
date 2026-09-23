"""
load_manager.py — Load and Ballast Manager
============================================

Manages the allocation of load and ballast to ship sections
with capacity and compatibility validations.
"""

from __future__ import annotations

from typing import List, Optional

from models.ship_config import SectionConfig, ShipConfig


class LoadManager:
    """Manages the ship's load and ballast."""

    def __init__(self, ship: ShipConfig):
        self.ship = ship

    def set_load(self, section_index: int, load: float) -> None:
        """Sets the load of a section by index."""
        if section_index < 0 or section_index >= len(self.ship.sections):
            raise IndexError(f"Invalid section index: {section_index}")

        section = self.ship.sections[section_index]
        if section.is_ballast:
            raise ValueError(
                f"Section '{section.name}' is a ballast tank. Use set_ballast()."
            )
        section.set_load(load)

    def set_ballast(self, section_index: int, ballast: float) -> None:
        """Sets the ballast of a section by index."""
        if section_index < 0 or section_index >= len(self.ship.sections):
            raise IndexError(f"Invalid section index: {section_index}")

        section = self.ship.sections[section_index]
        if not section.is_ballast:
            raise ValueError(
                f"Section '{section.name}' is not a ballast tank. Use set_load()."
            )
        section.set_load(ballast)

    def get_ballast_sections(self) -> List[SectionConfig]:
        """Returns the ballast sections."""
        return [s for s in self.ship.sections if s.is_ballast]

    def get_cargo_sections(self) -> List[SectionConfig]:
        """Returns the cargo sections."""
        return [s for s in self.ship.sections if not s.is_ballast]

    def get_total_cargo_weight(self) -> float:
        """Total cargo weight (excluding structure)."""
        return sum(s.current_load for s in self.ship.sections if not s.is_ballast)

    def get_total_ballast_weight(self) -> float:
        """Total ballast weight."""
        return sum(s.current_load for s in self.ship.sections if s.is_ballast)

    def get_total_weight(self) -> float:
        """Total ship weight (structure + cargo + ballast)."""
        return sum(s.total_weight for s in self.ship.sections)

    def reset_all_loads(self, cargo_factor: float = 0.6, ballast_factor: float = 0.3) -> None:
        """Resets all loads to default values."""
        for section in self.ship.sections:
            if section.is_ballast:
                section.set_load(section.capacity * ballast_factor)
            else:
                section.set_load(section.capacity * cargo_factor)

    def get_load_summary(self) -> dict:
        """Load summary."""
        return {
            "total_cargo_kN": self.get_total_cargo_weight() / 1000.0,
            "total_ballast_kN": self.get_total_ballast_weight() / 1000.0,
            "total_weight_kN": self.get_total_weight() / 1000.0,
            "num_cargo_sections": len(self.get_cargo_sections()),
            "num_ballast_sections": len(self.get_ballast_sections()),
        }
