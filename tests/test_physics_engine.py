"""
test_physics_engine.py — Pruebas del motor de física
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from core.physics_engine import PhysicsEngine
from models.ship_config import ShipConfig, SectionConfig
from utils.constants import MAX_ALLOWED_STRESS


def create_test_ship() -> ShipConfig:
    """Crea un buque de prueba simple."""
    ship = ShipConfig(
        name="Test Ship",
        length_overall=100.0,
        beam=20.0,
        depth=12.0,
        draft_design=7.0,
        displacement=15_000_000.0,
        moment_of_inertia_zz=1200.0,  # Valor realista para buque 100m
        y_deck=5.5,
        y_keel=-6.5,
    )

    section_length = 20.0
    for i in range(5):
        section = SectionConfig(
            name=f"Section {i+1}",
            length=section_length,
            weight_empty=5000e3,
            capacity=10000e3,
            current_load=3000e3,
        )
        ship.sections.append(section)

    return ship


class TestPhysicsEngine:
    """Pruebas del motor de física."""

    def test_section_positions(self):
        """Las secciones deben tener posiciones correctas."""
        ship = create_test_ship()
        engine = PhysicsEngine(ship)

        assert ship.sections[0].x_center == 10.0
        assert ship.sections[1].x_center == 30.0
        assert ship.sections[2].x_center == 50.0

    def test_buoyancy_distribution(self):
        """El empuje total debe ser igual al desplazamiento."""
        ship = create_test_ship()
        engine = PhysicsEngine(ship)

        total_buoyancy = sum(s._buoyancy for s in ship.sections)
        assert abs(total_buoyancy - ship.displacement) < 1.0

    def test_load_distribution(self):
        """La distribución de carga debe tener valores razonables."""
        ship = create_test_ship()
        engine = PhysicsEngine(ship)

        positions, loads = engine.compute_load_distribution()
        assert len(positions) == 5
        assert len(loads) == 5

    def test_simulation_result(self):
        """La simulación debe retornar un resultado válido."""
        ship = create_test_ship()
        engine = PhysicsEngine(ship)

        result = engine.compute_shear_and_moment()
        assert result.status in ["VERDE", "AMARILLO", "ROJO"]
        assert len(result.sections) == 5
        assert result.total_weight > 0
        assert result.gm_estimate > -1.0

    def test_stress_calculation(self):
        """Las tensiones deben calcularse correctamente."""
        ship = create_test_ship()
        engine = PhysicsEngine(ship)

        result = engine.compute_shear_and_moment()
        for stress in result.sections:
            # Tensión no debe ser NaN
            assert stress.stress_max >= 0
            assert stress.stress_deck != 0 or stress.stress_keel != 0


class TestShipConfig:
    """Pruebas de configuración del buque."""

    def test_section_weight(self):
        """El peso total debe ser estructura + carga."""
        section = SectionConfig(
            name="Test", length=20.0,
            weight_empty=5000e3, capacity=10000e3,
            current_load=3000e3
        )
        assert section.total_weight == 8000e3

    def test_set_load_validation(self):
        """No debe permitir cargas que excedan capacidad."""
        section = SectionConfig(
            name="Test", length=20.0,
            weight_empty=5000e3, capacity=10000e3
        )
        with pytest.raises(ValueError):
            section.set_load(15000e3)

    def test_ballast_section(self):
        """Las secciones de lastre deben identificarse."""
        section = SectionConfig(
            name="Ballast", length=20.0,
            weight_empty=3000e3, capacity=8000e3,
            is_ballast=True
        )
        assert section.is_ballast
