"""Recover messages from known SDES2-style multiplicative transformations."""

from dataclasses import dataclass

from sdes2.integer_linalg import integer_row_reduce


@dataclass(frozen=True)
class KnownTransformation:
    """An exponent vector and its observed multiplicative factor modulo N."""

    exponents: tuple[int, ...]
    factor: int


def combination_coefficients(
    known_exponents: list[tuple[int, ...]], target_exponents: tuple[int, ...]
) -> tuple[int, ...]:
    """Express a target vector as an integer combination of known vectors."""
    if not known_exponents:
        raise ValueError("at least one known exponent vector is required")
    width = len(target_exponents)
    if width == 0 or any(len(row) != width for row in known_exponents):
        raise ValueError("all exponent vectors must have the same non-zero length")

    _, transform = integer_row_reduce(known_exponents)
    return tuple(
        sum(
            target_exponents[pivot] * transform[pivot][sample]
            for pivot in range(width)
        )
        for sample in range(len(known_exponents))
    )


def reconstruct_factor(
    samples: list[KnownTransformation], target_exponents: tuple[int, ...], modulus: int
) -> int:
    """Reconstruct the target's multiplicative factor from known factors."""
    if modulus <= 1:
        raise ValueError("modulus must be greater than one")
    coefficients = combination_coefficients(
        [sample.exponents for sample in samples], target_exponents
    )
    factor = 1
    try:
        for sample, coefficient in zip(samples, coefficients, strict=True):
            factor = factor * pow(sample.factor, coefficient, modulus) % modulus
    except ValueError as error:
        raise ValueError(
            "a negative coefficient requires its factor to be invertible"
        ) from error
    return factor


def reconstruct_message(
    transformed_message: int,
    samples: list[KnownTransformation],
    target_exponents: tuple[int, ...],
    modulus: int,
) -> int:
    """Remove a reconstructed multiplicative factor from a transformed message."""
    factor = reconstruct_factor(samples, target_exponents, modulus)
    try:
        inverse = pow(factor, -1, modulus)
    except ValueError as error:
        message = "the reconstructed factor is not invertible modulo modulus"
        raise ValueError(message) from error
    return transformed_message * inverse % modulus
