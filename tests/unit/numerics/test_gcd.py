import pytest
from algolib.numerics import gcd
from algolib.exceptions import InvalidTypeError, InvalidValueError
from math import gcd as math_gcd


def test_gcd_basic_pairs():
    assert gcd(0) == math_gcd(0)
    assert gcd(0, 0) == math_gcd(0, 0)
    assert gcd(7, 0) == math_gcd(7, 0)
    assert gcd(0, 7) == math_gcd(0, 7)
    assert gcd(12, 18) == math_gcd(12, 18)
    assert gcd(-12, 18) == math_gcd(-12, 18)
    assert gcd(12, -18) == math_gcd(12, -18)
    assert gcd(-12, -18) == math_gcd(-12, -18)
    assert gcd(13, 17) == math_gcd(13, 17)


def test_gcd_variadic():
    assert gcd(12, 18, 24) == math_gcd(12, 18, 24)
    assert gcd(21, 14, 7) == math_gcd(21, 14, 7)
    assert gcd(8, 12, 20, 28) == math_gcd(8, 12, 20, 28)


def test_gcd_large_integers():
    a = 12345678901234567890
    b = 98765432109876543210
    assert gcd(a, b) == math_gcd(a, b)


def test_gcd_accepts_bools_as_ints():
    # bool 是 int 子类，行为与 math.gcd 一致
    assert gcd(True, True) == 1
    assert gcd(False, True) == 1
    assert gcd(False, False) == 0


def test_gcd_errors():
    with pytest.raises(InvalidValueError):
        gcd()
    with pytest.raises(InvalidTypeError):
        gcd(3.14)
    with pytest.raises(InvalidTypeError):
        gcd(1, "2")
