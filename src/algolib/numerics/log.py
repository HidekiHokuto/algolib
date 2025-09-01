# src/algolib/numerics/log.py

from __future__ import annotations

from algolib.numerics.exp import exp
from algolib.numerics.stable import frexp
from algolib.numerics.constants import LN2
from algolib.algorithms.rootfinding import newton
from algolib.exceptions import InvalidValueError, InvalidTypeError


def log(x: float, base: float | None = None) -> float:
    r"""
    Natural logarithm :math:`\ln(x)`; if ``base`` is provided, return
    :math:`\log_{\text{base}}(x) = \ln(x) / \ln(\text{base})`.

    Strategy
    --------
    1) **Special-cases**:

       - ``log(NaN) -> NaN``
       - ``log(+inf) -> +inf``
       - ``x == 0.0 -> -inf``
       - ``x < 0`` raises :class:`InvalidValueError`.

    2) **Initial guess via binary scaling**:

       Use our own :func:`frexp` to write ``x = m * 2**e`` with ``m in [0.5, 1)``.
       Then ``ln(x) = ln(m) + e * LN2``. For ``ln(m)`` seed Newton with the short
       series ``log1p(t) ≈ t - t^2/2 + t^3/3`` where ``t = m - 1``.

    3) **Refine with Newton** on ``f(y) = exp(y) - x`` using our own
       :func:`exp` as both function and derivative: ``f'(y) = exp(y)``.

    Parameters
    ----------
    x : float
        Input value (must be positive for a finite result).
    base : float, optional
        If provided, compute ``log(x, base)``. ``base`` must be positive and not
        equal to 1.

    Returns
    -------
    float
        ``ln(x)`` if ``base is None``; otherwise ``ln(x)/ln(base)``.

    Raises
    ------
    InvalidTypeError
        If ``x`` (or ``base`` when provided) is not ``int``/``float`` compatible.
    InvalidValueError
        If ``x <= 0``; or if ``base`` is not positive or equals 1.

    Notes
    -----
    - Implementation avoids :mod:`math` and relies only on the library's
      internal numerics.
    - ``frexp`` handles subnormal inputs; the Newton step quickly brings
      the seed to full precision.
    """
    # Type check (accept ints/bools as numbers)
    if not isinstance(x, (int, float)):
        raise InvalidTypeError(f"log() expects a real number, got {type(x)!r}")

    x = float(x)

    # Specials for x
    if x != x:  # NaN
        return float("nan")
    if x == float("inf"):
        ln_x = float("inf")
    else:
        if x <= 0.0:
            raise InvalidValueError("log() domain error: x must be positive")
        if x == 1.0:
            ln_x = 0.0
        else:
            # frexp-based seed: x = m * 2**e with m in [0.5, 1)
            m, e = frexp(x)

            # m is in [0.5, 1), so t in [-0.5, 0)
            t = m - 1.0
            # cubic seed for log1p(t)
            log_m_seed = t - 0.5 * t * t + (t * t * t) / 3.0

            y0 = e * LN2 + log_m_seed

            # Newton refinement: f(y) = exp(y) - x, f'(y) = exp(y)
            root = newton(
                lambda y: exp(y) - x,
                lambda y: exp(y),
                x0=y0,
                tol=1e-15,
                max_iter=50,
            )
            ln_x = float(root)

    # If base is not specified, return ln(x)
    if base is None:
        return ln_x

    # Validate and compute ln(base) using the same API (recursive, but base branch only)
    if not isinstance(base, (int, float)):
        raise InvalidTypeError(f"log() base must be a real number, got {type(base)!r}")

    base_val = float(base)

    if base_val != base_val:  # NaN
        return float("nan")
    if base_val <= 0.0 or base_val == 1.0:
        raise InvalidValueError("log() base must be positive and not equal to 1")

    ln_base = log(base_val)  # recursive call with base=None path

    return ln_x / ln_base

def log10(x: float) -> float:
    r"""
    Base-10 logarithm of ``x``.

    Equivalent to ``log(x, 10.0)``.
    """
    return log(x, 10.0)

def log2(x: float) -> float:
    r"""
    Base-2 logarithm of ``x``.

    Equivalent to ``log(x, 2.0)``.
    """
    return log(x, 2.0)


if __name__ == "__main__":
    print("ln(2e5)=", log(200000))
    print("log10(2e5)=", log(200000, 10))