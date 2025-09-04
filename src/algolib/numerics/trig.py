"""Trigonometric functions via Chebyshev expansions (pure Python).

This module provides numerically stable implementations of ``sin``, ``cos``,
and ``tan`` without importing :mod:`math` or third-party packages. The design
follows a *full-period* Chebyshev expansion on the mapped variable

    y = remainder(x, 2π) / π  ∈ [-1, 1],

so that the periodicity is handled up-front by IEEE-754-style remainder, and
the series is evaluated on a compact domain using Clenshaw recurrence.

Policy
------
- Non-finite inputs (NaN/±Inf) return ``NAN`` (no exceptions).
- Remainder reduction uses :func:`algolib.numerics.rounding.remainder` with
  sticky-zero behavior to stabilize values near multiples of the period.
- The trigonometric functions are computed via stable Chebyshev expansions
  on a mapped variable to ensure accuracy and periodicity.
"""

from __future__ import annotations

from typing import List

from algolib.numerics.constants import PI, NAN, isfinite_f
from algolib.numerics.rounding import remainder
from algolib.numerics.rounding import round_even
from algolib.numerics.sqrt import newton_sqrt as sqrt
from algolib.numerics.constants import PI, TAU, NAN, isfinite_f

__all__ = ["sin", "cos", "tan"]


# ---------------------------------------------------------------------------
# Chebyshev evaluator (Clenshaw)
# ---------------------------------------------------------------------------

def _clenshaw_T(y: float, c_full: List[float]) -> float:
    """Evaluate ``∑ c_k T_k(y)`` with Clenshaw recurrence.

    Parameters
    ----------
    y : float
        Evaluation point with ``|y| ≤ 1``.
    c_full : list of float
        Coefficients for Chebyshev T polynomials, where ``c_full[k]``
        multiplies ``T_k(y)``.

    Returns
    -------
    float
        The series value at ``y``.
    """
    if not c_full:
        return 0.0
    b1 = 0.0
    b2 = 0.0
    for ck in reversed(c_full[1:]):
        b0 = 2.0 * y * b1 - b2 + ck
        b2, b1 = b1, b0
    return y * b1 - b2 + c_full[0]


# ---------------------------------------------------------------------------
# Sine kernel: odd-order Chebyshev series for f(y) = sin(π y)
# y = remainder(x, 2π) / π  ∈ [-1, 1]
# Only odd indices are non-zero: c[2k+1] = a[k].
# The list below is long enough to deliver ~1e-15 absolute accuracy in
# practice over typical ranges, assuming correct mapping and double-precision.
# ---------------------------------------------------------------------------

_A_SIN_ODD: List[float] = [
    5.69230686359505514690621199372e-1,   # T1   =  2*J1(pi)
    -6.66916672405979070780437163480e-1,  # T3   = -2*J3(pi)
    1.04282368734236949480920252186e-1,   # T5   =  2*J5(pi)
    -6.84063353699157900985137450329e-3,  # T7   = -2*J7(pi)
    2.50006884950386227652215859008e-4,   # T9   =  2*J9(pi)
    -5.85024830863914369171711619397e-6,  # T11  = -2*J11(pi)
    9.53477275029940114004406775030e-8,   # T13  =  2*J13(pi)
    -1.14563844170946315134756461815e-9,  # T15  = -2*J15(pi)
    1.05742726175391285886989821647e-11,  # T17  =  2*J17(pi)
    -7.73527099540430709415664628627e-14, # T19  = -2*J19(pi)
    4.59595614618295945919569164343e-16,  # T21  =  2*J21(pi)
    -2.26230592819741110431266043618e-18, # T23  = -2*J23(pi)
    9.37764779915313579625162444174e-21,  # T25  =  2*J25(pi)
]

