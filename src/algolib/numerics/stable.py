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
    r = y / x # |r| <= 1
    return x * newton_sqrt(1.0 + r*r)

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
            raise InvalidTypeError(f"gcd() only accepts integers, got {type(x).__name__}.")
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