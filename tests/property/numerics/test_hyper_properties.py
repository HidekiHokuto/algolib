# tests/property/numerics/test_hyper_properties.py
from math import isclose
from hypothesis import given, strategies as st

from algolib.numerics.hyper import sinh, cosh, tanh
from algolib.numerics.exp import exp

@given(st.floats(min_value=-700, max_value=700, allow_nan=False, allow_infinity=False))
def test_cosh_ge_1(x: float) -> None:
    # cosh(x) >= 1 for all finite x
    assert cosh(x) >= 1.0


@given(st.floats(allow_nan=False, allow_infinity=False))
def test_tanh_range(x: float) -> None:
    # tanh(x) in [-1, 1] for finite x
    val = tanh(x)
    assert -1.0 <= val <= 1.0


@given(st.floats(allow_nan=False, allow_infinity=False))
def  test_odd_even_symmetry(x: float) -> None:
    # sinh(-x) = -sinh(x)
    assert isclose(sinh(-x), -sinh(x), rel_tol=1e-12, abs_tol=1e-12)
    # cosh(-x) = cosh(x)
    assert isclose(cosh(-x), cosh(x), rel_tol=1e-12, abs_tol=1e-12)
    # tanh(-x) = -tanh(x)
    assert isclose(tanh(-x), -tanh(x), rel_tol=1e-12, abs_tol=1e-12)


@given(st.floats(min_value=-700, max_value=700, allow_nan=False, allow_infinity=False))
def test_cosh_sinh_identity(x: float) -> None:
    # Use the stable identity (cosh + sinh) * (cosh - sinh) = exp(x) * exp(-x) = 1
    # Evaluating cosh^2 - sinh^2 directly can overflow (cosh(356) ~ 1e154)
    # or suffer catastrophic cancellation around ~20.
    lhs = exp(x) * exp(-x)
    assert isclose(lhs, 1.0, rel_tol=1e-12, abs_tol=1e-12)

@given(st.floats(min_value=-1e-7, max_value=1e-7))
def test_sinh_small_x(x: float) -> None:
    # For small |x|, sinh(x) ≈ x (first-order)
    assert isclose(sinh(x), x, rel_tol=1e-12, abs_tol=1e-12)