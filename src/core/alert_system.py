"""
alert_system.py — Sistema de alertas semafórico
==================================================

Evalúa los resultados de la simulación y genera alertas
basadas en criterios de seguridad estructural y estabilidad.
"""

from __future__ import annotations

from models.simulation_result import SimulationResult
from utils.constants import (
    MAX_ALLOWED_STRESS,
    GM_MIN_GREEN,
    GM_MIN_YELLOW,
)


class AlertSystem:
    """Gestiona las alertas del simulador."""

    def __init__(self):
        self.alerts: list[str] = []
        self.status: str = "VERDE"

    def evaluate(self, result: SimulationResult) -> SimulationResult:
        """
        Evalúa un resultado de simulación y actualiza el estado.

        Args:
            result: Resultado de la simulación.

        Returns:
            El mismo resultado con estado actualizado.
        """
        self.alerts = []

        # Evaluar tensiones
        if result.max_stress > MAX_ALLOWED_STRESS:
            self.alerts.append(
                f"FLUENCIA: sigma_max = {result.max_stress/1e6:.1f} MPa > "
                f"{MAX_ALLOWED_STRESS/1e6:.1f} MPa en x = {result.max_stress_position:.1f} m"
            )
            result.status = "ROJO"
        elif result.max_stress > MAX_ALLOWED_STRESS * 0.75:
            self.alerts.append(
                f"PRECAUCION: sigma_max = {result.max_stress/1e6:.1f} MPa "
                f"({result.max_stress/MAX_ALLOWED_STRESS*100:.0f}% del limite)"
            )
            if result.status != "ROJO":
                result.status = "AMARILLO"

        # Evaluar estabilidad
        if result.gm_estimate < GM_MIN_YELLOW:
            self.alerts.append(
                f"VUELO INMINENTE: GM = {result.gm_estimate:.3f} m < {GM_MIN_YELLOW} m"
            )
            result.status = "ROJO"
        elif result.gm_estimate < GM_MIN_GREEN:
            self.alerts.append(
                f"ESTABILIDAD REDUCIDA: GM = {result.gm_estimate:.3f} m"
            )
            if result.status != "ROJO":
                result.status = "AMARILLO"

        # Evaluar balance de fuerzas
        if abs(result.net_force) > result.total_weight * 0.05:
            direction = "peso" if result.net_force > 0 else "empuje"
            self.alerts.append(
                f"DESBALANCE: {abs(result.net_force)/1000:.1f} kN de exceso de {direction}"
            )

        result.warnings = self.alerts
        return result

    def get_color_code(self, status: str) -> str:
        """Codigo de color ANSI para el estado."""
        from utils.constants import Colors
        color_map = {
            "VERDE": Colors.VERDE,
            "AMARILLO": Colors.AMARILLO,
            "ROJO": Colors.ROJO,
        }
        return color_map.get(status, Colors.RESET)
