# tests/maths/number_theory/test_prime.py
import math
import pytest
from algolib.maths.number_theory import is_prime
from algolib.exceptions import InvalidTypeError, InvalidValueError

@pytest.mark.parametrize(
    "n, expected",
    [
        (0, False), (1, False), (2, True), (3, True), (4, False),
        (5, True), (27, False), (87, False), (563, True), (2999, True),
    ],
)
def test_known_values(n, expected):
    assert is_prime(n) is expected

@pytest.mark.parametrize("bad", [1.5, "7", None, complex(2, 0)])
def test_invalid_type(bad):
    with pytest.raises(InvalidTypeError) as e:
        is_prime(bad)  # type: ignore[arg-type]
    assert "n must be int" in str(e.value)

@pytest.mark.parametrize("bad", [-1, -10, -999999])
def test_invalid_value(bad):
    with pytest.raises(InvalidValueError) as e:
        is_prime(bad)
    assert "non-negative" in str(e.value)

def slow_reference_is_prime(n: int) -> bool:
    if n < 2:
        return False
    for d in range(2, math.isqrt(n) + 1):
        if n % d == 0:
            return False
    return True

def test_compare_with_reference_small_range():
    for n in range(0, 5000):
        assert is_prime(n) == slow_reference_is_prime(n)