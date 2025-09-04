# src/algolib/numerics/stable.py

from __future__ import annotations
from typing import Iterable
from algolib.numerics.sqrt import newton_sqrt
from algolib.exceptions import InvalidTypeError, InvalidValueError


def hypot(x: float, y: float) -> float:
    r"""
    Stable :math:`\sqrt{x^2 + y^2}` with overflow/underflow protections.
    """
    x, y = abs(x), abs(y)
    if x < y:
        x, y = y, x
    if x == 0.0:
        return 0.0
    r = y / x  # |r| <= 1
    return x * newton_sqrt(1.0 + r * r)


def hypot_n(*xs: float) -> float:
    r"""
    Stable Euclidean norm for :math:`N` components:
    :math:`\sqrt{\sum_i xs[i]^2}`.
    """
    acc = 0.0
    for v in xs:
        acc = hypot(acc, float(v))
    return acc


def hypot_iter(vals: Iterable[float]) -> float:
    acc = 0.0
    for v in vals:
        acc = hypot(acc, float(v))
    return acc


def gcd(*args: int) -> int:
    r"""
    Greatest common divisor for one or more integers.

    Parameters
    __________
    *args : int
        One or more integer values. Booleans are accepted (as integers).

    Returns
    -------
    int
        Non-negative GCD. By convention, gcd(0, 0) -> 0.

    Raises
    ------
    InvalidValueError
        If no arguments are provided.
    InvalidTypeError
        If any argument is not an integer.
    """
    if not args:
        raise InvalidValueError("gcd() expected at least 1 argument.")

    g: int = 0
    for x in args:
        if not isinstance(x, int):
            raise InvalidTypeError(
                f"gcd() only accepts integers, got {type(x).__name__}."
            )
        a = x if x >= 0 else -x
        if a == 0:
            # gcd(g, 0) = g
            continue
        if g == 0:
            g = a
            continue
        # Euclidean algorithm
        b = a
        while b:
            g, b = b, g % b

    return g


def frexp(x: float) -> tuple[float, int]:
    r"""
    Decompose ``x`` into ``(m, e)`` such that :math:`x = m \cdot 2^e` with
    :math:`0.5 \leq |m| < 1`, except for ``x == 0.0`` where ``(±0.0, 0)`` is
    returned (sign of zero preserved).

    Specials (match CPython :func:`math.frexp` behaviour we emulate):
    - ``frexp(±inf) -> (±inf, 0)``
    - ``frexp(nan)  -> (nan, 0)``
    """
    # type check
    if not isinstance(x, (int, float, bool)):
        raise InvalidTypeError(f"frexp() expected float, got {type(x)}")
    xf = float(x)

    # specials: NaN / ±Inf / ±0.0 (preserve signed zero)
    if xf != xf:  # NaN
        return (xf, 0)
    if xf == float("inf") or xf == float("-inf"):
        return (xf, 0)
    if xf == 0.0:
        return (xf, 0)

    # Use hex representation: '[-]0x1.mmmmmmp±e' for normals,
    # subnormals may appear like '[-]0x0.mmmmmmp-1022'.
    hs = xf.hex()  # e.g., '-0x1.8p-1'
    neg = hs[0] == "-"
    if neg:
        hs = hs[1:]
    # split mantissa and binary exponent
    mant_str, exp_str = hs.split("p")
    bexp = int(exp_str)  # binary exponent (base-2)
    assert mant_str.startswith("0x")
    mant_str = mant_str[2:]  # like '1.8' or '0.0001'
    if "." in mant_str:
        ip, fp = mant_str.split(".")
    else:
        ip, fp = mant_str, ""

    # parse hex fraction to a Python float exactly
    ip_val = int(ip, 16) if ip else 0
    frac_val = 0.0
    for i, ch in enumerate(fp, start=1):
        frac_val += int(ch, 16) / (16.0**i)
    mant = ip_val + frac_val  # in [0, 2)

    # Now xf = sign * mant * 2**bexp
    sign = -1.0 if neg else 1.0

    # Normalize mantissa into [0.5, 1)
    # (for normals mant>=1; for subnormals mant<1)
    if mant == 0.0:
        # Should not happen for non-zero xf, but guard anyway
        return (sign * 0.0, 0)

    while mant >= 1.0:
        mant *= 0.5
        bexp += 1
    while mant < 0.5:
        mant *= 2.0
        bexp -= 1

    m = sign * mant
    return (m, bexp)


def ldexp(m: float, e: int) -> float:
    r"""
    Inverse of :func:`frexp`: return ``m * 2**e`` using only multiplications
    (no :mod:`math`, no :mod:`struct`). Propagates NaN/Inf, preserves signed zero.
    """
    if not isinstance(m, (int, float, bool)):
        raise InvalidTypeError(f"ldexp() expected float, got {type(m)}")
    if not isinstance(e, int):
        raise InvalidTypeError(f"ldexp() exponent must be int, got {type(e)}")

    mf = float(m)
    # NaN/Inf propagate; ±0.0 returns ±0.0 regardless of e
    if mf != mf or mf == float("inf") or mf == float("-inf") or mf == 0.0:
        return mf

    # exponentiation by squaring on base 2.0 or 0.5 depending on e sign
    n = e if e >= 0 else -e
    base = 2.0 if e >= 0 else 0.5
    scale = 1.0
    while n > 0:
        if n & 1:
            scale *= base
        base *= base
        n >>= 1
    return mf * scale
