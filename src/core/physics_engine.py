"""
physics_engine.py — Motor de física para resistencia longitudinal
=================================================================

Implementa el cálculo de fuerza cortante V(x), momento flector M(x)
y tensiones de flexión σ(x) para un buque dividido en secciones discretas.

Teoría basada en:
- Método de integración numérica (trapecio)
- Teoría de Euler-Bernoulli para vigas flotantes
- Criterio de fluencia para acero naval
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
    Motor de física para el cálculo de resistencia longitudinal del buque.

    Calcula las distribuciones de:
    - Carga neta q(x) = w(x) - b(x)
    - Fuerza cortante V(x) = -∫q(x)dx
    - Momento flector M(x) = -∫V(x)dx
    - Tensiones de flexión σ(x) = M(x)·y/I_z
    """

    def __init__(self, ship: ShipConfig):
        self.ship = ship
        self._compute_section_positions()
        self._compute_buoyancy_distribution()

    def _compute_section_positions(self) -> None:
        """Calcula la posición del centro de cada sección."""
        x = 0.0
        for section in self.ship.sections:
            section.x_center = x + section.length / 2.0
            x += section.length

    def _compute_buoyancy_distribution(self) -> None:
        """
        Distribución de empuje trapezoidal simplificada.
        20% en extremos, 60% en centro.
        El empuje total iguala el peso total (equilibrio estático).
        """
        n = len(self.ship.sections)
        # El empuje total debe igualar el peso total del buque (Arquímedes)
        total_weight = sum(s.total_weight for s in self.ship.sections)
        total_buoyancy = total_weight  # Equilibrio estático

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
        """Calcula la distribución de carga neta (peso - empuje) por sección."""
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
        Calcula V(x), M(x) y tensiones por integración numérica.

        Returns:
            SimulationResult con todos los resultados y estado de seguridad.
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

        # Integración: fuerza cortante
        shear = [0.0] * n
        for i in range(n):
            if i > 0:
                shear[i] = shear[i - 1] - loads[i] * dx
            else:
                shear[i] = -loads[i] * dx

        # Integración: momento flector
        moment = [0.0] * n
        for i in range(n):
            if i == 0:
                moment[i] = shear[i] * dx
            else:
                moment[i] = moment[i - 1] + shear[i] * dx

        # Aplicar factor de estado de mar (amplificación dinámica)
        moment = [m * sea_factor for m in moment]

        # Calcular tensiones
        I_zz = self.ship.moment_of_inertia_zz
        y_d = self.ship.y_deck
        y_k = self.ship.y_keel

        if I_zz <= 0:
            raise ValueError("Momento de inercia I_z no configurado o inválido")

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

            # Determinar estado semafórico
            if sigma_max > MAX_ALLOWED_STRESS:
                section_status = "ROJO"
                status = "ROJO"
                warnings.append(
                    f"¡FLUENCIA! Sección '{self.ship.sections[i].name}' "
                    f"en x={positions[i]:.1f} m: σ={sigma_max/1e6:.1f} MPa "
                    f"> límite {MAX_ALLOWED_STRESS/1e6:.1f} MPa"
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

        # Estabilidad
        gm = self._estimate_gm()

        if gm < 0.15:
            warnings.append(f"GM muy bajo ({gm:.3f} m) — Riesgo de vuelco")
            status = "ROJO"
        elif gm < 0.30:
            warnings.append(f"GM bajo ({gm:.3f} m) — Estabilidad reducida")
            if status != "ROJO":
                status = "AMARILLO"

        # Balance de fuerzas
        total_weight = sum(s.total_weight for s in self.ship.sections)
        total_buoyancy = sum(s._buoyancy for s in self.ship.sections)
        net_force = total_weight - total_buoyancy

        if abs(net_force) > total_weight * 0.05:
            warnings.append(
                f"Desbalance de fuerzas: {net_force/1000:.1f} kN "
                f"({'exceso de peso' if net_force > 0 else 'exceso de empuje'})"
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
        Estima la altura metacéntrica GM.
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
        # KG más conservador: el centro de gravedad suele ser más alto
        # cuando hay carga pesada en cubierta
        KG = 0.62 * D

        GM = KB + BM - KG
        return max(GM, -0.5)
