# src/algolib/numerics/rounding.py
from algolib.numerics.constants import isfinite_f, NAN
"""Rounding functions for numerical values.

This module provides functions to perform rounding of floating-point numbers
using different strategies.

Functions
---------
round_half_away_from_zero(x)
    Rounds a number to the nearest integer, rounding halves away from zero.

round_even(x)
    Rounds a number to the nearest integer, rounding halves to the nearest even integer.
"""


def round_half_away_from_zero(x: float) -> int:
    """
    Round a number to the nearest integer, rounding halves away from zero.

    Parameters
    ----------
    x : float
        The number to round.

    Returns
    -------
    int
        The rounded integer.

    Examples
    --------
    >>> round_half_away_from_zero(2.5)
    3
    >>> round_half_away_from_zero(-2.5)
    -3
    >>> round_half_away_from_zero(2.3)
    2
    >>> round_half_away_from_zero(-2.3)
    -2
    """
    if x >= 0:
        return int(x + 0.5)
    else:
        return int(x - 0.5)


def round_even(x: float) -> int:
    """
    Round a number to the nearest integer, rounding halves to the nearest even integer.

    This rounding method is also known as "bankers' rounding". When the fractional
    part of the number is exactly 0.5 or -0.5, the number is rounded to the nearest
    even integer.

    Parameters
    ----------
    x : float
        The number to round.

    Returns
    -------
    int
        The rounded integer.

    Examples
    --------
    >>> round_even(2.5)
    2
    >>> round_even(3.5)
    4
    >>> round_even(-2.5)
    -2
    >>> round_even(-3.5)
    -4
    """
    i = int(x)
    frac = x - i
    if x >= 0:
        if frac > 0.5 or (frac == 0.5 and i % 2 != 0):
            return i + 1
        else:
            return i
    else:
        if frac < -0.5 or (frac == -0.5 and i % 2 != 0):
            return i - 1
        else:
            return i

def remainder(x: float, y: float) -> float:
    r"""
    IEEE-754 style remainder r = x - n*y where n is nearest integer to x/y.

    Parameters
    ----------
    x : float
        Dividend.
    y : float
        Divisor.

    Returns
    -------
    float
        The IEEE-754 style remainder of x with respect to y.
        Result is in interval :math:`[-|y|/2, |y|/2]`.
        If |remainder| < 2**-40 * |y|, returns +0.0.
        Returns NaN if x or y is not finite, or y == 0.0.

    Notes
    -----
    - The result r = x - n*y, where n is the integer nearest to x/y;
      if |x/y - n| = 0.5, n is chosen to be even.
    - The result is always in [-|y|/2, |y|/2].
    - For very small |r| (< 2**-40 * |y|), result is +0.0.
    - If x or y is not finite, or y == 0.0, returns NaN.
    """
    if not (isfinite_f(x) and isfinite_f(y)) or y == 0.0:
        return NAN

    ay = abs(y)
    # Truncate quotient toward zero first (robust for very large |x/y|)
    q = x / y
    n = int(q)
    r = x - n * y

    # Now decide whether we are closer to the next integer multiple
    # Compare |r| to |y|/2 with ties-to-even on n.
    ar = r if r >= 0.0 else -r
    h = 0.5 * ay

    if ar > h or (ar == h and (n & 1) != 0):
        # Move r to the nearer representative (and ensure tie goes to even n)
        if r > 0.0:
            r -= ay
        elif r < 0.0:
            r += ay
        else:
            # r == 0 case at exact half and odd n: choose negative/positive consistently
            # Move toward +0 by subtracting ay with sign determined by y
            r = -h if y > 0.0 else h

    # Snap tiny |r| to +0.0 per policy
    if (r if r >= 0.0 else -r) < (2 ** -40) * ay:
        return 0.0

    # Ensure the result lies in [-|y|/2, |y|/2]
    if r > h:
        r -= ay
    elif r < -h:
        r += ay

    return r