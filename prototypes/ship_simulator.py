#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ship Resistance Game - Simulador de Resistencia Longitudinal del Buque
======================================================================

Simulador educativo que calcula la distribución de pesos, empuje, fuerza
cortante, momento flector y tensiones de flexión en la viga buque durante
operaciones de carga/descarga.

Permite modificar la carga y lastre por sección y recalcular dinámicamente
los diagramas de esfuerzo, alertando si se alcanza la fluencia del acero
o condiciones de pandeo.

Uso:
    python ship_simatorio.py

Requisitos:
    - Python 3.8+
    - numpy (opcional, para gráficos) / matplotlib (opcional)

El simulador funciona sin dependencias externas para cálculos.
La visualización requiere matplotlib si está disponible.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import math

# =============================================================================
# CONSTANTES Y PARÁMETROS DEL BUQUE
# =============================================================================

# Acero estructural naval (valores típicos)
STEEL_YIELD_STRESS = 235.0e6  # Pa (235 MPa para acero naval AH36)
STEEL_YOUNGS_MODULUS = 200e9  # Pa
STEEL_DENSITY = 7850.0  # kg/m^3

# Límites de seguridad
SAFETY_FACTOR_YIELD = 1.5  # Factor de seguridad para fluencia
SAFETY_FACTOR_BUCKLING = 2.0  # Factor de seguridad para pandeo
MAX_ALLOWED_STRESS = STEEL_YIELD_STRESS / SAFETY_FACTOR_YIELD  # 156.67 MPa

# Estado de mar (coeficiente de amplificación dinámica)
SEA_STATE_FACTORS = {
    0: 1.00,  # Calma
    1: 1.05,  # Marejada ligera
    2: 1.10,  # Marejada moderada
    3: 1.20,  # Marejada fuerte
    4: 1.35,  # Mar gruesa
    5: 1.50,  # Mar muy gruesa (tormenta)
}


@dataclass
class SectionConfig:
    """Configuración de una sección del buque."""
    name: str  # Nombre descriptivo de la sección
    length: float  # Longitud de la sección [m]
    weight_empty: float  # Peso en vacío (estructura) [N]
    capacity: float  # Capacidad máxima (carga + lastre) [N]
    current_load: float = 0.0  # Carga actual [N] (positivo = carga, negativo = lastre por debajo)
    is_ballast: bool = False  # True si es tanque de lastre

    @property
    def x_center(self) -> float:
        """Posición del centro de la sección (se calcula externamente)."""
        return self._x_center if hasattr(self, '_x_center') else 0.0

    @x_center.setter
    def x_center(self, value: float):
        self._x_center = value

    @property
    def total_weight(self) -> float:
        """Peso total de la sección (estructura + carga/lastre)."""
        return self.weight_empty + abs(self.current_load)

    def set_load(self, load: float) -> None:
        """Establece la carga con validación."""
        max_load = self.capacity
        if abs(load) > max_load:
            raise ValueError(
                f"Carga {load/1000:.1f} kN excede capacidad máxima {max_load/1000:.1f} kN "
                f"en sección '{self.name}'"
            )
        self.current_load = load


@dataclass
class ShipConfig:
    """Configuración completa del buque."""
    name: str
    length_overall: float  # Eslota total [m]
    beam: float  # Manga [m]
    depth: float  # Puntal [m]
    draft_design: float  # Calado de diseño [m]
    displacement: float  # Desplazamiento total [N] (peso = empuje en flotación)
    sections: List[SectionConfig] = field(default_factory=list)

    # Propiedades de la sección transversal (simplificación: caja)
    deck_breadth_ratio: float = 0.85  # Manga de cubierta / Manga total
    keel_breadth_ratio: float = 0.15  # Manga de quilla / Manga total

    # Inercia de la sección transversal (viga buque)
    moment_of_inertia_zz: float = 0.0  # I_z [m^4] (alrededor del eje horizontal)

    # Posiciones de esfuerzo
    y_deck: float = 0.0  # Distancia desde eje neutro hasta cubierta [m]
    y_keel: float = 0.0  # Distancia desde eje neutro hasta quilla [m]


