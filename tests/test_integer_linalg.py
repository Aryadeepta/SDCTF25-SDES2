import pytest

from sdes2.integer_linalg import integer_row_reduce, multiply_matrices


def test_integer_row_operations_preserve_transformation_invariant() -> None:
    original = [[6, 1], [10, 2], [15, 4]]

    reduced, transform = integer_row_reduce(original)

    assert reduced == multiply_matrices(transform, original)
    assert [row[:2] for row in reduced[:2]] == [[1, 0], [0, 1]]
    assert all(isinstance(value, int) for row in transform for value in row)


def test_integer_row_reduction_rejects_non_primitive_column() -> None:
    with pytest.raises(ValueError, match="unit pivot"):
        integer_row_reduce([[2], [4]])


def test_integer_row_reduction_rejects_ragged_or_wide_input() -> None:
    with pytest.raises(ValueError, match="equal length"):
        integer_row_reduce([[1, 2], [3]])
    with pytest.raises(ValueError, match="at least as many rows"):
        integer_row_reduce([[1, 0, 0], [0, 1, 0]])