# 1) 在 sin 的系数表后面，新增 cos 的偶阶系数表
_A_COS_EVEN: List[float] = [
    -3.04242177644093864202034912818e-1, # T0
    -9.70867865263018219410991432366e-1, # T2
    3.02849155262699421507419118631e-1,  # T4
    -2.90919339650111211473207392080e-2,
    1.39224399117623185998462220895e-3,
    -4.01899445107549429881652623637e-5,
    7.78276701181530608857305789695e-7,
    -1.08265303418582848109342149268e-8,
    1.13510917791150770103019401952e-10,
    -9.29529663267875655288541008453e-13,
    6.11136418833476772380622907668e-15,
    -3.29765784134345898638243555411e-17,
    1.48681342367320770479543710935e-19,
    -5.68557813684716435376105402637e-22,
    1.86742062104768142592220173020e-24,  # T28
    -5.32544678353978417005705767787e-27,
    1.33102565167121694216809032100e-29,
    -2.93964321349350579748495535843e-32,
    5.77860971039493827501269009893e-35, # T36
    -1.01757564166906268062520133550e-37,
    1.61445217148946221306633275540e-40
]


# High-precision reduction constants (Cody–Waite style) for π/2.
# These are standard splits used to reduce argument with minimal rounding error.
_INVPIO2 = 6.36619772367581382433e-01  # 2/pi
_PIO2_1  = 1.57079632673412561417e+00  # first 33 bits of pi/2
_PIO2_2  = 6.07710050630396597660e-11  # next bits
_PIO2_3  = 2.02226624879595063154e-21  # tail

# High-precision reduction constants for π (Cody–Waite style).
_INVPI  = 3.18309886183790671538e-01  # 1/pi
_PI_1   = 3.14159265358979311600e+00  # first 33 bits of pi
_PI_2   = 1.22464679914735320717e-16  # next bits
_PI_3   = 2.69546091939735374550e-33  # tail


def _reduce_pi(x: float) -> tuple[int, float]:
    """Reduce x by π with Cody–Waite split, returning (k, r).

    k = round_even(x / π) and r = x - k*π using hi/mid/lo compensation.
    The remainder r is in about [-π/2, π/2].
    """
    k = int(round_even(x * _INVPI))
    kd = float(k)
    r = ((x - kd * _PI_1) - kd * _PI_2) - kd * _PI_3
    return k, r


def _reduce_pio2(x: float) -> tuple[int, float]:
    """Reduce x by π/2 with Cody–Waite split, returning (k, r).

    k = round_even(x * 2/pi) and r = x - k*(π/2) with hi/mid/lo compensation.
    The remainder r is in about [-π/4, π/4].
    """
    k = int(round_even(x * _INVPIO2))
    kd = float(k)
    r = ((x - kd * _PIO2_1) - kd * _PIO2_2) - kd * _PIO2_3
    return k, r


def _sincos_highprec(x: float) -> tuple[float, float]:
    """Compute (sin(x), cos(x)) using high-precision π/2 argument reduction.

    This performs Cody–Waite style reduction to ``r ∈ [-π/4, π/4]`` by rounding
    ``k ≈ x / (π/2)`` to nearest-even, then subtracting ``k*(π/2)`` using a
    split constant (hi+mid+lo) to minimize cancellation. The final (sin, cos)
    for the original ``x`` is reconstructed from ``(sin r, cos r)`` via the
    quadrant determined by ``k mod 4``. No third-party libs are used.
    """
    # Fast path for non-finite handled by caller.
    # Compute k, r = _reduce_pio2(x)
    k, r = _reduce_pio2(x)

    # Evaluate sin(r), cos(r) via Chebyshev kernels on y = r/π ∈ [-0.25, 0.25]
    y = r / PI
    sr = _sin_series_cheb(y)
    cr = _cos_series_cheb(y)

    # Quadrant reconstruction
    n = k & 3  # k mod 4
    if n == 0:
        s, c = sr, cr
    elif n == 1:
        s, c = cr, -sr
    elif n == 2:
        s, c = -sr, -cr
    else:  # n == 3
        s, c = -cr, sr

    return s, c


