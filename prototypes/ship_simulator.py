#!/usr/bin/env python3
"""
ship_simulator.py — Quick Demo CLI
===================================

Legacy CLI prototype for quick testing. For the full interactive experience:
    streamlit run app.py

This file runs a demo simulation and prints results to the console.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from data.ship_presets import get_ship_preset
from core.physics_engine import PhysicsEngine
from core.alert_system import AlertSystem


def main():
    """Run a quick demo simulation."""
    print("⚓ Ship Resistance Game — Quick Demo")
    print("=" * 50)
    print("For the full interactive app, run: streamlit run app.py")
    print("=" * 50)

    ship = get_ship_preset("containership")
    engine = PhysicsEngine(ship)
    alert_sys = AlertSystem()

    result = engine.compute_shear_and_moment()
    result = alert_sys.evaluate(result)

    print(f"\nShip: {ship.name}")
    print(f"Length: {ship.length_overall:.0f} m | Beam: {ship.beam:.0f} m | Draft: {ship.draft_design:.0f} m")
    print(f"\nStatus: {result.status}")
    print(f"Max Stress: {result.max_stress/1e6:.2f} MPa")
    print(f"Max Bending Moment: {max(abs(s.bending_moment) for s in result.sections)/1e6:.2f} MN·m")
    print(f"GM (stability): {result.gm_estimate:.3f} m")

    if result.warnings:
        print("\n⚠️  Alerts:")
        for w in result.warnings:
            print(f"  • {w}")
    else:
        print("\n✅ All systems within safe limits!")


if __name__ == "__main__":
    main()
