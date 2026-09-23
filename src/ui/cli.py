"""
cli.py — Interfaz de línea de comandos del simulador
====================================================

Proporciona un menú interactivo para operar el simulador.
"""

from __future__ import annotations

import sys
from typing import Optional

import sys
import os

# Añadir src al path para imports absolutos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.physics_engine import PhysicsEngine
from core.load_manager import LoadManager
from core.alert_system import AlertSystem
from models.ship_config import ShipConfig
from ui.plotter import plot_results
from utils.constants import (
    Colors, MAX_ALLOWED_STRESS, SEA_STATE_FACTORS, SEA_STATE_DESCRIPTIONS
)
from data.ship_presets import get_ship_preset


class SimulatorCLI:
    """Interfaz de línea de comandos del simulador."""

    def __init__(self, ship: Optional[ShipConfig] = None):
        if ship is None:
            ship = get_ship_preset("containership")
        self.ship = ship
        self.engine = PhysicsEngine(ship)
        self.load_manager = LoadManager(ship)
        self.alert_system = AlertSystem()
        self.result = None

    def run(self) -> None:
        """Bucle principal del simulador."""
        self._print_header()

        while True:
            self._print_menu()
            choice = input("\n  Opción: ").strip()

            actions = {
                "1": self._show_ship_config,
                "2": self._modify_load,
                "3": self._modify_ballast,
                "4": self._run_simulation,
                "5": self._change_sea_state,
                "6": self._reset_loads,
                "7": self._change_ship_preset,
                "0": self._exit,
            }

            action = actions.get(choice)
            if action:
                action()
            else:
                print(Colors.colorize("\n  Opción inválida.", "AMARILLO"))

    def _print_header(self) -> None:
        print("\n" + "=" * 70)
        print(Colors.colorize("  SHIP RESISTANCE GAME v1.0", "BOLD"))
        print("  Simulador Educativo de Resistencia Longitudinal del Buque")
        print("=" * 70)
        print(f"\n  Buque: {self.ship.name}")
        print(f"  Eslota: {self.ship.length_overall:.0f} m | "
              f"Manga: {self.ship.beam:.0f} m | "
              f"Calado: {self.ship.draft_design:.0f} m")
        print(f"  Desplazamiento: {self.ship.displacement/1e6:.1f} MN")

    def _print_menu(self) -> None:
        print("\n" + "-" * 40)
        print("  MENÚ PRINCIPAL")
        print("-" * 40)
        print("  1. Ver configuración del buque")
        print("  2. Modificar carga por sección")
        print("  3. Modificar lastre")
        print("  4. Ejecutar simulación")
        print("  5. Cambiar estado de mar")
        print("  6. Restablecer cargas")
        print("  7. Cambiar buque (preset)")
        print("  0. Salir")

    def _show_ship_config(self) -> None:
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
        cargo_sections = self.load_manager.get_cargo_sections()
        if not cargo_sections:
            print(Colors.colorize("  No hay secciones de carga.", "AMARILLO"))
            return

        print("\n  Secciones de carga:")
        for i, section in enumerate(cargo_sections):
            print(f"    {i+1}. {section.name}: {section.current_load/1000:.0f} / "
                  f"{section.capacity/1000:.0f} kN")

        try:
            idx = int(input("\n  Selecciona sección (0 para cancelar): "))
            if idx == 0:
                return
            if idx < 1 or idx > len(cargo_sections):
                raise IndexError("Índice fuera de rango")

            section = cargo_sections[idx - 1]
            print(f"\n  Sección: {section.name}")
            print(f"  Capacidad máxima: {section.capacity/1000:.0f} kN")
            print(f"  Carga actual: {section.current_load/1000:.0f} kN")

            new_load = float(input("  Nueva carga (kN, 0 = vacío): "))
            section.set_load(new_load * 1000.0)
            print(Colors.colorize(f"  Carga actualizada a {new_load:.0f} kN", "VERDE"))

        except (ValueError, IndexError) as e:
            print(Colors.colorize(f"  Error: {e}", "ROJO"))

    def _modify_ballast(self) -> None:
        ballast_sections = self.load_manager.get_ballast_sections()
        if not ballast_sections:
            print(Colors.colorize("  No hay tanques de lastre.", "AMARILLO"))
            return

        print("\n  Tanques de lastre:")
        for i, section in enumerate(ballast_sections):
            print(f"    {i+1}. {section.name}: {section.current_load/1000:.0f} / "
                  f"{section.capacity/1000:.0f} kN")

        try:
            idx = int(input("\n  Selecciona tanque (0 para cancelar): "))
            if idx == 0:
                return
            if idx < 1 or idx > len(ballast_sections):
                raise IndexError("Índice fuera de rango")

            section = ballast_sections[idx - 1]
            print(f"\n  Sección: {section.name}")
            print(f"  Capacidad: {section.capacity/1000:.0f} kN")

            new_load = float(input("  Nuevo lastre (kN, 0 = vacío): "))
            section.set_load(new_load * 1000.0)
            print(Colors.colorize(f"  Lastre actualizado a {new_load:.0f} kN", "VERDE"))

        except (ValueError, IndexError) as e:
            print(Colors.colorize(f"  Error: {e}", "ROJO"))

    def _run_simulation(self) -> None:
        self.result = self.engine.compute_shear_and_moment()
        self.result = self.alert_system.evaluate(self.result)

        AlertSystem.print_status(self.result)
        AlertSystem.print_section_table(self.result, self.ship)

        # Intentar graficar
        try:
            plot_results(self.result, self.ship)
        except Exception:
            pass

    def _change_sea_state(self) -> None:
        print("\n  Estados de mar disponibles:")
        for state, desc in SEA_STATE_DESCRIPTIONS.items():
            factor = SEA_STATE_FACTORS[state]
            marker = " ← actual" if state == self.ship.sea_state else ""
            print(f"    {state}: {desc} (×{factor:.2f}){marker}")

        try:
            choice = int(input("\n  Selecciona estado de mar: "))
            if choice not in SEA_STATE_FACTORS:
                raise ValueError("Estado inválido")
            self.ship.sea_state = choice
            print(Colors.colorize(
                f"  Estado de mar actualizado a {choice}", "VERDE"
            ))
        except (ValueError, KeyError) as e:
            print(Colors.colorize(f"  Error: {e}", "ROJO"))

    def _reset_loads(self) -> None:
        self.load_manager.reset_all_loads()
        print(Colors.colorize("  Cargas restablecidas a valores por defecto.", "VERDE"))

    def _change_ship_preset(self) -> None:
        from ..data.ship_presets import SHIP_PRESETS
        print("\n  Buques disponibles:")
        for i, (key, _) in enumerate(SHIP_PRESETS.items()):
            print(f"    {i+1}. {key}")

        try:
            choice = int(input("\n  Selecciona buque (0 para cancelar): "))
            if choice == 0:
                return
            keys = list(SHIP_PRESETS.keys())
            if choice < 1 or choice > len(keys):
                raise IndexError("Selección inválida")

            key = keys[choice - 1]
            self.ship = get_ship_preset(key)
            self.engine = PhysicsEngine(self.ship)
            self.load_manager = LoadManager(self.ship)
            print(Colors.colorize(f"  Buque cambiado a: {self.ship.name}", "VERDE"))
        except (ValueError, IndexError) as e:
            print(Colors.colorize(f"  Error: {e}", "ROJO"))

    def _exit(self) -> None:
        print("\n  ¡Hasta luego! Gracias por usar Ship Resistance Game.")
        sys.exit(0)


def main():
    """Punto de entrada de la CLI."""
    try:
        cli = SimulatorCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\n  Simulación cancelada por el usuario.")
        sys.exit(0)


if __name__ == "__main__":
    main()
