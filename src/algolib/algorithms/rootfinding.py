# src/algolib/algorithms/rootfinding.py
from __future__ import annotations
from typing import Callable, Optional
from algolib.exceptions import ConvergenceError

def newton(
    f: Callable[[float], float],
    fprime: Optional[Callable[[float], float]],
    x0: float,
    *,
    tol: float = 1e-15,
    max_iter: int = 100,
    fd_eps: float = 1e-8,
) -> float:
    r"""
    General Newton-Raphson root finding.

    Parameters
    ----------
    f : Callable[[float], float]
        Function whose root is to be found.
    fprime : Callable[[float], float] or None
        Derivative of ``f``. If ``None``, a forward finite-difference
        approximation is used.
    x0 : float
        Initial guess.
    tol : float, optional
        Relative tolerance for convergence. Defaults to ``1e-15``.
    max_iter : int, optional
        Maximum number of iterations. Defaults to ``100``.
    fd_eps : float, optional
        Step size used by the finite-difference derivative when ``fprime``
        is ``None``. Defaults to ``1e-8``.
    
    Returns
    -------
    float
        Approximate root of :math:`f(x) = 0`.

    Raises
    ------
    ConvergenceError
        If convergence is not reached within ``max_iter`` iterations
        or the derivative becomes zero.

    Notes
    -----
    The update is :math:`x_{n+1} = x_n - f(x_n) / f'(x_n)`. Convergence is
    tested using ``abs(dx) <= tol * max(1.0, abs(x_{n+1}))``.
    """
    x = float(x0)
    for i in range(max_iter):
        fx = f(x)
        if fprime is None:
            # Scale step by current magnitude to reduce catastrophic cancellation
            h = fd_eps * max(1.0, abs(x))
            dfx = (f(x + h) - fx) / h
        else:
            dfx = fprime(x)
        if dfx == 0.0:
            raise ConvergenceError(iterations=i, residual=fx, target_tol=tol)
        dx = -fx / dfx
        x_new = x + dx
        if abs(dx) <= tol * max(1.0, abs(x_new)):
            return x_new
        x = x_new
    # Not converged
    raise ConvergenceError(iterations=max_iter, residual=abs(f(x)), target_tol=tol)


def newton_sqrt(x: float, *, tol: float = 1e-15, max_iter: int = 100) -> float:
    """
    Square root via Newton–Raphson iteration (overflow-safe update).

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