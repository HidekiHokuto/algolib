import math
from hypothesis import given, strategies as st, settings
from algolib.maths.algebra.polynomial import Polynomial
from algolib.numerics.diff import derivative_cstep

coeffs_strat = st.lists(
    st.floats(allow_nan=False, allow_infinity=False, min_value=-1e6, max_value=1e6),
    min_size=1,
    max_size=20,
)

x_strat = st.floats(
    allow_nan=False, allow_infinity=False, min_value=-1e2, max_value=1e2
)


@given(a=coeffs_strat, x=x_strat)
@settings(max_examples=100)
def test_derivative_matches_cstep(a, x):
    p = Polynomial(a)
    dp = p.derivative()
    # Compare analytical derivative with complex-step numerical derivative
    assert math.isclose(
        dp(x), derivative_cstep(lambda t: p(t), x), rel_tol=5e-8, abs_tol=1e-10
    )


@given(a=coeffs_strat, x=x_strat)
@settings(max_examples=100)
def test_eval_is_finite(a, x):
    p = Polynomial(a)
    y = p(x)
    if isinstance(y, complex):
        assert math.isfinite(y.real) and math.isfinite(y.imag)
    else:
        assert math.isfinite(y)
