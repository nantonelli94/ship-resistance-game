"""
validators.py — Input validators
=================================

Functions for validating user inputs in the simulator.
"""

from __future__ import annotations


def validate_positive_number(value: str, name: str = "value") -> float:
    """Validates that a string is a positive number."""
    try:
        num = float(value)
    except ValueError:
        raise ValueError(f"'{value}' is not a valid number")

    if num < 0:
        raise ValueError(f"{name} must be positive, received {num}")

    return num


def validate_integer(value: str, min_val: int, max_val: int, name: str = "value") -> int:
    """Validates that a string is an integer within a range."""
    try:
        num = int(value)
    except ValueError:
        raise ValueError(f"'{value}' is not a valid integer")

    if num < min_val or num > max_val:
        raise ValueError(
            f"{name} must be between {min_val} and {max_val}, received {num}"
        )

    return num


def validate_load_value(load: float, capacity: float) -> None:
    """Validates that a load does not exceed capacity."""
    if abs(load) > capacity:
        raise ValueError(
            f"Load {load/1000:.1f} kN exceeds capacity {capacity/1000:.1f} kN"
        )


def validate_section_index(index: int, max_index: int) -> None:
    """Validates that a section index is valid."""
    if index < 0 or index >= max_index:
        raise IndexError(
            f"Index {index} out of range [0, {max_index - 1}]"
        )