@dataclass
class StressResult:
    """Resultado de tensiones en una sección."""
    x: float  # Posición longitudinal [m]
    shear_force: float  # Fuerza cortante [N]
    bending_moment: float  # Momento flector [N·m]
    stress_deck: float  # Tensión en cubierta [Pa]
    stress_keel: float  # Tensión en quilla [Pa]
    stress_max: float  # Tensión máxima [Pa]
    status: str  # "VERDE", "AMARILLO", "ROJO"


@dataclass
class SimulationResult:
    """Resultado completo de la simulación."""
    sections: List[StressResult]
    max_stress: float
    max_stress_position: float
    total_weight: float
    buoyancy: float
    net_force: float  # Peso - Empuje
    gm_estimate: float  # Estimación de GM (altura metacéntrica)
    status: str  # "VERDE", "AMARILLO", "ROJO"
    warnings: List[str]


# =============================================================================
# MOTOR DE FÍSICA
# =============================================================================

class PhysicsEngine:
    """
    Motor de física para el cálculo de resistencia longitudinal del buque.

    Implementa el método de integración numérica para obtener las curvas de
    fuerza cortante V(x) y momento flector M(x) a partir de las distribuciones
    de peso w(x) y empuje b(x).
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
        Distribución de empuje simplificada (rectángulo modificado).

        En un buque real, el empuje sigue la forma del casco. Aquí usamos
        una distribución trapezoidal que concentra más empopme en el centro.
        """
        n = len(self.ship.sections)
        total_buoyancy = self.ship.displacement

        if n == 0:
            return

        # Distribución trapezoidal: 20% en extremos, 60% central
        weights = []
        for i in range(n):
            if n == 1:
                w = 1.0
            elif i == 0 or i == n - 1:
                w = 0.2  # Extremos
            else:
                w = 0.6 / (n - 2) if n > 2 else 1.0  # Centro
            weights.append(w)

        # Normalizar y asignar
        total_w = sum(weights)
        for i, section in enumerate(self.ship.sections):
            section._buoyancy = total_buoyancy * weights[i] / total_w

    def compute_load_distribution(self) -> Tuple[List[float], List[float]]:
        """
        Calcula la distribución de carga neta (peso - empuje) por sección.

        Returns:
            (positions, loads): Listas de posiciones [m] y cargas [N]
        """
        positions = []
        loads = []

        for section in self.ship.sections:
            weight = section.total_weight
            buoyancy = getattr(section, '_buoyancy', 0.0)
            net_load = weight - buoyancy  # Positivo = hacia abajo
            positions.append(section.x_center)
            loads.append(net_load)

        return positions, loads

    def compute_shear_and_moment(self) -> SimulationResult:
        """
        Calcula fuerza cortante V(x) y momento flector M(x) por integración.

        V(x) = -∫(w - b) dx
        M(x) = -∫V(x) dx

        Usando el método de Euler con corrección de frontera.
        """
        positions, loads = self.compute_load_distribution()
        n = len(positions)

        if n == 0:
            return SimulationResult(
                sections=[], max_stress=0, max_stress_position=0,
                total_weight=0, buoyancy=0, net_force=0,
                gm_estimate=0, status="VERDE", warnings=[]
            )

        # Espaciado entre secciones
        dx = self.ship.sections[0].length

        # Integración: fuerza cortante (método del trapecio acumulativo)
        shear = [0.0] * n
        cumulative = 0.0
        for i in range(n):
            # V(i) = V(i-1) - load(i)*dx
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

        # Calcular tensiones en cada sección
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

            # Tensión de flexión: σ = M*y/I
            sigma_deck = (M * y_d) / I_zz
            sigma_keel = (M * y_k) / I_zz
            sigma_max = max(abs(sigma_deck), abs(sigma_keel))

            # Determinar estado
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

        # Calcular GM simplificado
        gm = self._estimate_gm()

        # Verificar estabilidad
        if gm < 0.15:
            warnings.append(f"GM muy bajo ({gm:.3f} m) - Riesgo de vuelco")
            status = "ROJO"
        elif gm < 0.30:
            warnings.append(f"GM bajo ({gm:.3f} m) - Estabilidad reducida")
            if status != "ROJO":
                status = "AMARILLO"

        # Peso total y empuje
        total_weight = sum(s.total_weight for s in self.ship.sections)
        total_buoyancy = sum(getattr(s, '_buoyancy', 0.0) for s in self.ship.sections)
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
        Estima la altura metacéntrica GM usando la fórmula simplificada:
        GM = KB + BM - KG

        Para una caja rectangular:
        KB ≈ T/2 (aproximación)
        BM = I / V (inercia del plano de flotación / volumen)
        KG ≈ profundidad/2 (aproximación para distribución uniforme)
        """
        T = self.ship.draft_design
        B = self.ship.beam
        L = self.ship.length_overall
        D = self.ship.depth

        KB = T / 2.0
        I_flota = (L * B**3) / 12.0  # Inercia del plano de flotación
        V = L * B * T  # Volumen de carena (aproximación caja)
        BM = I_flota / V if V > 0 else 0.0

        # KG depende de la distribución de pesos
        # Aproximación: centro de gravedad a 55% del puntal desde quilla
        KG = 0.55 * D

        GM = KB + BM - KG
        return max(GM, -0.5)  # Evitar valores extremadamente negativos


# =============================================================================
# SISTEMA DE ALERTAS
# =============================================================================

class AlertSystem:
    """Gestiona las alertas del simulador."""

    COLORS = {
        "VERDE": "\033[92m",   # Verde
        "AMARILLO": "\033[93m", # Amarillo
        "ROJO": "\033[91m",     # Rojo
        "RESET": "\033[0m",     # Reset
        "BOLD": "\033[1m",      # Negrita
    }

    @staticmethod
    def colorize(text: str, color: str) -> str:
        """Aplica color ANSI al texto."""
        return f"{AlertSystem.COLORS.get(color, '')}{text}{AlertSystem.COLORS['RESET']}"

    @staticmethod
    def print_status(result: SimulationResult) -> None:
        """Imprime el estado general de la simulación con colores."""
        status = result.status
        color = status if status in AlertSystem.COLORS else "RESET"

        print("\n" + "=" * 70)
        print(AlertSystem.colorize(f"  ESTADO GENERAL: {status}", color))
        print("=" * 70)

        for warning in result.warnings:
            print(AlertSystem.colorize(f"  ⚠  {warning}", "ROJO"))

        print(f"\n  Tensiones máximas:")
        print(f"    Posición: {result.max_stress_position:.1f} m desde proa")
        print(f"    Valor:    {result.max_stress/1e6:.2f} MPa")
        print(f"    Límite:   {MAX_ALLOWED_STRESS/1e6:.2f} MPa")
        print(f"    Factor de seguridad: {STEEL_YIELD_STRESS/result.max_stress:.2f}")

        print(f"\n  Balance de fuerzas:")
        print(f"    Peso total:  {result.total_weight/1000:.1f} kN")
        print(f"    Empuje:       {result.buoyancy/1000:.1f} kN")
        print(f"    Diferencia:   {result.net_force/1000:.1f} kN")

        print(f"\n  Estabilidad:")
        print(f"    GM estimado: {result.gm_estimate:.3f} m")

    @staticmethod
    def print_section_table(result: SimulationResult, ship: ShipConfig) -> None:
        """Imprime tabla detallada por sección."""
        print("\n" + "-" * 90)
        header = f"{'Sección':<20} {'x [m]':>8} {'V [kN]':>10} {'M [MN·m]':>10} {'σ_cubierta':>12} {'σ_quilla':>10} {'Estado':>10}"
        print(header)
        print("-" * 90)

        for i, stress in enumerate(result.sections):
            section_name = ship.sections[i].name
            status = stress.status
            color = status if status in AlertSystem.COLORS else ""

            row = (
                f"{section_name:<20} "
                f"{stress.x:>8.1f} "
                f"{stress.shear_force/1000:>10.1f} "
                f"{stress.bending_moment/1e6:>10.2f} "
                f"{stress.stress_deck/1e6:>12.1f} "
                f"{stress.stress_keel/1e6:>10.1f} "
            )

            if color:
                row += AlertSystem.colorize(f"{status:>10}", color)
            else:
                row += f"{status:>10}"

            print(row)

        print("-" * 90)


# =============================================================================
# INTERFAZ DE USUARIO (CLI)
# =============================================================================

class SimulatorUI:
    """Interfaz de usuario basada en terminal."""

    def __init__(self):
        self.ship = self._create_default_ship()
        self.engine = PhysicsEngine(self.ship)
        self.result = None

    def _create_default_ship(self) -> ShipConfig:
        """Crea un buque de ejemplo: portacontenedores de 200m."""
        ship = ShipConfig(
            name="MV Containership-200",
            length_overall=200.0,
            beam=32.0,
            depth=18.0,
            draft_design=10.0,
            displacement=45_000_000.0,  # 45,000 toneladas ≈ 45,000,000 kgf → ~441 MN
            moment_of_inertia_zz=8500.0,  # I_z [m^4] realista para buque 200m
            y_deck=8.5,  # m desde eje neutro
            y_keel=-9.0,  # m desde eje neutro
        )

        # Crear 10 secciones iguales de 20m cada una
        section_length = ship.length_overall / 10.0

        # Configuración: [nombre, peso estructural (kN), capacidad (kN), es_lastre]
        section_data = [
            ("Pico de proa",        5000,  2000, False),
            ("Proa - Carga 1",     8000, 15000, False),
            ("Proa - Carga 2",     8000, 15000, False),
            ("Tanque proa",        3000,  8000, True),
            ("Centro - Carga 1",  10000, 20000, False),
            ("Centro - Carga 2",  10000, 20000, False),
            ("Tanque centro",      2000,  5000, True),
            ("Popa - Carga 1",    10000, 20000, False),
            ("Popa - Carga 2",     8000, 15000, False),
            ("Pico de popa",       4000,  1500, False),
        ]

        for name, w_empty, cap, is_ballast in section_data:
            section = SectionConfig(
                name=name,
                length=section_length,
                weight_empty=w_empty * 1000.0,  # kN → N
                capacity=cap * 1000.0,
                is_ballast=is_ballast,
            )
            ship.sections.append(section)

        # Cargar por defecto al 60%
        for section in ship.sections:
            default_load = section.capacity * 0.6 if not section.is_ballast else section.capacity * 0.3
            section.set_load(default_load)

        return ship

    def run(self) -> None:
        """Ejecuta el bucle principal del simulador."""
        self._print_header()

        while True:
            self._print_menu()
            choice = input("\n  Opción: ").strip()

            if choice == "1":
                self._show_ship_config()
            elif choice == "2":
                self._modify_load()
            elif choice == "3":
                self._modify_ballast()
            elif choice == "4":
                self._run_simulation()
            elif choice == "5":
                self._change_sea_state()
            elif choice == "6":
                self._reset_loads()
            elif choice == "0":
                print("\n  ¡Hasta luego! Gracias por usar Ship Resistance Game.")
                break
            else:
                print(AlertSystem.colorize("\n  Opción inválida.", "AMARILLO"))

    def _print_header(self) -> None:
        """Imprime el encabezado del simulador."""
        print("\n" + "=" * 70)
        print(AlertSystem.colorize(
            "  SHIP RESISTANCE GAME v1.0",
            "BOLD"
        ))
        print("  Simulador Educativo de Resistencia Longitudinal del Buque")
        print("=" * 70)
        print(f"\n  Buque: {self.ship.name}")
        print(f"  Eslota: {self.ship.length_overall:.0f} m | "
              f"Manga: {self.ship.beam:.0f} m | "
              f"Calado: {self.ship.draft_design:.0f} m")
        print(f"  Desplazamiento: {self.ship.displacement/1e6:.1f} MN")

    def _print_menu(self) -> None:
        """Imprime el menú principal."""
        print("\n" + "-" * 40)
        print("  MENÚ PRINCIPAL")
        print("-" * 40)
        print("  1. Ver configuración del buque")
        print("  2. Modificar carga por sección")
        print("  3. Modificar lastre")
        print("  4. Ejecutar simulación")
        print("  5. Cambiar estado de mar")
        print("  6. Restablecer cargas")
        print("  0. Salir")

    def _show_ship_config(self) -> None:
        """Muestra la configuración detallada del buque."""
        print("\n" + "=" * 70)
        print("  CONFIGURACIÓN DEL BUQUE")
        print("=" * 70)
        print(f"\n  {'Sección':<20} {'Longitud':>10} {'Peso vacío':>12} {'Capacidad':>12} {'Carga actual':>14}")
        print("  " + "-" * 72)
        for section in self.ship.sections:
            load_type = "Lastre" if section.is_ballast else "Carga"
            print(
                f"  {section.name:<20} "
                f"{section.length:>8.1f} m "
                f"{section.weight_empty/1000:>10.0f} kN "
                f"{section.capacity/1000:>10.0f} kN "
                f"{section.current_load/1000:>10.0f} kN ({load_type})"
            )

    def _modify_load(self) -> None:
        """Permite modificar la carga de una sección."""
        self._show_section_list()
        try:
            idx = int(input("\n  Selecciona sección (0 para cancelar): "))
            if idx == 0:
                return
            if idx < 0 or idx >= len(self.ship.sections):
                print(AlertSystem.colorize("  Índice inválido.", "ROJO"))
                return

            section = self.ship.sections[idx]
            if section.is_ballast:
                print(AlertSystem.colorize(
                    "  Esta es una sección de lastre. Usa la opción 3.", "AMARILLO"
                ))
                return

            print(f"\n  Sección: {section.name}")
            print(f"  Capacidad máxima: {section.capacity/1000:.0f} kN")
            print(f"  Carga actual: {section.current_load/1000:.0f} kN")

            new_load = float(input("  Nueva carga (kN, 0 = vacío): "))
            section.set_load(new_load * 1000.0)
            print(AlertSystem.colorize(f"  Carga actualizada a {new_load:.0f} kN", "VERDE"))

        except ValueError as e:
            print(AlertSystem.colorize(f"  Error: {e}", "ROJO"))

    def _modify_ballast(self) -> None:
        """Permite modificar el lastre de una sección."""
        ballast_sections = [s for s in self.ship.sections if s.is_ballast]
        if not ballast_sections:
            print(AlertSystem.colorize("  No hay tanques de lastre.", "AMARILLO"))
            return

        print("\n  Tanques de lastre:")
        for i, section in enumerate(ballast_sections):
            print(f"    {i+1}. {section.name}: {section.current_load/1000:.0f} / {section.capacity/1000:.0f} kN")

        try:
            idx = int(input("\n  Selecciona tanque (0 para cancelar): "))
            if idx == 0:
                return
            if idx < 0 or idx >= len(ballast_sections):
                print(AlertSystem.colorize("  Índice inválido.", "ROJO"))
                return

            section = ballast_sections[idx]
            print(f"\n  Sección: {section.name}")
            print(f"  Capacidad: {section.capacity/1000:.0f} kN")
            print(f"  Lastre actual: {section.current_load/1000:.0f} kN")

            new_load = float(input("  Nuevo lastre (kN, 0 = vacío): "))
            section.set_load(new_load * 1000.0)
            print(AlertSystem.colorize(f"  Lastre actualizado a {new_load:.0f} kN", "VERDE"))

        except ValueError as e:
            print(AlertSystem.colorize(f"  Error: {e}", "ROJO"))

    def _run_simulation(self) -> None:
        """Ejecuta la simulación y muestra resultados."""
        self.result = self.engine.compute_shear_and_moment()
        AlertSystem.print_status(self.result)
        AlertSystem.print_section_table(self.result, self.ship)

        # Intentar mostrar gráficos si matplotlib está disponible
        self._try_plot_results()

    def _change_sea_state(self) -> None:
        """Cambia el estado de mar (afecta amplificación dinámica)."""
        print("\n  Estados de mar disponibles:")
        for state, factor in SEA_STATE_FACTORS.items():
            desc = ["Calma", "Marejada ligera", "Marejada moderada",
                    "Marejada fuerte", "Mar gruesa", "Mar muy gruesa"][state]
            print(f"    {state}: {desc} (×{factor:.2f})")

        try:
            choice = int(input("\n  Selecciona estado de mar: "))
            if choice not in SEA_STATE_FACTORS:
                raise ValueError("Estado inválido")
            self._sea_state = choice
            print(AlertSystem.colorize(
                f"  Estado de mar actualizado a {choice}", "VERDE"
            ))
            # Nota: en una versión completa, el factor de mar se aplicaría
            # al cálculo de momento flector como M_dinámico = M_estático × factor
        except ValueError as e:
            print(AlertSystem.colorize(f"  Error: {e}", "ROJO"))

    def _reset_loads(self) -> None:
        """Restablece todas las cargas a sus valores por defecto."""
        for section in self.ship.sections:
            if section.is_ballast:
                section.set_load(section.capacity * 0.3)
            else:
                section.set_load(section.capacity * 0.6)
        print(AlertSystem.colorize("  Cargas restablecidas a valores por defecto.", "VERDE"))

    def _show_section_list(self) -> None:
        """Muestra la lista de secciones con sus índices."""
        print("\n  Secciones disponibles:")
        for i, section in enumerate(self.ship.sections):
            load_type = "[L]" if section.is_ballast else "[C]"
            print(f"    {i+1:2d}. {load_type} {section.name:<20} "
                  f"Carga: {section.current_load/1000:>8.0f} kN")

    def _try_plot_results(self) -> None:
        """Intenta graficar los resultados usando matplotlib."""
        if self.result is None:
            return

        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            print("\n  (matplotlib no disponible - omitiendo gráficos)")
            print("  Instala con: pip install matplotlib numpy")
            return

        if not self.result.sections:
            return

        x = [s.x for s in self.result.sections]
        shear = [s.shear_force / 1000.0 for s in self.result.sections]  # kN
        moment = [s.bending_moment / 1e6 for s in self.result.sections]  # MN·m
        stress_deck = [s.stress_deck / 1e6 for s in self.result.sections]  # MPa
        stress_keel = [abs(s.stress_keel) / 1e6 for s in self.result.sections]  # MPa

        fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
        fig.suptitle(f"Simulación: {self.ship.name} — Estado: {self.result.status}",
                     fontsize=14, fontweight='bold')

        # Diagrama de fuerza cortante
        ax = axes[0]
        ax.fill_between(x, shear, alpha=0.3, color='steelblue')
        ax.plot(x, shear, 'b-', linewidth=1.5)
        ax.axhline(y=0, color='k', linewidth=0.5)
        ax.set_ylabel('V(x) [kN]')
        ax.set_title('Diagrama de Fuerza Cortante')
        ax.grid(True, alpha=0.3)

        # Diagrama de momento flector
        ax = axes[1]
        ax.fill_between(x, moment, alpha=0.3, color='darkorange')
        ax.plot(x, moment, 'r-', linewidth=1.5)
        ax.axhline(y=0, color='k', linewidth=0.5)
        ax.set_ylabel('M(x) [MN·m]')
        ax.set_title('Diagrama de Momento Flector')
        ax.grid(True, alpha=0.3)

        # Tensiones
        ax = axes[2]
        ax.plot(x, stress_deck, 'g-', linewidth=1.5, label='Cubierta (σ)')
        ax.plot(x, stress_keel, 'm-', linewidth=1.5, label='Quilla (σ)')
        ax.axhline(y=MAX_ALLOWED_STRESS/1e6, color='r', linestyle='--',
                    linewidth=1.5, label=f'Límite ({MAX_ALLOWED_STRESS/1e6:.1f} MPa)')
        ax.axhline(y=-MAX_ALLOWED_STRESS/1e6, color='r', linestyle='--', linewidth=1.5)
        ax.axhline(y=0, color='k', linewidth=0.5)
        ax.set_ylabel('σ [MPa]')
        ax.set_xlabel('x [m] (desde proa)')
        ax.set_title('Tensiones de Flexión en la Viga Buque')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)

        # Colorear zonas de tensión
        ax.axhspan(MAX_ALLOWED_STRESS/1e6, max(stress_deck)*1.1,
                    alpha=0.1, color='red', label='Zona ROJA')
        ax.axhspan(MAX_ALLOWED_STRESS/1e6*0.75, MAX_ALLOWED_STRESS/1e6,
                    alpha=0.1, color='yellow', label='Zona AMARILLA')
        ax.axhspan(-MAX_ALLOWED_STRESS/1e6*0.75, MAX_ALLOWED_STRESS/1e6*0.75,
                    alpha=0.1, color='green', label='Zona VERDE')

        plt.tight_layout()
        plt.savefig('simulation_results.png', dpi=150, bbox_inches='tight')
        print("\n  Gráfico guardado en: simulation_results.png")
        plt.show()


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

def main():
    """Función principal del simulador."""
    try:
        ui = SimulatorUI()
        ui.run()
    except KeyboardInterrupt:
        print("\n\n  Simulación cancelada por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\n  Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
