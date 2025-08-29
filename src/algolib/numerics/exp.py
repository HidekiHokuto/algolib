
# src/algolib/numerics/exp.py
from __future__ import annotations

from typing import Final
from algolib.numerics.constants import (
    LN2_HI,
    LN2_LO,
    INV_LN2,
    DBL_MAX,
)

# NOTE: No math import: keep numerics self-contained.

# Derived constants
LOG2_E: Final[float] = INV_LN2
MAX_LOG: Final[float] = 709.782712893384   # ln(DBL_MAX)
MIN_LOG: Final[float] = -745.1332191019411 # ln(min subnormal)


def exp(x: float) -> float:
    r"""
    Compute the natural exponential :math:`e^x` using Cody-Waite style range
    reduction and a Padé [3/3] kernel, without relying on :mod:`math`.

    Algorithm
    ---------
    1. Range reduction:
        - Choose integer k = round(x / ln2).
        - Let r = x - k*ln2 computed via LN2_HI + LN2_LO splitting to reduce
            cancellation.
        - Then e^x = 2^k * e^r.

    2. Kernel approximation on r in [-ln2/2, ln2/2]:
        - Use a [3/3] Padé approximant:
            exp(r) ≈ (120 + 60r + 12r^2 + r^3) / (120 - 60r + 12r^2 - r^3).

    3. Reconstruct with 2**k.


    Special cases
    -------------
    - exp(+inf) = +inf
    - exp(-inf) = 0.0
    - exp(NaN)  = NaN

    Parameters
    ----------
    x : float
        Input value.

    Returns
    -------
    float
        The exponential e**x.
    """

    # Handle specials
    if x != x:  # NaN
        return float("nan")
    if x == float("inf"):
        return float("inf")
    if x == float("-inf"):
        return 0.0

    # Overflow / underflow clamps
    if x > MAX_LOG:
        return float("inf")
    if x < MIN_LOG:
        return 0.0

    # Range reduction
    k = int(x * LOG2_E + (0.5 if x >= 0 else -0.5))
    r = x - k * LN2_HI
    r -= k * LN2_LO

    # Padé [5/5] kernel (matches series up to r^10)
    r2 = r * r
    r3 = r2 * r
    r4 = r2 * r2
    r5 = r4 * r
    # Coefficients follow the standard [5/5] Padé for exp:
    # num = 30240 + 15120 r + 3360 r^2 + 420 r^3 + 30 r^4 + r^5
    # den = 30240 - 15120 r + 3360 r^2 - 420 r^3 + 30 r^4 - r^5
    num = 30240.0 + 15120.0 * r + 3360.0 * r2 + 420.0 * r3 + 30.0 * r4 + r5
    den = 30240.0 - 15120.0 * r + 3360.0 * r2 - 420.0 * r3 + 30.0 * r4 - r5
    er = num / den

    return (2.0 ** k) * er

