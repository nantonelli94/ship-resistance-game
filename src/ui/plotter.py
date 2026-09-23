"""
plotter.py — Renderizado de diagramas de esfuerzo
==================================================

Genera gráficos de:
- Fuerza cortante V(x)
- Momento flector M(x)
- Tensiones de flexión σ(x)

Requiere matplotlib y numpy.
"""

from __future__ import annotations

from typing import Optional

from models.simulation_result import SimulationResult
from models.ship_config import ShipConfig
from utils.constants import MAX_ALLOWED_STRESS


def plot_results(result: SimulationResult, ship: ShipConfig,
                 save_path: Optional[str] = None) -> None:
    """
    Genera y muestra (o guarda) los diagramas de esfuerzo.

    Args:
        result: Resultado de la simulación.
        ship: Configuración del buque.
        save_path: Si se especifica, guarda el gráfico en esa ruta.
    """
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("(matplotlib no disponible — omitiendo gráficos)")
        print("Instala con: pip install matplotlib numpy")
        return

    if not result.sections:
        return

    x = [s.x for s in result.sections]
    shear = [s.shear_force / 1000.0 for s in result.sections]
    moment = [s.bending_moment / 1e6 for s in result.sections]
    stress_deck = [s.stress_deck / 1e6 for s in result.sections]
    stress_keel = [abs(s.stress_keel) / 1e6 for s in result.sections]

    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    fig.suptitle(f"Simulación: {ship.name} — Estado: {result.status}",
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

    # Zonas de color
    max_stress_val = max(max(stress_deck), max(stress_keel)) * 1.1
    ax.axhspan(MAX_ALLOWED_STRESS/1e6, max_stress_val,
                alpha=0.1, color='red', label='Zona ROJA')
    ax.axhspan(MAX_ALLOWED_STRESS/1e6*0.75, MAX_ALLOWED_STRESS/1e6,
                alpha=0.1, color='yellow', label='Zona AMARILLA')
    ax.axhspan(-MAX_ALLOWED_STRESS/1e6*0.75, MAX_ALLOWED_STRESS/1e6*0.75,
                alpha=0.1, color='green', label='Zona VERDE')

    ax.set_ylabel('σ [MPa]')
    ax.set_xlabel('x [m] (desde proa)')
    ax.set_title('Tensiones de Flexión en la Viga Buque')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"\nGráfico guardado en: {save_path}")
    else:
        plt.show()
