# src/algolib/numerics/hyper.py
r"""
Hyperbolic functions (pure implementation).

This module provides ``sinh``, ``cosh`` and ``tanh`` implemented in pure
Python, without importing :mod:`math`. It relies on the local ``exp`` kernel
and uses cancellation-safe formulas.

Notes
-----

- Non-finite input (NaN/:math:`\pm` Inf) returns NaN, to align with algolib's numerics
    contract.
- ``tanh`` uses the stable identity with ``exp(-2|x|)`` to avoid overflow and
    catastrophic cancellation.
- ``sinh``/``cosh`` are implemented with reciprocal forms and simple small-``x``
    fallbacks.

These functions live as normal numerics utilities (not bebind the backend
switch), similar to ``sqrt`` and the stable helpers.
"""

from __future__ import annotations

from algolib.numerics.constants import INF, NAN, isfinite_f
from algolib.numerics.exp import exp
from algolib.numerics.sqrt import newton_sqrt as sqrt
from algolib.numerics.log import log
from algolib.exceptions import InvalidValueError

__all__ = ["sinh", "cosh", "tanh"]


def _isfinite(x: float) -> bool:
    r"""
    Lightweight finiteness check without :mod:`math`.

    Parameters
    ----------
    x : float
        Value to test.

    Returns
    -------
    bool
        ``True`` if finite, else ``False``.
    """
    return (x == x) and (-INF < x < INF)


def _abs(x: float) -> float:
    return -x if x < 0.0 else x


def sinh(x: float) -> float:
    r"""
    Hyperbolic sine.

    Parameters
    ----------
    x : float
        Real input.

    Returns
    -------
    float
        ``sinh(x)``.

    Notes
    -----
    - Non-finite input NaN.
    - For very small ``|x|`` we return ``x`` (first-order Taylor) to avoid cancellation when forming ``exp(x) - exp(-x)``.
    - For large ``|x|`` we use the dominant term ``0.5 * exp(|x|)`` with sign.
    """
    if not _isfinite(x):
        return NAN
    ax = _abs(x)
    if ax < 1e-8:
        return x
    if ax > 350.0:
        ex = exp(ax)
        if ex != ex or ex == INF:
            return (1.0 if x >= 0.0 else -1.0) * INF
        return (1.0 if x >= 0.0 else -1.0) * (0.5 * ex)
    ex = exp(x)
    return 0.5 * (ex - 1.0 / ex)


def cosh(x: float) -> float:
    """Hyperbolic cosine.

    Parameters
    ----------
    x : float
        Real input.

    Returns
    -------
    float
        ``cosh(x)``.

    Notes
    -----
    - Non-finite input returns NaN.
    - For small ``|x|`` we use ``1 + x**2/2``.
    - For large ``|x|`` we use the dominant term ``0.5 * exp(|x|)``.
    """

    if not _isfinite(x):
        return NAN
    ax = _abs(x)
    if ax < 1e-8:
        return 1.0 + 0.5 * x * x
    if ax > 350.0:
        ex = exp(ax)
        if ex != ex or ex == INF:
            return INF
        return 0.5 * ex
    # Use reciprocal form in the moderate range to better preserve cosh^2 - sinh^2 ≈ 1
    ex = exp(x)
    return 0.5 * (ex + 1.0 / ex)


def tanh(x: float) -> float:
    """Hyperbolic tangent with stable branches.

    Parameters
    ----------
    x : float
        Input value.

    Returns
    -------
    float
        tanh(x). For non-finite inputs, returns NaN per algolib convention.

    Notes
    -----
    We use odd-function reduction: tanh(-x) = -tanh(x). For x ≥ 0, compute:
    tanh(x) = (e^{2x} - 1) / (e^{2x} + 1)
    which avoids catastrophic cancellation for moderate/large x. For very
    large x we directly saturate to 1.0 to avoid overflow.
    """

    # Non-finite policy
    if not isfinite_f(x):
        return NAN

    if x == 0.0:
        # Preserve signed zero behavior
        return x

    # Odd reduction: work on positive magnitude, restore sign at the end.
    sgn = 1.0 if x > 0.0 else -1.0
    ax = x if x > 0.0 else -x

    # For very large |x|, tanh(|x|) ~ 1 within double precision.
    # Threshold 20 is conservative and avoids overflow in exp(2*ax).
    if ax > 20.0:
        return sgn * 1.0

    # Compute using (e^{2a} - 1)/(e^{2a} + 1) for a = |x|
    e2a = exp(2.0 * ax)
    t = (e2a - 1.0) / (e2a + 1.0)
    return sgn * t


def asinh(x: float) -> float:
    r"""
    Inverse hyperbolic sine.

    Parameters
    ----------
    x : float
        Real input.

    Returns
    -------
    float
        ``asinh(x)``.

    Notes
    -----
    - Non-finite input returns NaN, per algolib contract.
    - Preserves signed zero: asinh(±0.0) = ±0.0.
    - Implemented using the stable form
      ``sgn(x) * log(|x| + sqrt(x**2 + 1))``.
    """

    # Non-finite policy
    if not isfinite_f(x):
        return NAN

    if x == 0.0:
        return x

    sgn = 1.0 if x > 0.0 else -1.0
    ax = x if x > 0.0 else -x

    return sgn * log(ax + sqrt(ax**2 + 1))


def acosh(x: float) -> float:
    r"""
    Inverse hyperbolic cosine.

    Parameters
    ----------
    x : float
        Real input.

    Returns
    -------
    float
        ``acosh(x)``.

    Notes
    -----
    - Domain: ``x >= 1``.
    - Non-finite input returns NaN, per algolib contract.
    - Out-of-domain inputs (``x < 1``) return NaN (no exceptions).
    - Preserves floating semantics: ``acosh(1.0) = 0.0``.
    - Implemented with the cancellation-safe form:
      ``acosh(x) = log(x + sqrt((x - 1) * (x + 1)))``,
      which is more stable near ``x ≈ 1`` than ``sqrt(x**2 - 1)``.

    """
    if not isfinite_f(x):
        return NAN

    if x < 1.0:
        return NAN
    if x == 1.0:
        return 0.0

    # Stable form near x ≈ 1: sqrt((x - 1)*(x + 1))
    t = sqrt((x - 1.0) * (x + 1.0))
    return log(x + t)


def atanh(x: float) -> float:
    r"""
    Inverse hyperbolic tangent.

    Parameters
    ----------
    x : float
        Real input.

    Returns
    -------
    float
        ``atanh(x)``.

    Notes
    -----
    - Domain: ``-1 < x < 1``.
    - Non-finite input returns NaN, per algolib contract.
    - Out-of-domain inputs (``|x| >= 1``) return NaN (no exceptions).
    - Preserves signed zero: ``atanh(±0.0) = ±0.0``.
    - Implemented as ``sgn(x) * 0.5 * log((1 + |x|) / (1 - |x|))``,
      which is equivalent to the usual formula while keeping sign handling explicit.

    """
    if not isfinite_f(x):
        return NAN
    if not (-1.0 < x < 1.0):
        return NAN

    if x == 0.0:
        # Preserve signed zero
        return x

    sgn = 1.0 if x > 0.0 else -1.0
    ax = x if x > 0.0 else -x
    return sgn * 0.5 * log((1.0 + ax) / (1.0 - ax))
