"""
constants.py — Physical constants and material properties
=========================================================

Defines all constants used for longitudinal ship strength simulation:
naval steel properties, safety factors, and sea state coefficients.
"""

from __future__ import annotations

# =============================================================================
# NAVAL STEEL PROPERTIES (AH36)
# =============================================================================

STEEL_YIELD_STRESS: float = 235.0e6       # Pa (235 MPa)
STEEL_ULTIMATE_STRESS: float = 490.0e6     # Pa (490 MPa)
STEEL_YOUNGS_MODULUS: float = 200e9        # Pa (200 GPa)
STEEL_DENSITY: float = 7850.0              # kg/m^3
STEEL_POISSON_RATIO: float = 0.30

# =============================================================================
# SAFETY FACTORS
# =============================================================================

SAFETY_FACTOR_YIELD: float = 1.5           # For yield
SAFETY_FACTOR_BUCKLING: float = 2.0        # For buckling
SAFETY_FACTOR_FATIGUE: float = 1.2          # For fatigue

# Derived allowable stress
MAX_ALLOWED_STRESS: float = STEEL_YIELD_STRESS / SAFETY_FACTOR_YIELD

# =============================================================================
# SEA STATES (dynamic amplification factors — Douglas scale)
# =============================================================================

SEA_STATE_FACTORS: dict[int, float] = {
    0: 1.00,   # Calm
    1: 1.05,   # Slight swell
    2: 1.10,   # Moderate swell
    3: 1.20,   # Rough sea
    4: 1.35,   # Very rough sea
    5: 1.50,   # High sea (storm)
}

SEA_STATE_DESCRIPTIONS: dict[int, str] = {
    0: "Calm",
    1: "Slight swell",
    2: "Moderate swell",
    3: "Rough sea",
    4: "Very rough sea",
    5: "High sea (storm)",
}

# =============================================================================
# PHYSICAL CONSTANTS
# =============================================================================

GRAVITY: float = 9.81                     # m/s^2
WATER_DENSITY: float = 1025.0             # kg/m^3 (seawater)
AIR_DENSITY: float = 1.225                # kg/m^3

# =============================================================================
# STABILITY LIMITS
# =============================================================================

GM_MIN_GREEN: float = 0.30                # m — stable
GM_MIN_YELLOW: float = 0.15               # m — reduced margin
GM_MIN_RED: float = 0.0                   # m — unstable

# =============================================================================
# TRAFFIC LIGHT COLORS (ANSI)
# =============================================================================

class Colors:
    """ANSI color codes for terminal output."""
    VERDE = "\033[92m"
    AMARILLO = "\033[93m"
    ROJO = "\033[91m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"

    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """Apply ANSI color to text."""
        return f"{getattr(cls, color.upper(), '')}{text}{cls.RESET}"
