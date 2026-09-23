"""
ship_presets.py — Presets de buques predefinidos
=================================================

Define configuraciones de buques típicos para el simulador.
"""

from __future__ import annotations

from models.ship_config import ShipConfig, SectionConfig


def create_containership_200() -> ShipConfig:
    """Portacontenedores de 200m de eslora."""
    ship = ShipConfig(
        name="MV Containership-200",
        length_overall=200.0,
        beam=32.0,
        depth=18.0,
        draft_design=10.0,
        displacement=45_000_000.0,
        moment_of_inertia_zz=8500.0,  # I_z realista para buque 200m x 32m x 18m
        y_deck=8.5,
        y_keel=-9.0,
    )

    section_length = 20.0
    section_data = [
        ("Pico de proa", 5000, 2000, False),
        ("Proa - Carga 1", 8000, 15000, False),
        ("Proa - Carga 2", 8000, 15000, False),
        ("Tanque proa", 3000, 8000, True),
        ("Centro - Carga 1", 10000, 20000, False),
        ("Centro - Carga 2", 10000, 20000, False),
        ("Tanque centro", 2000, 5000, True),
        ("Popa - Carga 1", 10000, 20000, False),
        ("Popa - Carga 2", 8000, 15000, False),
        ("Pico de popa", 4000, 1500, False),
    ]

    for name, w_empty, cap, is_ballast in section_data:
        ship.sections.append(SectionConfig(
            name=name, length=section_length,
            weight_empty=w_empty * 1000.0,
            capacity=cap * 1000.0,
            is_ballast=is_ballast,
        ))

    # Carga por defecto
    for section in ship.sections:
        factor = 0.3 if section.is_ballast else 0.6
        section.set_load(section.capacity * factor)

    return ship


def create_bulk_carrier_250() -> ShipConfig:
    """Granelero de 250m de eslora."""
    ship = ShipConfig(
        name="MV BulkCarrier-250",
        length_overall=250.0,
        beam=40.0,
        depth=20.0,
        draft_design=12.0,
        displacement=80_000_000.0,
        moment_of_inertia_zz=22000.0,  # I_z realista para granelero 250m
        y_deck=9.5,
        y_keel=-10.5,
    )

    section_length = 25.0
    section_data = [
        ("Pico de proa", 8000, 3000, False),
        ("Proa - Hold 1", 12000, 25000, False),
        ("Proa - Hold 2", 12000, 25000, False),
        ("Tanque proa", 5000, 15000, True),
        ("Centro - Hold 1", 15000, 35000, False),
        ("Centro - Hold 2", 15000, 35000, False),
        ("Tanque centro", 3000, 10000, True),
        ("Popa - Hold 1", 15000, 35000, False),
        ("Popa - Hold 2", 12000, 25000, False),
        ("Pico de popa", 6000, 2000, False),
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
    """Petrolero VLCC de 330m de eslora."""
    ship = ShipConfig(
        name="VLCC Tanker-330",
        length_overall=330.0,
        beam=60.0,
        depth=28.0,
        draft_design=16.0,
        displacement=300_000_000.0,
        moment_of_inertia_zz=150000.0,  # I_z realista para VLCC 330m
        y_deck=13.0,
        y_keel=-15.0,
    )

    section_length = 33.0
    section_data = [
        ("Pico de proa", 15000, 5000, False),
        ("Proa - Cargo", 20000, 30000, False),
        ("Tanque proa", 8000, 20000, True),
        ("Centro - Cargo 1", 25000, 40000, False),
        ("Centro - Cargo 2", 25000, 40000, False),
        ("Centro - Cargo 3", 25000, 40000, False),
        ("Tanque centro", 5000, 15000, True),
        ("Popa - Cargo", 20000, 30000, False),
        ("Popa - Maquinaria", 18000, 10000, False),
        ("Pico de popa", 10000, 3000, False),
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


# Diccionario de presets disponibles
SHIP_PRESETS = {
    "containership": create_containership_200,
    "bulk_carrier": create_bulk_carrier_250,
    "vlcc_tanker": create_tanker_vlcc,
}


def get_ship_preset(name: str) -> ShipConfig:
    """Obtiene un preset de buque por nombre."""
    if name not in SHIP_PRESETS:
        raise ValueError(
            f"Preset '{name}' no encontrado. "
            f"Disponibles: {', '.join(SHIP_PRESETS.keys())}"
        )
    return SHIP_PRESETS[name]()
