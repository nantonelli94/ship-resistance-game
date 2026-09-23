"""
ship_presets.py — Predefined ship configurations
===============================================

Defines typical ship configurations for the simulator.
"""

from __future__ import annotations

from models.ship_config import ShipConfig, SectionConfig


def create_containership_200() -> ShipConfig:
    """200m container ship."""
    ship = ShipConfig(
        name="MV Containership-200",
        length_overall=200.0,
        beam=32.0,
        depth=18.0,
        draft_design=10.0,
        displacement=45_000_000.0,
        moment_of_inertia_zz=8500.0,  # Realistic I_z for 200m x 32m x 18m ship
        y_deck=8.5,
        y_keel=-9.0,
    )

    section_length = 20.0
    section_data = [
        ("Bow peak", 5000, 2000, False),
        ("Forward cargo 1", 8000, 15000, False),
        ("Forward cargo 2", 8000, 15000, False),
        ("Forward tank", 3000, 8000, True),
        ("Mid cargo 1", 10000, 20000, False),
        ("Mid cargo 2", 10000, 20000, False),
        ("Mid tank", 2000, 5000, True),
        ("Aft cargo 1", 10000, 20000, False),
        ("Aft cargo 2", 8000, 15000, False),
        ("Stern peak", 4000, 1500, False),
    ]

    for name, w_empty, cap, is_ballast in section_data:
        ship.sections.append(SectionConfig(
            name=name, length=section_length,
            weight_empty=w_empty * 1000.0,
            capacity=cap * 1000.0,
            is_ballast=is_ballast,
        ))

    # Default loads
    for section in ship.sections:
        factor = 0.3 if section.is_ballast else 0.6
        section.set_load(section.capacity * factor)

    return ship


def create_bulk_carrier_250() -> ShipConfig:
    """250m bulk carrier."""
    ship = ShipConfig(
        name="MV BulkCarrier-250",
        length_overall=250.0,
        beam=40.0,
        depth=20.0,
        draft_design=12.0,
        displacement=80_000_000.0,
        moment_of_inertia_zz=22000.0,  # Realistic for 250m bulk carrier
        y_deck=9.5,
        y_keel=-10.5,
    )

    section_length = 25.0
    section_data = [
        ("Bow peak", 8000, 3000, False),
        ("Fwd hold 1", 12000, 25000, False),
        ("Fwd hold 2", 12000, 25000, False),
        ("Fwd tank", 5000, 15000, True),
        ("Mid hold 1", 15000, 35000, False),
        ("Mid hold 2", 15000, 35000, False),
        ("Mid tank", 3000, 10000, True),
        ("Aft hold 1", 15000, 35000, False),
        ("Aft hold 2", 12000, 25000, False),
        ("Stern peak", 6000, 2000, False),
    ]

    for name, w_empty, cap, is_ballast in section_data:
        ship.sections.append(SectionConfig(
            name=name, length=section_length,
            weight_empty=w_empty * 1000.0,
            capacity=cap * 1000.0,
            is_ballast=is_ballast,
        ))

    for section in ship.sections:
        factor = 0.3 if section.is_ballast else 0.6
        section.set_load(section.capacity * factor)

    return ship


def create_tanker_vlcc() -> ShipConfig:
    """330m VLCC tanker."""
    ship = ShipConfig(
        name="VLCC Tanker-330",
        length_overall=330.0,
        beam=60.0,
        depth=28.0,
        draft_design=16.0,
        displacement=300_000_000.0,
        moment_of_inertia_zz=150000.0,  # Realistic for 330m VLCC
        y_deck=13.0,
        y_keel=-15.0,
    )

    section_length = 33.0
    section_data = [
        ("Bow peak", 15000, 5000, False),
        ("Fwd cargo", 20000, 30000, False),
        ("Fwd tank", 8000, 20000, True),
        ("Mid cargo 1", 25000, 40000, False),
        ("Mid cargo 2", 25000, 40000, False),
        ("Mid cargo 3", 25000, 40000, False),
        ("Mid tank", 5000, 15000, True),
        ("Aft cargo", 20000, 30000, False),
        ("Aft machinery", 18000, 10000, False),
        ("Stern peak", 10000, 3000, False),
    ]

    for name, w_empty, cap, is_ballast in section_data:
        ship.sections.append(SectionConfig(
            name=name, length=section_length,
            weight_empty=w_empty * 1000.0,
            capacity=cap * 1000.0,
            is_ballast=is_ballast,
        ))

    for section in ship.sections:
        factor = 0.3 if section.is_ballast else 0.6
        section.set_load(section.capacity * factor)

    return ship


# Available presets
SHIP_PRESETS = {
    "containership": create_containership_200,
    "bulk_carrier": create_bulk_carrier_250,
    "vlcc_tanker": create_tanker_vlcc,
}


def get_ship_preset(name: str) -> ShipConfig:
    """Get a ship preset by name."""
    if name not in SHIP_PRESETS:
        raise ValueError(
            f"Preset '{name}' not found. "
            f"Available: {', '.join(SHIP_PRESETS.keys())}"
        )
    return SHIP_PRESETS[name]()
