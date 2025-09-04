from __future__ import annotations
import math
from algolib.exceptions import InvalidTypeError, InvalidValueError

__all__ = ["is_prime"]


def is_prime(n: int) -> bool:
    r"""Check whether an integer is a prime using the :math:`6k \pm 1` optimization.

    Parameters
    ----------
    n : int
        Non-negative integer to test.

    Returns
    -------
    bool
        True if `n` is prime; False otherwise.

    Raises
    ------
    InvalidTypeError
        If `n` is not int.
    InvalidValueError
        If `n` is negative.
    """
    if not isinstance(n, int):
        raise InvalidTypeError(f"n must be int, got {type(n).__name__}")
    if n < 0:
        raise InvalidValueError(f"n must be non-negative, got {n}")
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    limit = math.isqrt(n)
    i = 5
    while i <= limit:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True
