import pytest
from hypothesis import given, strategies as st
import math
from algolib.numerics.exp import exp

@given(st.floats(min_value=-700, max_value=700, allow_nan=False, allow_infinity=False))
def test_exp_property_random_finite(x):
    # math.exp may still overflow for x close to 700, so restrict to safe range
    try:
        expected = math.exp(x)
    except OverflowError:
        pytest.skip("math.exp overflowed")
    result = exp(x)
    assert math.isclose(result, expected, rel_tol=1e-12, abs_tol=1e-12)