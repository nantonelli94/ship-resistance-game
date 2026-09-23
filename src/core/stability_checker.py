"""
stability_checker.py — Transverse stability checker
===================================================

Computes the metacentric height GM and verifies stability criteria
according to IMO recommendations.
"""

from __future__ import annotations

from models.ship_config import ShipConfig
from utils.constants import GM_MIN_GREEN, GM_MIN_YELLOW


class StabilityChecker:
    """Checks the ship's transverse stability."""

    def __init__(self, ship: ShipConfig):
        self.ship = ship

    def compute_gm(self) -> float:
        """Metacentric height GM = KB + BM - KG."""
        T = self.ship.draft_design
        B = self.ship.beam
        L = self.ship.length_overall
        D = self.ship.depth

        KB = T / 2.0
        I_flota = (L * B**3) / 12.0
        V = L * B * T
        BM = I_flota / V if V > 0 else 0.0
        KG = 0.55 * D

        return max(KB + BM - KG, -0.5)

    def get_stability_status(self) -> str:
        """Stability status: VERDE, AMARILLO or ROJO."""
        gm = self.compute_gm()

        if gm < GM_MIN_YELLOW:
            return "ROJO"
        elif gm < GM_MIN_GREEN:
            return "AMARILLO"
        else:
            return "VERDE"

    def compute_righting_arm(self, heel_angle_deg: float) -> float:
        """
        Righting arm GZ for a heel angle.
        Simplification: GZ = GM * sin(θ) for small angles.
        """
        import math
        gm = self.compute_gm()
        theta_rad = math.radians(heel_angle_deg)
        return gm * math.sin(theta_rad)

    def check_imo_criteria(self) -> dict:
        """
        Checks basic IMO stability criteria.
        """
        gm = self.compute_gm()
        criteria = {}

        # Criteria 1: GM >= 0.15 m
        criteria["GM_min"] = {
            "value": gm,
            "required": 0.15,
            "pass": gm >= 0.15
        }

        # Criteria 2: GZ_max >= 0.20 m
        gz_max = self.compute_righting_arm(30)
        criteria["GZ_max"] = {
            "value": gz_max,
            "required": 0.20,
            "pass": gz_max >= 0.20
        }

        # Criteria 3: Area 0-30° >= 0.055 m·rad
        area = self._approx_area_0_30()
        criteria["Area_0_30"] = {
            "value": area,
            "required": 0.055,
            "pass": area >= 0.055
        }

        return criteria

    def _approx_area_0_30(self) -> float:
        """Approximation of the area under the GZ curve from 0° to 30°."""
        import math
        # Numerical integration (trapezoidal) of GZ(θ) from 0° to 30°
        n_steps = 10
        theta_max = math.radians(30)
        d_theta = theta_max / n_steps

        area = 0.0
        for i in range(n_steps):
            theta1 = i * d_theta
            theta2 = (i + 1) * d_theta
            gz1 = self.compute_righting_arm(math.degrees(theta1))
            gz2 = self.compute_righting_arm(math.degrees(theta2))
            area += (gz1 + gz2) / 2.0 * d_theta

        return area
