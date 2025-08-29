# tests/unit/numerics/test_rounding.py

import pytest
from algolib.numerics.rounding import round_half_away_from_zero, round_even

@pytest.mark.parametrize("input_val, expected", [
    (2.5, 3),
    (-2.5, -3),
    (2.3, 2),
    (-2.3, -2),
    (0.5, 1),
    (-0.5, -1),
    (1.5, 2),
    (-1.5, -2),
    (0.0, 0),
    (3.7, 4),
    (-3.7, -4),
])
def test_round_half_away_from_zero(input_val, expected):
    assert round_half_away_from_zero(input_val) == expected

@pytest.mark.parametrize("input_val", [
    2.5,
    3.5,
    -2.5,
    -3.5,
    1.5,
    4.5,
    -1.5,
    -4.5,
    0.5,
    -0.5,
    2.3,
    -2.3,
    3.7,
    -3.7,
    0.0,
])
def test_round_even_matches_builtin_round(input_val):
    assert round_even(input_val) == round(input_val)