"""Small integer-linear-algebra helpers used by the reconstruction attack."""

from collections.abc import Sequence

Matrix = list[list[int]]


def extended_gcd(left: int, right: int) -> tuple[int, int, int]:
    """Return ``(gcd, x, y)`` such that ``x*left + y*right == gcd``."""
    old_remainder, remainder = abs(left), abs(right)
    old_x, x = 1, 0
    old_y, y = 0, 1
    while remainder:
        quotient = old_remainder // remainder
        old_remainder, remainder = remainder, old_remainder - quotient * remainder
        old_x, x = x, old_x - quotient * x
        old_y, y = y, old_y - quotient * y

    left_sign = -1 if left < 0 else 1
    right_sign = -1 if right < 0 else 1
    return old_remainder, old_x * left_sign, old_y * right_sign


def _combine_rows_for_gcd(
    matrix: Matrix, transform: Matrix, pivot: int, row: int
) -> None:
    """Replace two rows with an invertible integer combination producing their GCD."""
    left, right = matrix[pivot][pivot], matrix[row][pivot]
    divisor, left_coefficient, right_coefficient = extended_gcd(left, right)
    if divisor == 0:
        return

    old_pivot = matrix[pivot][:]
    old_row = matrix[row][:]
    old_transform_pivot = transform[pivot][:]
    old_transform_row = transform[row][:]
    matrix[pivot] = [
        left_coefficient * a + right_coefficient * b
        for a, b in zip(old_pivot, old_row, strict=True)
    ]
    matrix[row] = [
        -(right // divisor) * a + (left // divisor) * b
        for a, b in zip(old_pivot, old_row, strict=True)
    ]
    transform[pivot] = [
        left_coefficient * a + right_coefficient * b
        for a, b in zip(old_transform_pivot, old_transform_row, strict=True)
    ]
    transform[row] = [
        -(right // divisor) * a + (left // divisor) * b
        for a, b in zip(old_transform_pivot, old_transform_row, strict=True)
    ]


def integer_row_reduce(rows: Sequence[Sequence[int]]) -> tuple[Matrix, Matrix]:
    """Reduce a tall integer matrix while tracking every row operation.

    A unit pivot is constructed in each column by repeatedly applying Bezout
    coefficients to the remaining rows. The returned matrices satisfy
    ``reduced == transform @ rows`` using integer arithmetic only.

    Raises:
        ValueError: if the matrix is empty, ragged, not tall enough, or a
            column cannot produce a unit pivot.
    """
    if not rows or not rows[0]:
        raise ValueError("matrix must be non-empty")
    column_count = len(rows[0])
    if any(len(row) != column_count for row in rows):
        raise ValueError("matrix rows must have equal length")
    if len(rows) < column_count:
        raise ValueError("matrix must have at least as many rows as columns")

    reduced = [list(row) for row in rows]
    transform = [
        [int(row_index == column_index) for column_index in range(len(rows))]
        for row_index in range(len(rows))
    ]

    for pivot in range(column_count):
        for row in range(pivot + 1, len(reduced)):
            _combine_rows_for_gcd(reduced, transform, pivot, row)
        if reduced[pivot][pivot] == -1:
            reduced[pivot] = [-value for value in reduced[pivot]]
            transform[pivot] = [-value for value in transform[pivot]]
        if reduced[pivot][pivot] != 1:
            raise ValueError(f"column {pivot} does not admit an integer unit pivot")
        for row in range(pivot + 1, len(reduced)):
            multiple = reduced[row][pivot]
            pairs = zip(reduced[row], reduced[pivot], strict=True)
            reduced[row] = [
                value - multiple * pivot_value for value, pivot_value in pairs
            ]
            transform[row] = [
                value - multiple * pivot_value
                for value, pivot_value in zip(
                    transform[row], transform[pivot], strict=True
                )
            ]

    for pivot in range(column_count - 1, -1, -1):
        for row in range(pivot):
            multiple = reduced[row][pivot]
            pairs = zip(reduced[row], reduced[pivot], strict=True)
            reduced[row] = [
                value - multiple * pivot_value for value, pivot_value in pairs
            ]
            transform[row] = [
                value - multiple * pivot_value
                for value, pivot_value in zip(
                    transform[row], transform[pivot], strict=True
                )
            ]
    return reduced, transform


def multiply_matrices(
    left: Sequence[Sequence[int]], right: Sequence[Sequence[int]]
) -> Matrix:
    """Multiply two integer matrices; primarily exposed for invariant tests."""
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("incompatible matrix dimensions")
    return [
        [
            sum(a * b for a, b in zip(row, column, strict=True))
            for column in zip(*right, strict=True)
        ]
        for row in left
    ]