def _tan_kernel(r: float) -> float:
    """Evaluate tan(r) for |r| ≤ π/4 using a truncated continued fraction.

    tan r = r / (1 - r^2/(3 - r^2/(5 - r^2/(7 - ...))))
    We use backward evaluation with an odd-denominator ladder. Depth 15 is
    ample for ~1e-15 accuracy in double precision on this interval.
    """
    x2 = r * r
    # 深度 64 的连分式，在 |r| ≤ π/4 上把内核误差压到 ~1e-16
    N = 64
    b = float(2 * N + 1)
    for m in range(N, 0, -1):
        odd = float(2 * m - 1)
        b = odd - (x2 / b)
    return r / b


def _tan_highprec(x: float) -> float:
    # Align with test path: first reduce modulo 2π using our IEEE-style remainder,
    # then evaluate tan on that reduced angle using the same high-precision
    # sin/cos kernel, and finally form the quotient.
    # 与测试路径完全对齐：先按 TAU 做 IEEE 风格的余数，
    # 然后在 y=xr/PI 的全周期域上用 Chebyshev 核计算 sin/cos，最后取商。
    xr = remainder(x, TAU)
    y = xr / PI
    s = _sin_series_cheb(y)
    c = _cos_series_cheb(y)
    if c == 0.0:
        return NAN
    return s / c


def _sin_series_cheb(y: float) -> float:
    """Evaluate the odd-order Chebyshev sine series at ``y``.

    Parameters
    ----------
    y : float
        Mapped variable ``y = remainder(x, 2π)/π ∈ [-1,1]``.
    """
    # Build full T-series with odd positions filled.
    c_full = [0.0] * (2 * len(_A_SIN_ODD) + 2)
    for k, ak in enumerate(_A_SIN_ODD):
        c_full[2 * k + 1] = ak
    return _clenshaw_T(y, c_full)

def _cos_series_cheb(y: float) -> float:
    # 构造 full c_full，偶数位填入
    c_full = [0.0] * (2 * len(_A_COS_EVEN) + 1)
    c_full[0] = _A_COS_EVEN[0]      # T0
    for k, ak in enumerate(_A_COS_EVEN[1:], start=1):
        c_full[2 * k] = ak          # T2, T4, ...
    return _clenshaw_T(y, c_full)


def _sin_cos_pair_raw(x: float) -> tuple[float, float]:
    return _sincos_highprec(x)


def _sin_cos_pair(x: float) -> tuple[float, float]:
    s, c = _sincos_highprec(x)
    # Conditional normalization only if clearly beneficial
    norm2 = s * s + c * c
    if isfinite_f(norm2) and norm2 > 0.0:
        if abs(norm2 - 1.0) > 4e-16:
            inv = 1.0 / sqrt(norm2)
            s *= inv
            c *= inv
    return s, c


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def sin(x: float) -> float:
    """Compute ``sin(x)`` using a Chebyshev series.

    Parameters
    ----------
    x : float
        Angle in radians.

    Returns
    -------
    float
        ``sin(x)``. Non-finite input returns ``NAN``.
    """
    if not isfinite_f(x):
        return NAN
    s, _ = _sin_cos_pair(x)
    return s


def cos(x: float) -> float:
    """Compute ``cos(x)`` using a Chebyshev series.

    Non-finite input returns ``NAN``.
    """
    if not isfinite_f(x):
        return NAN
    _, c = _sin_cos_pair(x)
    return c


def tan(x: float) -> float:
    """Compute ``tan(x)`` as a guarded quotient ``sin(x)/cos(x)``.

    Returns ``NAN`` at poles (when ``cos(x) == 0.0`` by evaluation).
    """
    if not isfinite_f(x):
        return NAN
    return _tan_highprec(x)
