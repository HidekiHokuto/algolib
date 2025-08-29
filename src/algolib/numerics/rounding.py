# src/algolib/numerics/rounding.py
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