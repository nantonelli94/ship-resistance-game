"""
physics_engine.py — Physics engine for longitudinal strength
=================================================================

Implements the calculation of shear force V(x), bending moment M(x)
and bending stresses σ(x) for a ship divided into discrete sections.

Theory based on:
- Numerical integration method (trapezoidal)
- Euler-Bernoulli beam theory for floating beams
- Yield criterion for marine steel
"""

from __future__ import annotations

from typing import List, Tuple

from models.ship_config import ShipConfig
from models.simulation_result import StressResult, SimulationResult
from utils.constants import (
    MAX_ALLOWED_STRESS,
    SAFETY_FACTOR_YIELD,
    SEA_STATE_FACTORS,
    STEEL_YIELD_STRESS,
)


class PhysicsEngine:
    """
    Physics engine for longitudinal ship strength calculation.

    Calculates distributions of:
    - Net load q(x) = w(x) - b(x)
    - Shear force V(x) = -∫q(x)dx
    - Bending moment M(x) = -∫V(x)dx
    - Bending stresses σ(x) = M(x)·y/I_z
    """

    def __init__(self, ship: ShipConfig):
        self.ship = ship
        self._compute_section_positions()
        self._compute_buoyancy_distribution()

    def _compute_section_positions(self) -> None:
        """Calculates the center position of each section."""
        x = 0.0
        for section in self.ship.sections:
            section.x_center = x + section.length / 2.0
            x += section.length

    def _compute_buoyancy_distribution(self) -> None:
        """
        Simplified trapezoidal buoyancy distribution.
        20% at ends, 60% at center.
        Total buoyancy equals total weight (static equilibrium).
        """
        n = len(self.ship.sections)
        # Total buoyancy must equal total weight of the ship (Archimedes' principle)
        total_weight = sum(s.total_weight for s in self.ship.sections)
        total_buoyancy = total_weight  # Static equilibrium

        if n == 0:
            return

        weights = []
        for i in range(n):
            if n == 1:
                w = 1.0
            elif i == 0 or i == n - 1:
                w = 0.2
            else:
                w = 0.6 / (n - 2) if n > 2 else 1.0
            weights.append(w)

        total_w = sum(weights)
        for i, section in enumerate(self.ship.sections):
            section._buoyancy = total_buoyancy * weights[i] / total_w

    def compute_load_distribution(self) -> Tuple[List[float], List[float]]:
        """Calculates the net load distribution (weight - buoyancy) per section."""
        positions = []
        loads = []

        for section in self.ship.sections:
            weight = section.total_weight
            buoyancy = section._buoyancy
            net_load = weight - buoyancy
            positions.append(section.x_center)
            loads.append(net_load)

        return positions, loads

    def compute_shear_and_moment(self) -> SimulationResult:
        """
        Calculates V(x), M(x) and stresses by numerical integration.

        Returns:
            SimulationResult with all results and safety status.
        """
        positions, loads = self.compute_load_distribution()
        n = len(positions)

        if n == 0:
            return SimulationResult(
                sections=[], max_stress=0, max_stress_position=0,
                total_weight=0, buoyancy=0, net_force=0,
                gm_estimate=0, status="VERDE", warnings=[]
            )

        dx = self.ship.sections[0].length
        sea_factor = SEA_STATE_FACTORS.get(self.ship.sea_state, 1.0)

        # Integration: shear force
        shear = [0.0] * n
        for i in range(n):
            if i > 0:
                shear[i] = shear[i - 1] - loads[i] * dx
            else:
                shear[i] = -loads[i] * dx

        # Integration: bending moment
        moment = [0.0] * n
        for i in range(n):
            if i == 0:
                moment[i] = shear[i] * dx
            else:
                moment[i] = moment[i - 1] + shear[i] * dx

        # Apply sea state factor (dynamic amplification)
        moment = [m * sea_factor for m in moment]

        # Calculate stresses
        I_zz = self.ship.moment_of_inertia_zz
        y_d = self.ship.y_deck
        y_k = self.ship.y_keel

        if I_zz <= 0:
            raise ValueError("Moment of inertia I_z not configured or invalid")

        stress_results = []
        max_stress = 0.0
        max_stress_pos = 0.0
        warnings = []
        status = "VERDE"

        for i in range(n):
            M = moment[i]
            V = shear[i]

            sigma_deck = (M * y_d) / I_zz
            sigma_keel = (M * y_k) / I_zz
            sigma_max = max(abs(sigma_deck), abs(sigma_keel))

            # Determine traffic light status
            if sigma_max > MAX_ALLOWED_STRESS:
                section_status = "ROJO"
                status = "ROJO"
                warnings.append(
                    f"YIELD! Section '{self.ship.sections[i].name}' "
                    f"at x={positions[i]:.1f} m: σ={sigma_max/1e6:.1f} MPa "
                    f"> limit {MAX_ALLOWED_STRESS/1e6:.1f} MPa"
                )
            elif sigma_max > MAX_ALLOWED_STRESS * 0.75:
                section_status = "AMARILLO"
                if status != "ROJO":
                    status = "AMARILLO"
            else:
                section_status = "VERDE"

            if sigma_max > max_stress:
                max_stress = sigma_max
                max_stress_pos = positions[i]

            stress_results.append(StressResult(
                x=positions[i],
                shear_force=V,
                bending_moment=M,
                stress_deck=sigma_deck,
                stress_keel=sigma_keel,
                stress_max=sigma_max,
                status=section_status
            ))

        # Stability
        gm = self._estimate_gm()

        if gm < 0.15:
            warnings.append(f"Very low GM ({gm:.3f} m) — Risk of capsizing")
            status = "ROJO"
        elif gm < 0.30:
            warnings.append(f"Low GM ({gm:.3f} m) — Reduced stability")
            if status != "ROJO":
                status = "AMARILLO"

        # Force balance
        total_weight = sum(s.total_weight for s in self.ship.sections)
        total_buoyancy = sum(s._buoyancy for s in self.ship.sections)
        net_force = total_weight - total_buoyancy

        if abs(net_force) > total_weight * 0.05:
            warnings.append(
                f"Force imbalance: {net_force/1000:.1f} kN "
                f"({'excess weight' if net_force > 0 else 'excess buoyancy'})"
            )

        return SimulationResult(
            sections=stress_results,
            max_stress=max_stress,
            max_stress_position=max_stress_pos,
            total_weight=total_weight,
            buoyancy=total_buoyancy,
            net_force=net_force,
            gm_estimate=gm,
            status=status,
            warnings=warnings
        )

    def _estimate_gm(self) -> float:
        """
        Estimates the metacentric height GM.
        GM = KB + BM - KG
        """
        T = self.ship.draft_design
        B = self.ship.beam
        L = self.ship.length_overall
        D = self.ship.depth

        KB = T / 2.0
        I_flota = (L * B**3) / 12.0
        V = L * B * T
        BM = I_flota / V if V > 0 else 0.0
        # More conservative KG: center of gravity is usually higher
        # when there is heavy cargo on deck
        KG = 0.62 * D

        GM = KB + BM - KG
        return max(GM, -0.5)