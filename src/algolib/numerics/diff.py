from __future__ import annotations
import math
from typing import Callable

def derivative_cstep(f: Callable[[complex], complex], x: float, h: float = 1e-20) -> float:
    """
    Complex-step derivative approximation:

        f'(x) ≈ Im(f(x + i*h)) / h

    Requires f to support complex input. Very stable since
    there is no subtractive cancellation.
    """
    return (f(x + 1j * h)).imag / h

def derivative_central(
    f: Callable[[float], float],
    x: float,
    *,
    h: float | None = None,
    max_iter: int = 6,
) -> float:
    """
    Central difference derivative approximation with Richardson extrapolation.

    Useful when f does not support complex input.
    Accuracy is O(h^2) per step and improved by extrapolation.
    """
    scale = max(1.0, abs(x))
    h = 1e-3 * scale if h is None else h

    T = []
    for k in range(max_iter):
        hk = h / (2 ** k)
        T0k = (f(x + hk) - f(x - hk)) / (2.0 * hk)
        T.append([T0k])
        for j in range(1, k + 1):
            num = T[k][j - 1] - T[k - 1][j - 1]
            T[k].append(T[k][j - 1] + num / (4 ** j - 1))
    return T[-1][-1]