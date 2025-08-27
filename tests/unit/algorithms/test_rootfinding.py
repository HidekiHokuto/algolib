# tests/unit/algorithms/test_rootfinding.py
import math
import pytest

from algolib.algorithms.rootfinding import newton_sqrt

@pytest.mark.parametrize("x", [0.0, 1e-300, 1e-12, 1.0, 2.0, 4.0, 12345.6789, 1e300])
def test_newton_sqrt_matches_math(x):
    got = newton_sqrt(x)
    exp = math.sqrt(x)
    assert math.isfinite(got) and math.isfinite(exp)
    # 相对+绝对双阈值，避免极小/极大时误判
    assert abs(got - exp) <= 1e-12 * max(1.0, exp) + 5e-15

def test_newton_sqrt_specials():
    assert math.isnan(newton_sqrt(float("nan")))
    assert newton_sqrt(0.0) == 0.0
    assert newton_sqrt(float("inf")) == float("inf")
    assert math.isnan(newton_sqrt(-1.0))