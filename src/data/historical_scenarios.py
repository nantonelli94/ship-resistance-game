"""
historical_scenarios.py — Historical case studies
==================================================

Defines scenarios based on real maritime accidents for the "Historical Cases" mode.
"""

from __future__ import annotations

from models.ship_config import ShipConfig, SectionConfig


def create_kurdistan_scenario() -> ShipConfig:
    """
    MV Kurdistan case (1979):
    Broke in two in heavy seas due to excessive bending moments.
    """
    ship = ShipConfig(
        name="MV Kurdistan (1979) — Historical Case",
        length_overall=180.0,
        beam=28.0,
        depth=16.0,
        draft_design=9.0,
        displacement=30_000_000.0,
        moment_of_inertia_zz=6000.0,  # Realistic for 180m ship
        y_deck=7.5,
        y_keel=-8.5,
        sea_state=4,  # Very rough sea
    )

    section_length = 18.0
    section_data = [
        ("Bow peak", 4000, 1500, False),
        ("Fwd cargo", 7000, 12000, False),
        ("Fwd cargo", 7000, 12000, False),
        ("Fwd tank", 2500, 6000, True),
        ("Mid cargo", 9000, 18000, False),
        ("Mid cargo", 9000, 18000, False),
        ("Mid tank", 1500, 4000, True),
        ("Aft cargo", 9000, 18000, False),
        ("Aft cargo", 7000, 12000, False),
        ("Stern peak", 3500, 1200, False),
    ]

    for name, w_empty, cap, is_ballast in section_data:
        ship.sections.append(SectionConfig(
            name=name, length=section_length,
            weight_empty=w_empty * 1000.0,
            capacity=cap * 1000.0,
            is_ballast=is_ballast,
        ))

    # Asymmetric load that caused the failure
    loads = [8000, 12000, 12000, 3000, 18000, 18000, 2000, 18000, 12000, 1000]
    for section, load in zip(ship.sections, loads):
        section.set_load(load * 1000.0)

    return ship


def create_edmund_fitzgerald_scenario() -> ShipConfig:
    """
    SS Edmund Fitzgerald case (1975):
    Sank in Lake Superior due to flooding and loss of stability.
    """
    ship = ShipConfig(
        name="SS Edmund Fitzgerald (1975) — Historical Case",
        length_overall=222.0,
        beam=23.0,
        depth=14.0,
        draft_design=8.5,
        displacement=26_000_000.0,
        moment_of_inertia_zz=3500.0,  # Realistic for 222m ship
        y_deck=6.5,
        y_keel=-7.5,
        sea_state=5,  # Storm
    )

    section_length = 22.2
    section_data = [
        ("Bow peak", 3500, 1200, False),
        ("Fwd cargo", 6000, 10000, False),
        ("Fwd cargo", 6000, 10000, False),
        ("Fwd tank", 2000, 5000, True),
        ("Mid cargo", 8000, 15000, False),
        ("Mid cargo", 8000, 15000, False),
        ("Mid tank", 1200, 3000, True),
        ("Aft cargo", 8000, 15000, False),
        ("Aft cargo", 6000, 10000, False),
        ("Stern peak", 3000, 1000, False),
    ]

    for name, w_empty, cap, is_ballast in section_data:
        ship.sections.append(SectionConfig(
            name=name, length=section_length,
            weight_empty=w_empty * 1000.0,
            capacity=cap * 1000.0,
            is_ballast=is_ballast,
        ))

    # Concentrated cargo aft (iron ore)
    loads = [6000, 10000, 10000, 2500, 15000, 15000, 1500, 15000, 10000, 800]
    for section, load in zip(ship.sections, loads):
        section.set_load(load * 1000.0)

    return ship


def create_prestige_scenario() -> ShipConfig:
    """
    MV Prestige case (2002):
    Structural failure due to fatigue and severe weather.
    """
    ship = ShipConfig(
        name="MV Prestige (2002) — Historical Case",
        length_overall=243.0,
        beam=34.0,
        depth=18.0,
        draft_design=11.0,
        displacement=50_000_000.0,
        moment_of_inertia_zz=9000.0,  # Realistic for 243m ship
        y_deck=8.0,
        y_keel=-10.0,
        sea_state=4,  # Very rough sea
    )

    section_length = 24.3
    section_data = [
        ("Bow peak", 5500, 2000, False),
        ("Fwd cargo", 8500, 14000, False),
        ("Fwd cargo", 8500, 14000, False),
        ("Fwd tank", 3000, 7000, True),
        ("Mid cargo", 10000, 18000, False),
        ("Mid cargo", 10000, 18000, False),
        ("Mid tank", 2000, 5000, True),
        ("Aft cargo", 10000, 18000, False),
        ("Aft cargo", 8500, 14000, False),
        ("Stern peak", 4500, 1800, False),
    ]

    for name, w_empty, cap, is_ballast in section_data:
        ship.sections.append(SectionConfig(
            name=name, length=section_length,
            weight_empty=w_empty * 1000.0,
            capacity=cap * 1000.0,
            is_ballast=is_ballast,
        ))

    # Load with fatigue defects
    loads = [5500, 14000, 14000, 3500, 18000, 18000, 2500, 18000, 14000, 1800]
    for section, load in zip(ship.sections, loads):
        section.set_load(load * 1000.0)

    return ship


HISTORICAL_CASES = {
    "kurdistan": {
        "name": "MV Kurdistan (1979)",
        "description": "Broke in two in heavy seas due to excessive bending moments",
        "create_fn": create_kurdistan_scenario,
    },
    "edmund_fitzgerald": {
        "name": "SS Edmund Fitzgerald (1975)",
        "description": "Sank in Lake Superior due to flooding and loss of stability",
        "create_fn": create_edmund_fitzgerald_scenario,
    },
    "prestige": {
        "name": "MV Prestige (2002)",
        "description": "Structural failure due to fatigue and severe weather",
        "create_fn": create_prestige_scenario,
    },
}


def get_historical_case(case_id: str) -> tuple[ShipConfig, str, str]:
    """Get a historical case by ID."""
    if case_id not in HISTORICAL_CASES:
        raise ValueError(
            f"Case '{case_id}' not found. "
            f"Available: {', '.join(HISTORICAL_CASES.keys())}"
        )
    case = HISTORICAL_CASES[case_id]
    ship = case["create_fn"]()
    return ship, case["name"], case["description"]
