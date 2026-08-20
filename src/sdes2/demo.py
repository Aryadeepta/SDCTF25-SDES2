"""Deterministic, entirely local demonstration of message reconstruction."""

from sdes2.exponents import ExponentScheduleParameters, generate_exponent_schedule
from sdes2.reconstruction import KnownTransformation, reconstruct_message

TOY_MODULUS = 1_000_003
TOY_KEYS = (2, 3, 5, 7)
TOY_MESSAGE = 424_242
TOY_PARAMETERS = ExponentScheduleParameters(
    exponent_bits=4,
    box_count=len(TOY_KEYS),
    recurrence_exponent=5,
    recurrence_modulus=65_537,
)
KNOWN_SEEDS = (10_840, 62_601, 22_713, 59, 48_662, 49_238, 30_410, 8_623)
TARGET_SEED = 12_345


def multiplicative_factor(exponents: tuple[int, ...]) -> int:
    """Evaluate the toy model's product of keyed powers."""
    factor = 1
    for key, exponent in zip(TOY_KEYS, exponents, strict=True):
        factor = factor * pow(key, exponent, TOY_MODULUS) % TOY_MODULUS
    return factor


def run_demo() -> int:
    """Construct fixed local observations and reconstruct the toy message."""
    samples = []
    for seed in KNOWN_SEEDS:
        exponents = generate_exponent_schedule(seed, TOY_PARAMETERS)
        samples.append(KnownTransformation(exponents, multiplicative_factor(exponents)))

    target_exponents = generate_exponent_schedule(TARGET_SEED, TOY_PARAMETERS)
    transformed = TOY_MESSAGE * multiplicative_factor(target_exponents) % TOY_MODULUS
    return reconstruct_message(transformed, samples, target_exponents, TOY_MODULUS)


def main() -> None:
    """Print the deterministic demonstration result."""
    recovered = run_demo()
    print(f"Original message:      {TOY_MESSAGE}")
    print(f"Reconstructed message: {recovered}")
    print(f"Match: {recovered == TOY_MESSAGE}")


if __name__ == "__main__":
    main()
