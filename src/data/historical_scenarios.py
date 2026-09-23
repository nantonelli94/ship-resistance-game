"""
historical_scenarios.py — Casos de estudio históricos
======================================================

Define escenarios basados en accidentes navales reales
para el modo "Casos de Estudio Históricos".
"""

from __future__ import annotations

from models.ship_config import ShipConfig, SectionConfig


def create_kurdistan_scenario() -> ShipConfig:
    """
    Caso MV Kurdistan (1979):
    Rotura en dos en mar gruesa por concentración de momentos flectores.
    """
    ship = ShipConfig(
        name="MV Kurdistan (1979) — Caso Histórico",
        length_overall=180.0,
        beam=28.0,
        depth=16.0,
        draft_design=9.0,
        displacement=30_000_000.0,
        moment_of_inertia_zz=6000.0,  # I_z realista para buque 180m
        y_deck=7.5,
        y_keel=-8.5,
        sea_state=4,  # Mar gruesa
    )

    section_length = 18.0
    section_data = [
        ("Pico de proa", 4000, 1500, False),
        ("Proa - Carga", 7000, 12000, False),
        ("Proa - Carga", 7000, 12000, False),
        ("Tanque proa", 2500, 6000, True),
        ("Centro - Carga", 9000, 18000, False),
        ("Centro - Carga", 9000, 18000, False),
        ("Tanque centro", 1500, 4000, True),
        ("Popa - Carga", 9000, 18000, False),
        ("Popa - Carga", 7000, 12000, False),
        ("Pico de popa", 3500, 1200, False),
    ]

    for name, w_empty, cap, is_ballast in section_data:
        ship.sections.append(SectionConfig(
            name=name, length=section_length,
            weight_empty=w_empty * 1000.0,
            capacity=cap * 1000.0,
            is_ballast=is_ballast,
        ))

    # Carga asimétrica que causó la falla
    loads = [8000, 12000, 12000, 3000, 18000, 18000, 2000, 18000, 12000, 1000]
    for section, load in zip(ship.sections, loads):
        section.set_load(load * 1000.0)

    return ship


def create_edmund_fitzgerald_scenario() -> ShipConfig:
    """
    Caso SS Edmund Fitzgerald (1975):
    Hundimiento en el lago Superior por inundación y pérdida de estabilidad.
    """
    ship = ShipConfig(
        name="SS Edmund Fitzgerald (1975) — Caso Histórico",
        length_overall=222.0,
        beam=23.0,
        depth=14.0,
        draft_design=8.5,
        displacement=26_000_000.0,
        moment_of_inertia_zz=3500.0,  # I_z realista para buque 222m
        y_deck=6.5,
        y_keel=-7.5,
        sea_state=5,  # Tormenta
    )

    section_length = 22.2
    section_data = [
        ("Pico de proa", 3500, 1200, False),
        ("Proa - Carga", 6000, 10000, False),
        ("Proa - Carga", 6000, 10000, False),
        ("Tanque proa", 2000, 5000, True),
        ("Centro - Carga", 8000, 15000, False),
        ("Centro - Carga", 8000, 15000, False),
        ("Tanque centro", 1200, 3000, True),
        ("Popa - Carga", 8000, 15000, False),
        ("Popa - Carga", 6000, 10000, False),
        ("Pico de popa", 3000, 1000, False),
    ]

    for name, w_empty, cap, is_ballast in section_data:
        ship.sections.append(SectionConfig(
            name=name, length=section_length,
            weight_empty=w_empty * 1000.0,
            capacity=cap * 1000.0,
            is_ballast=is_ballast,
        ))

    # Carga concentrada en popa (mineral de hierro)
    loads = [6000, 10000, 10000, 2500, 15000, 15000, 1500, 15000, 10000, 800]
    for section, load in zip(ship.sections, loads):
        section.set_load(load * 1000.0)

    return ship


def create_prestige_scenario() -> ShipConfig:
    """
    Caso MV Prestige (2002):
    Rotura estructural por fatiga y mal tiempo.
    """
    ship = ShipConfig(
        name="MV Prestige (2002) — Caso Histórico",
        length_overall=243.0,
        beam=34.0,
        depth=18.0,
        draft_design=11.0,
        displacement=50_000_000.0,
        moment_of_inertia_zz=9000.0,  # I_z realista para buque 243m
        y_deck=8.0,
        y_keel=-10.0,
        sea_state=4,  # Mar gruesa
    )

    section_length = 24.3
    section_data = [
        ("Pico de proa", 5500, 2000, False),
        ("Proa - Carga", 8500, 14000, False),
        ("Proa - Carga", 8500, 14000, False),
        ("Tanque proa", 3000, 7000, True),
        ("Centro - Carga", 10000, 18000, False),
        ("Centro - Carga", 10000, 18000, False),
        ("Tanque centro", 2000, 5000, True),
        ("Popa - Carga", 10000, 18000, False),
        ("Popa - Carga", 8500, 14000, False),
        ("Pico de popa", 4500, 1800, False),
    ]

    for name, w_empty, cap, is_ballast in ship.sections:
        section = SectionConfig(
            name=name, length=section_length,
            weight_empty=w_empty * 1000.0,
            capacity=cap * 1000.0,
            is_ballast=is_ballast,
        )
        ship.sections.append(section)

    # Carga con defectos de fatiga
    loads = [5500, 14000, 14000, 3500, 18000, 18000, 2500, 18000, 14000, 1800]
    for section, load in zip(ship.sections, loads):
        section.set_load(load * 1000.0)

    return ship


HISTORICAL_CASES = {
    "kurdistan": {
        "name": "MV Kurdistan (1979)",
        "description": "Rotura en dos en mar gruesa por momentos flectores excesivos",
        "create_fn": create_kurdistan_scenario,
    },
    "edmund_fitzgerald": {
        "name": "SS Edmund Fitzgerald (1975)",
        "description": "Hundimiento en lago Superior por inundación y pérdida de estabilidad",
        "create_fn": create_edmund_fitzgerald_scenario,
    },
    "prestige": {
        "name": "MV Prestige (2002)",
        "description": "Rotura estructural por fatiga y mal tiempo",
        "create_fn": create_prestige_scenario,
    },
}


def get_historical_case(case_id: str) -> tuple[ShipConfig, str, str]:
    """Obtiene un caso histórico por ID."""
    if case_id not in HISTORICAL_CASES:
        raise ValueError(
            f"Caso '{case_id}' no encontrado. "
            f"Disponibles: {', '.join(HISTORICAL_CASES.keys())}"
        )
    case = HISTORICAL_CASES[case_id]
    ship = case["create_fn"]()
    return ship, case["name"], case["description"]
