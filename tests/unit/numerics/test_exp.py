# tests/unit/numerics/test_exp.py
import math
import pytest
from algolib.numerics.exp import exp

@pytest.mark.parametrize("x", [0, 1, -1, 10, -10, 100])
def test_exp_typical_values(x):
    expected = math.exp(x)
    result = exp(x)
    assert math.isclose(result, expected, rel_tol=1e-12, abs_tol=1e-12)

@pytest.mark.parametrize("x,special_expected", [
    (float("nan"), float("nan")),
    (float("inf"), float("inf")),
    (float("-inf"), 0.0),
])
def test_exp_special_values(x, special_expected):
    result = exp(x)
    if math.isnan(special_expected):
        assert math.isnan(result)
    else:
        assert result == special_expected