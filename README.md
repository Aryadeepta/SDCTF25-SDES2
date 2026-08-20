# SDES2 Integer Reconstruction

An offline, educational reconstruction of the mathematical technique used to
solve an authorized SDCTF 2025 cryptography challenge. The project shows how
several known multiplicative transformations can be combined to remove an
unknown transformation from a target value, using only explicit integer row
operations and modular arithmetic.

The original competition networking and Windows-specific `ncat` automation
have been removed. This repository contains no remote interaction: its demo
uses deterministic toy parameters and all tests run locally.

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

For keys \(k_1, \ldots, k_b\), modulus \(N\), message \(m\), and an exponent
schedule \(e=(e_1,\ldots,e_b)\), the challenge transformation has the form

\[
  c = m \prod_{j=1}^{b} k_j^{e_j} \pmod N.
\]

Applying the transformation to the known message \(1\) reveals a factor
\(c_i=\prod_j k_j^{E_{i,j}}\) for a known exponent vector \(E_i\). If integer
coefficients \(v_i\) satisfy

\[
  \sum_i v_i E_i = e,
\]

then exponent laws give the target factor directly:

\[
  \prod_i c_i^{v_i} = \prod_j k_j^{e_j} \pmod N.
\]

The message is therefore the target value multiplied by the modular inverse of
that reconstructed factor. A negative \(v_i\) is evaluated as a modular inverse,
so the corresponding factor must be invertible modulo \(N\).

## Extended-GCD integer elimination

Ordinary Gaussian elimination can introduce fractions, which are unsuitable as
exponents in the multiplicative combination above. Instead, this implementation
uses Bezout coefficients. For two pivot entries \(a\) and \(b\), extended GCD
finds integers \(x,y\) such that

\[
  xa + yb = \gcd(a,b).
\]

The algorithm replaces the two rows with an invertible pair of integer row
combinations, repeats across the remaining rows, and obtains a pivot of `1`
when that column is primitive. It then performs elimination using integer
multiples only. Every operation is also applied to an identity matrix \(T\),
maintaining the visible invariant

\[
  R = T E,
\]

where \(E\) is the original sample matrix and \(R\) is its reduced form. Once
the leading block of \(R\) is the identity, the rows of \(T\) explicitly encode
how to form each basis vector from the known schedules. Combining those rows
with the target schedule produces the required \(v_i\).

This technique deliberately reports failure when the available rows cannot
produce a unit pivot; it does not silently switch to rational coefficients.

## Solution flow

1. Generate exponent schedules for fixed, known-message observations.
2. Build a tall integer matrix whose rows are those schedules.
3. Reduce it with extended-GCD integer row operations while tracking \(T\).
4. Express the target exponent schedule as an integer combination of samples.
5. Raise each known factor to its signed coefficient and multiply modulo \(N\).
6. Divide the transformed target by the reconstructed factor modulo \(N\).

## Repository structure

```text
src/sdes2/exponents.py       Exponent-schedule generation
src/sdes2/integer_linalg.py  Extended-GCD row reduction and invariants
src/sdes2/reconstruction.py  Factor and message reconstruction
src/sdes2/demo.py            Deterministic offline toy model
tests/                       Unit and end-to-end pytest coverage
.github/workflows/ci.yml     Lint and test workflow
```

## Setup, demo, and tests

Python 3.11 or newer is required. After obtaining the repository and while
offline, create an environment and install the project from local files (the
development dependencies must already be available in your package cache):

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

Run the deterministic local demonstration:

```bash
python -m sdes2.demo
```

Run the quality checks:

```bash
ruff check .
pytest
```

The runtime package has no third-party dependencies. Pytest and Ruff are used
only for development and CI.

## Technologies and skills demonstrated

Python, type hints, modular arithmetic, extended Euclidean algorithms, integer
linear algebra, API decomposition, deterministic test design, pytest, Ruff,
packaging with `pyproject.toml`, and GitHub Actions.

## Context and responsible use

This code documents a completed solution to a past, authorized SDCTF 2025 CTF
challenge. It is intentionally scoped to a local toy model and educational
analysis; it contains no service endpoints, socket code, target discovery, or
automation for interacting with real systems.
