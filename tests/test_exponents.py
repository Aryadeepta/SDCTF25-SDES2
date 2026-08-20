import pytest

from sdes2.exponents import ExponentScheduleParameters, generate_exponent_schedule


def test_exponent_schedule_follows_modular_recurrence_and_masks_low_bits() -> None:
    parameters = ExponentScheduleParameters(4, 4, 5, 65_537)

    assert generate_exponent_schedule(12_345, parameters) == (9, 7, 1, 12)


@pytest.mark.parametrize("seed", [-1, -100])
def test_exponent_schedule_rejects_negative_seed(seed: int) -> None:
    parameters = ExponentScheduleParameters(4, 4, 5, 65_537)

    with pytest.raises(ValueError, match="non-negative"):
        generate_exponent_schedule(seed, parameters)


def test_exponent_parameters_reject_invalid_dimensions() -> None:
    with pytest.raises(ValueError, match="exponent_bits"):
        ExponentScheduleParameters(0, 4, 5, 65_537)
    with pytest.raises(ValueError, match="box_count"):
        ExponentScheduleParameters(4, 0, 5, 65_537)
