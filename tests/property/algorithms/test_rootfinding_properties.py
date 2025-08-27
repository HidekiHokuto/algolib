from hypothesis import given, strategies as st
import math
from algolib.algorithms.rootfinding import newton_sqrt
from algolib.numerics.stable import hypot

safe = st.floats(allow_nan=False, allow_infinity=False, width=64, min_value=0.0, max_value=1e308)

@given(x=safe)
def test_sqrt_property_inverse(x):
    y = newton_sqrt(x)
    # y^2 ≈ x
    assert abs(y*y - x) <= 1e-12 * max(1.0, x) + 1e-12

@given(x=st.floats(0, 1e308), y=st.floats(0, 1e308))
def test_hypot_symmetry(x, y):
    assert hypot(x, y) == hypot(y, x)