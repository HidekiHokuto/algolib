# src/algolib/numerics/sqrt.py
from __future__ import annotations
from algolib.exceptions import ConvergenceError


def newton_sqrt(x: float, *, tol: float = 1e-15, max_iter: int = 100) -> float:
    """
    Square root via Newton-Raphson iteration (overflow-safe update).

    Notes
    -----
    Uses the overflow-safe iteration y_{k+1} = 0.5 * (y_k + x / y_k).
    The initial guess is derived from the binary exponent of `x`
    (parsed via float.hex) to match the magnitude of sqrt(x).
    """
    # Specials
    if x != x:  # NaN
        return float("nan")
    if x < 0.0:
        return float("nan")
    if x == 0.0:
        return 0.0
    if x == float("inf"):
        return float("inf")

    # Initial guess from binary exponent: float.hex(x) -> '0x1.23p+e'
    hx = float.hex(x)
    try:
        p = int(hx.split('p')[-1])
    except Exception:
        p = 0
    y = 2.0 ** (p // 2)
    if y == 0.0:
        y = 1.0  # safety for subnormals

    # Newton iteration without squaring (avoids overflow)
    for _ in range(max_iter):
        prev = y
        y = 0.5 * (y + x / y)
        if abs(y - prev) <= tol * max(1.0, y):
            return y
    return y