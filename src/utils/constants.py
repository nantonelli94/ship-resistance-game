"""
constantes.py — Constantes físicas y parámetros de materiales
=============================================================

Define todas las constantes utilizadas en el simulador de resistencia
longitudinal del buque: propiedades del acero naval, factores de
seguridad y coeficientes de estado de mar.
"""

from __future__ import annotations

# =============================================================================
# PROPIEDADES DEL ACERO NAVAL (AH36)
# =============================================================================

STEEL_YIELD_STRESS: float = 235.0e6       # Pa (235 MPa)
STEEL_ULTIMATE_STRESS: float = 490.0e6     # Pa (490 MPa)
STEEL_YOUNGS_MODULUS: float = 200e9        # Pa (200 GPa)
STEEL_DENSITY: float = 7850.0              # kg/m^3
STEEL_POISSON_RATIO: float = 0.30

# =============================================================================
# FACTORES DE SEGURIDAD
# =============================================================================

SAFETY_FACTOR_YIELD: float = 1.5           # Para fluencia
SAFETY_FACTOR_BUCKLING: float = 2.0        # Para pandeo
SAFETY_FACTOR_FATIGUE: float = 1.2          # Para fatiga

# Tensión admisible derivada
MAX_ALLOWED_STRESS: float = STEEL_YIELD_STRESS / SAFETY_FACTOR_YIELD

# =============================================================================
# ESTADOS DE MAR (coeficientes de amplificación dinámica)
# =============================================================================

SEA_STATE_FACTORS: dict[int, float] = {
    0: 1.00,   # Calma
    1: 1.05,   # Marejada ligera
    2: 1.10,   # Marejada moderada
    3: 1.20,   # Marejada fuerte
    4: 1.35,   # Mar gruesa
    5: 1.50,   # Mar muy gruesa (tormenta)
}

SEA_STATE_DESCRIPTIONS: dict[int, str] = {
    0: "Calma",
    1: "Marejada ligera",
    2: "Marejada moderada",
    3: "Marejada fuerte",
    4: "Mar gruesa",
    5: "Mar muy gruesa (tormenta)",
}

# =============================================================================
# CONSTANTES FÍSICAS
# =============================================================================

GRAVITY: float = 9.81                     # m/s^2
WATER_DENSITY: float = 1025.0             # kg/m^3 (agua de mar)
AIR_DENSITY: float = 1.225                # kg/m^3

# =============================================================================
# LÍMITES DE ESTABILIDAD
# =============================================================================

GM_MIN_GREEN: float = 0.30                # m — estable
GM_MIN_YELLOW: float = 0.15               # m — margen reducido
GM_MIN_RED: float = 0.0                   # m — inestable

# =============================================================================
# COLORES SEMAFÓRICOS (ANSI)
# =============================================================================

class Colors:
    """Códigos de color ANSI para terminal."""
    VERDE = "\033[92m"
    AMARILLO = "\033[93m"
    ROJO = "\033[91m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"

    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """Aplica color ANSI al texto."""
        return f"{getattr(cls, color.upper(), '')}{text}{cls.RESET}"
