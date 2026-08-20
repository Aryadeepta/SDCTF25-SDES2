import pytest

from sdes2.demo import TOY_MESSAGE, run_demo
from sdes2.reconstruction import (
    KnownTransformation,
    combination_coefficients,
    reconstruct_factor,
)


def test_local_demo_reconstructs_known_message() -> None:
    assert run_demo() == TOY_MESSAGE


def test_combination_coefficients_recreate_target_vector() -> None:
    known = [(1, 0), (0, 1), (1, 1)]
    target = (7, -2)

    coefficients = combination_coefficients(known, target)

    assert tuple(
        sum(
            coefficient * row[column]
            for coefficient, row in zip(coefficients, known, strict=True)
        )
        for column in range(2)
    ) == target


def test_negative_coefficient_requires_an_invertible_factor() -> None:
    samples = [KnownTransformation((1,), 2)]

    with pytest.raises(ValueError, match="negative coefficient"):
        reconstruct_factor(samples, (-1,), 4)


def test_vector_dimensions_must_match() -> None:
    with pytest.raises(ValueError, match="same non-zero length"):
        combination_coefficients([(1, 2)], (1,))
