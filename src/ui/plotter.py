"""
plotter.py — Stress diagram rendering
=====================================

Generates plots for:
- Shear force V(x)
- Bending moment M(x)
- Bending stress σ(x)

Requires matplotlib and numpy.
"""

from __future__ import annotations

from typing import Optional

from models.simulation_result import SimulationResult
from models.ship_config import ShipConfig
from utils.constants import MAX_ALLOWED_STRESS


def plot_results(result: SimulationResult, ship: ShipConfig,
                 save_path: Optional[str] = None) -> None:
    """
    Generates and displays (or saves) stress diagrams.

    Args:
        result: Simulation result.
        ship: Ship configuration.
        save_path: If specified, saves the plot to this path.
    """
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("(matplotlib not available — skipping plots)")
        print("Install with: pip install matplotlib numpy")
        return

    if not result.sections:
        return

    x = [s.x for s in result.sections]
    shear = [s.shear_force / 1000.0 for s in result.sections]
    moment = [s.bending_moment / 1e6 for s in result.sections]
    stress_deck = [s.stress_deck / 1e6 for s in result.sections]
    stress_keel = [abs(s.stress_keel) / 1e6 for s in result.sections]

    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    fig.suptitle(f"Simulation: {ship.name} — Status: {result.status}",
                 fontsize=14, fontweight='bold')

    # Shear force diagram
    ax = axes[0]
    ax.fill_between(x, shear, alpha=0.3, color='steelblue')
    ax.plot(x, shear, 'b-', linewidth=1.5)
    ax.axhline(y=0, color='k', linewidth=0.5)
    ax.set_ylabel('V(x) [kN]')
    ax.set_title('Shear Force Diagram')
    ax.grid(True, alpha=0.3)

    # Bending moment diagram
    ax = axes[1]
    ax.fill_between(x, moment, alpha=0.3, color='darkorange')
    ax.plot(x, moment, 'r-', linewidth=1.5)
    ax.axhline(y=0, color='k', linewidth=0.5)
    ax.set_ylabel('M(x) [MN·m]')
    ax.set_title('Bending Moment Diagram')
    ax.grid(True, alpha=0.3)

    # Stresses
    ax = axes[2]
    ax.plot(x, stress_deck, 'g-', linewidth=1.5, label='Deck (σ)')
    ax.plot(x, stress_keel, 'm-', linewidth=1.5, label='Keel (σ)')
    ax.axhline(y=MAX_ALLOWED_STRESS/1e6, color='r', linestyle='--',
                linewidth=1.5, label=f'Limit ({MAX_ALLOWED_STRESS/1e6:.1f} MPa)')
    ax.axhline(y=-MAX_ALLOWED_STRESS/1e6, color='r', linestyle='--', linewidth=1.5)
    ax.axhline(y=0, color='k', linewidth=0.5)

    # Color zones
    max_stress_val = max(max(stress_deck), max(stress_keel)) * 1.1
    ax.axhspan(MAX_ALLOWED_STRESS/1e6, max_stress_val,
                alpha=0.1, color='red', label='RED zone')
    ax.axhspan(MAX_ALLOWED_STRESS/1e6*0.75, MAX_ALLOWED_STRESS/1e6,
                alpha=0.1, color='yellow', label='YELLOW zone')
    ax.axhspan(-MAX_ALLOWED_STRESS/1e6*0.75, MAX_ALLOWED_STRESS/1e6*0.75,
                alpha=0.1, color='green', label='GREEN zone')

    ax.set_ylabel('σ [MPa]')
    ax.set_xlabel('x [m] (from bow)')
    ax.set_title('Bending Stress on Ship Beam')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"\nPlot saved to: {save_path}")
    else:
        plt.show()
