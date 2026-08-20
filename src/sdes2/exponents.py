"""Exponent-schedule generation for the SDES2 construction."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ExponentScheduleParameters:
    """Public parameters controlling deterministic exponent generation."""

    exponent_bits: int
    box_count: int
    recurrence_exponent: int
    recurrence_modulus: int

    def __post_init__(self) -> None:
        if self.exponent_bits <= 0:
            raise ValueError("exponent_bits must be positive")
        if self.box_count <= 0:
            raise ValueError("box_count must be positive")
        if self.recurrence_exponent < 0:
            raise ValueError("recurrence_exponent must be non-negative")
        if self.recurrence_modulus <= 1:
            raise ValueError("recurrence_modulus must be greater than one")


def generate_exponent_schedule(
    seed: int, parameters: ExponentScheduleParameters
) -> tuple[int, ...]:
    """Generate the low-bit exponent used by each successive multiplicative box."""
    if seed < 0:
        raise ValueError("seed must be non-negative")

    mask = (1 << parameters.exponent_bits) - 1
    state = seed
    schedule = []
    for _ in range(parameters.box_count):
        schedule.append(state & mask)
        state = pow(
            state,
            parameters.recurrence_exponent,
            parameters.recurrence_modulus,
        )
    return tuple(schedule)
