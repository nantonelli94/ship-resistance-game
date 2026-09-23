"""
load_manager.py — Gestor de carga y lastre
============================================

Maneja la asignación de carga y lastre a las secciones del buque
con validaciones de capacidad y compatibilidad.
"""

from __future__ import annotations

from typing import List, Optional

from models.ship_config import SectionConfig, ShipConfig


class LoadManager:
    """Gestiona la carga y lastre del buque."""

    def __init__(self, ship: ShipConfig):
        self.ship = ship

    def set_load(self, section_index: int, load: float) -> None:
        """Establece la carga de una sección por índice."""
        if section_index < 0 or section_index >= len(self.ship.sections):
            raise IndexError(f"Índice de sección inválido: {section_index}")

        section = self.ship.sections[section_index]
        if section.is_ballast:
            raise ValueError(
                f"La sección '{section.name}' es de lastre. Use set_ballast()."
            )
        section.set_load(load)

    def set_ballast(self, section_index: int, ballast: float) -> None:
        """Establece el lastre de una sección por índice."""
        if section_index < 0 or section_index >= len(self.ship.sections):
            raise IndexError(f"Índice de sección inválido: {section_index}")

        section = self.ship.sections[section_index]
        if not section.is_ballast:
            raise ValueError(
                f"La sección '{section.name}' no es de lastre. Use set_load()."
            )
        section.set_load(ballast)

    def get_ballast_sections(self) -> List[SectionConfig]:
        """Retorna las secciones de lastre."""
        return [s for s in self.ship.sections if s.is_ballast]

    def get_cargo_sections(self) -> List[SectionConfig]:
        """Retorna las secciones de carga."""
        return [s for s in self.ship.sections if not s.is_ballast]

    def get_total_cargo_weight(self) -> float:
        """Peso total de carga (sin estructura)."""
        return sum(s.current_load for s in self.ship.sections if not s.is_ballast)

    def get_total_ballast_weight(self) -> float:
        """Peso total de lastre."""
        return sum(s.current_load for s in self.ship.sections if s.is_ballast)

    def get_total_weight(self) -> float:
        """Peso total del buque (estructura + carga + lastre)."""
        return sum(s.total_weight for s in self.ship.sections)

    def reset_all_loads(self, cargo_factor: float = 0.6, ballast_factor: float = 0.3) -> None:
        """Restablece todas las cargas a valores por defecto."""
        for section in self.ship.sections:
            if section.is_ballast:
                section.set_load(section.capacity * ballast_factor)
            else:
                section.set_load(section.capacity * cargo_factor)

    def get_load_summary(self) -> dict:
        """Resumen de cargas."""
        return {
            "total_cargo_kN": self.get_total_cargo_weight() / 1000.0,
            "total_ballast_kN": self.get_total_ballast_weight() / 1000.0,
            "total_weight_kN": self.get_total_weight() / 1000.0,
            "num_cargo_sections": len(self.get_cargo_sections()),
            "num_ballast_sections": len(self.get_ballast_sections()),
        }
