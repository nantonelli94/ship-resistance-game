"""
alert_system.py — Traffic light alert system
============================================

Evaluates simulation results and generates alerts based on
structural safety and stability criteria.
"""

from __future__ import annotations

from models.simulation_result import SimulationResult
from utils.constants import (
    MAX_ALLOWED_STRESS,
    GM_MIN_GREEN,
    GM_MIN_YELLOW,
)


class AlertSystem:
    """Manages simulator alerts."""

    def __init__(self):
        self.alerts: list[str] = []
        self.status: str = "VERDE"

    def evaluate(self, result: SimulationResult) -> SimulationResult:
        """
        Evaluates a simulation result and updates the status.

        Args:
            result: Simulation result.

        Returns:
            The same result with updated status.
        """
        self.alerts = []

        # Evaluate stresses
        if result.max_stress > MAX_ALLOWED_STRESS:
            self.alerts.append(
                f"YIELD: sigma_max = {result.max_stress/1e6:.1f} MPa > "
                f"{MAX_ALLOWED_STRESS/1e6:.1f} MPa at x = {result.max_stress_position:.1f} m"
            )
            result.status = "ROJO"
        elif result.max_stress > MAX_ALLOWED_STRESS * 0.75:
            self.alerts.append(
                f"CAUTION: sigma_max = {result.max_stress/1e6:.1f} MPa "
                f"({result.max_stress/MAX_ALLOWED_STRESS*100:.0f}% of limit)"
            )
            if result.status != "ROJO":
                result.status = "AMARILLO"

        # Evaluate stability
        if result.gm_estimate < GM_MIN_YELLOW:
            self.alerts.append(
                f"CAPSIZE RISK: GM = {result.gm_estimate:.3f} m < {GM_MIN_YELLOW} m"
            )
            result.status = "ROJO"
        elif result.gm_estimate < GM_MIN_GREEN:
            self.alerts.append(
                f"REDUCED STABILITY: GM = {result.gm_estimate:.3f} m"
            )
            if result.status != "ROJO":
                result.status = "AMARILLO"

        # Evaluate force balance
        if abs(result.net_force) > result.total_weight * 0.05:
            direction = "weight" if result.net_force > 0 else "buoyancy"
            self.alerts.append(
                f"IMBALANCE: {abs(result.net_force)/1000:.1f} kN excess {direction}"
            )

        result.warnings = self.alerts
        return result

    def get_color_code(self, status: str) -> str:
        """ANSI color code for status."""
        from utils.constants import Colors
        color_map = {
            "VERDE": Colors.VERDE,
            "AMARILLO": Colors.AMARILLO,
            "ROJO": Colors.ROJO,
        }
        return color_map.get(status, Colors.RESET)
