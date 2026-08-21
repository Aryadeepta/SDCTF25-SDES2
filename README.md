# SDES2 Integer Reconstruction

[![CI](https://github.com/Aryadeepta/SDCTF25-SDES2/actions/workflows/ci.yml/badge.svg)](https://github.com/Aryadeepta/SDCTF25-SDES2/actions/workflows/ci.yml)

An offline, educational reconstruction of the mathematical technique used to
solve an authorized SDCTF 2025 cryptography challenge. The project shows how
known multiplicative transformations can be combined to remove an unknown
transformation from a target value using explicit integer row operations and
modular arithmetic.

## Original challenge context

SDES2 was an authorized SDCTF 2025 cryptography challenge. Its original
construction chained **8 multiplicative boxes** and exposed a limited-query
oracle: the service allowed at most 20 encryptions of chosen messages or the
target message. During the competition, the original solver collected **16
transformations of the known message 1**, then requested a transformation of
the target. It used `ncat` for the actual competition-service interaction; that
workflow is intentionally preserved as historical context.

The mathematical solution reconstructed the target exponent schedule as an
integer combination of the 16 known schedules. Those combinations were
produced with extended-GCD/Bézout row operations, allowing the corresponding
known ciphertext factors to be multiplied (or inverted for negative
coefficients) modulo $N$.

The maintained implementation under [`src/sdes2/`](src/sdes2/) is a cleaned,
deterministic, offline reconstruction of the same mathematical technique. The
original challenge used 8 boxes and its competition parameters; the current
demo and tests use smaller toy parameters. This toy model is explicitly a
reduced analogue for testing the same algebraic reconstruction technique
without needing the retired challenge server. Tests and the demo run entirely
locally and do not start or contact that server.

Preserved original artifacts:

- [`challenge/SDES2.py`](challenge/SDES2.py) — original cryptographic construction
- [`challenge/server.py`](challenge/server.py) — original menu service and
  20-query oracle
- [`challenge/Dockerfile`](challenge/Dockerfile) — original `socat` container,
  exposing the service on port 1337
- [`legacy/hacker.py`](legacy/hacker.py) — original competition solver and its
  Windows `ncat` interaction
- [`docs/original-writeup.md`](docs/original-writeup.md) — original competition
  writeup

These files are retained as historical artifacts and are not the maintained
implementation or part of the current test suite.

In particular, `legacy/hacker.py` is the original competition-time solver, not
a supported modern entry point. It historically required Windows `cmd`,
Nmap's `ncat`, NumPy, and SymPy; those packages are intentionally not modern
project dependencies.

## Technical highlights

- Models a chained construction of keyed modular powers.
- Generates deterministic exponent schedules from public recurrence parameters.
- Solves for an integer combination of known exponent vectors without a
  rational or black-box linear solver.
- Tracks a transformation matrix through extended-GCD row operations.
- Handles negative combination coefficients through modular inverses.
- Separates schedule generation, integer linear algebra, reconstruction, and
  demonstration code, with typed APIs and pytest coverage.

## Mathematical construction

For keys $k_1, \ldots, k_b$, modulus $N$, message $m$, and an exponent schedule
$e=(e_1,\ldots,e_b)$, the challenge transformation has the form

$$
c = m \prod_{j=1}^{b} k_j^{e_j} \pmod N.
$$

Applying the transformation to the known message $1$ reveals a factor
$c_i=\prod_j k_j^{E_{i,j}}$ for a known exponent vector $E_i$. If integer
coefficients $v_i$ satisfy

$$
\sum_i v_i E_i = e,
$$

then exponent laws give the target factor directly:

$$
\prod_i c_i^{v_i} = \prod_j k_j^{e_j} \pmod N.
$$

The message is therefore the target value multiplied by the modular inverse of
that reconstructed factor. A negative $v_i$ is evaluated as a modular inverse,
so the corresponding factor must be invertible modulo $N$.

## Extended-GCD integer elimination

Ordinary Gaussian elimination can introduce fractions, which are unsuitable as
exponents in the multiplicative combination above. Instead, this implementation
uses Bézout coefficients. For two pivot entries $a$ and $b$, extended GCD finds
integers $x,y$ such that

$$
xa + yb = \gcd(a,b).
$$

The algorithm replaces the two rows with an invertible pair of integer row
combinations, repeats across the remaining rows, and obtains a pivot of `1`
when that column is primitive. It then performs elimination using integer
multiples only. Every operation is also applied to an identity matrix $T$,
maintaining the visible invariant

$$
R = T E,
$$

where $E$ is the original sample matrix and $R$ is its reduced form. Once the
leading block of $R$ is the identity, the rows of $T$ explicitly encode how to
form each basis vector from the known schedules. Combining those rows with the
target schedule produces the required $v_i$.

This technique deliberately reports failure when the available rows cannot
produce a unit pivot; it does not silently switch to rational coefficients.

## Solution flow

1. Generate exponent schedules for fixed, known-message observations.
2. Build a tall integer matrix whose rows are those schedules.
3. Reduce it with extended-GCD integer row operations while tracking $T$.
4. Express the target exponent schedule as an integer combination of samples.
5. Raise each known factor to its signed coefficient and multiply modulo $N$.
6. Divide the transformed target by the reconstructed factor modulo $N$.

## Repository structure

```text
src/sdes2/                  Maintained deterministic implementation
tests/                      Unit and end-to-end pytest coverage
challenge/                  Preserved original challenge and container
legacy/hacker.py            Preserved original competition solver
docs/original-writeup.md    Preserved original writeup
.github/workflows/ci.yml    Lint and test workflow
```

## Setup, demo, and tests

Python 3.11 or newer is required. Install the project and development tools:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e '.[dev]'
```

Run the deterministic local demo and checks:

```bash
python3 -m sdes2.demo
python3 -m ruff check .
python3 -m pytest -q
```

Neither the demo nor the tests require the historical challenge server. The
runtime package has no third-party dependencies; pytest and Ruff are used only
for development and CI.

## Technologies and skills demonstrated

Python, type hints, modular arithmetic, extended Euclidean algorithms, integer
linear algebra, API decomposition, deterministic test design, pytest, Ruff,
packaging with `pyproject.toml`, and GitHub Actions.

## Context and responsible use

This repository documents a completed solution to a past, authorized SDCTF
2025 CTF challenge. The maintained implementation is scoped to deterministic,
offline analysis. Original service and networking code is retained only to
accurately preserve the competition artifacts and workflow.
