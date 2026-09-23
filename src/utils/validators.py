"""
validators.py — Validadores de entrada
======================================

Funciones para validar entradas del usuario en el simulador.
"""

from __future__ import annotations


def validate_positive_number(value: str, name: str = "valor") -> float:
    """Valida que un string sea un número positivo."""
    try:
        num = float(value)
    except ValueError:
        raise ValueError(f"'{value}' no es un número válido")

    if num < 0:
        raise ValueError(f"{name} debe ser positivo, se recibió {num}")

    return num


def validate_integer(value: str, min_val: int, max_val: int, name: str = "valor") -> int:
    """Valida que un string sea un entero en un rango."""
    try:
        num = int(value)
    except ValueError:
        raise ValueError(f"'{value}' no es un entero válido")

    if num < min_val or num > max_val:
        raise ValueError(
            f"{name} debe estar entre {min_val} y {max_val}, se recibió {num}"
        )

    return num


def validate_load_value(load: float, capacity: float) -> None:
    """Valida que una carga no exceda la capacidad."""
    if abs(load) > capacity:
        raise ValueError(
            f"Carga {load/1000:.1f} kN excede capacidad {capacity/1000:.1f} kN"
        )


def validate_section_index(index: int, max_index: int) -> None:
    """Valida que un índice de sección sea válido."""
    if index < 0 or index >= max_index:
        raise IndexError(
            f"Índice {index} fuera de rango [0, {max_index - 1}]"
        )
