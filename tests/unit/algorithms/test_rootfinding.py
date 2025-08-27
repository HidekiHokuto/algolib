# tests/unit/algorithms/test_rootfinding.py
import math
import pytest

from algolib.algorithms.rootfinding import newton
from algolib.numerics.sqrt import newton_sqrt
from algolib.exceptions import ConvergenceError


# ---------- newton(): finite-difference branch (fprime=None) ----------
def test_newton_fd_branch_linear_equation():
    # Solve f(x) = x - 3 = 0 with finite-difference derivative
    root = newton(lambda x: x - 3.0, None, x0=0.0, tol=1e-15, max_iter=50)
    assert abs(root - 3.0) <= 1e-12


# ---------- newton(): dfx == 0.0 branch ----------
def test_newton_derivative_zero_raises():
    # Choose f so that derivative at x0 is exactly 0:
    # f(x) = (x - 1)^2 + 1  -> f'(x) = 2(x - 1)
    # At x0=1: f'(1)=0 and f(1)=1  => should raise before dividing by zero
    with pytest.raises(ConvergenceError):
        newton(lambda x: (x - 1.0) ** 2 + 1.0, lambda x: 2.0 * (x - 1.0), x0=1.0)


# ---------- newton(): not converged within max_iter ----------
def test_newton_not_converged_raises():
    # Make steps extremely small so that convergence isn't reached within 1 iter
    # f(x) = x - 1, f'(x) = tiny -> dx = -(x0-1)/tiny is huge, but we clip iter count
    # Simpler: set max_iter=0 (allowed path) or 1 to force the final raise.
    with pytest.raises(ConvergenceError):
        newton(lambda x: x - 1.0, lambda x: 1e-300, x0=0.0, max_iter=1)


# ---------- newton_sqrt(): special values ----------
def test_newton_sqrt_special_values():
    assert math.isnan(newton_sqrt(float("nan")))
    assert math.isnan(newton_sqrt(-1.0))
    assert newton_sqrt(0.0) == 0.0
    assert newton_sqrt(float("inf")) == float("inf")


# ---------- newton_sqrt(): agreement with math.sqrt ----------
@pytest.mark.parametrize("x", [1e-300, 1e-12, 1.0, 2.0, 4.0, 12345.6789, 1e300])
def test_newton_sqrt_matches_math(x):
    got = newton_sqrt(x)
    exp = math.sqrt(x)
    assert math.isfinite(got) and math.isfinite(exp)
    # Mixed absolute/relative tolerance for extreme magnitudes
    assert abs(got - exp) <= 1e-12 * max(1.0, exp) + 5e-15


# ---------- newton_sqrt(): stress both tiny and huge for exponent-based initial guess ----------
@pytest.mark.parametrize("x", [5e-324,  # subnormal minimum > 0
                               1e-308,  # tiny normal
                               1e-200, 1e-100, 1e100, 1e200, 1e308])
def test_newton_sqrt_extremes(x):
    got = newton_sqrt(x)
    exp = math.sqrt(x)
    assert math.isfinite(got) and math.isfinite(exp)
    assert abs(got - exp) <= 1e-12 * max(1.0, exp) + 5e-15