# tests/unit/maths/algebra/test_polynomial.py
import math
import pytest

from algolib.maths.algebra import Polynomial
from algolib.exceptions import InvalidTypeError, InvalidValueError


def test_basic_construction_and_degree():
    p = Polynomial([1, 2, 3])  # 1 + 2x + 3x^2
    assert p.degree == 2
    assert p.coeffs == (1.0, 2.0, 3.0)

def test_strip_trailing_zeros():
    p = Polynomial([0, 0, 5, 0, 0])
    assert p.coeffs == (0.0, 0.0, 5.0)
    assert p.degree == 2

def test_invalid_inputs():
    with pytest.raises(InvalidValueError):
        Polynomial([])  # empty
    with pytest.raises(InvalidTypeError):
        Polynomial([1, object()])  # non-numeric

def test_eval_horner():
    p = Polynomial([1, -3, 2])  # (x-1)(x-2)= x^2 -3x + 1 (注意系数顺序)
    x = 5
    # 1 - 3*5 + 2*25 = 1 - 15 + 50 = 36
    assert p(x) == 36.0

def test_add_sub_mul():
    p = Polynomial([1, 2])      # 1 + 2x
    q = Polynomial([3, 0, 4])   # 3 + 0x + 4x^2
    assert (p + q).coeffs == (4.0, 2.0, 4.0)
    assert (q - p).coeffs == (2.0, -2.0, 4.0)
    # (1+2x)*(3+4x^2) = 3 + 6x + 4x^2 + 8x^3
    assert (p * q).coeffs == (3.0, 6.0, 4.0, 8.0)

def test_derivative_integral_roundtrip():
    p = Polynomial([1, 0, 3])   # 1 + 0x + 3x^2
    dp = p.derivative()         # 0 + 6x
    assert dp.coeffs == (0.0, 6.0)
    ip = dp.integral(c0=5)      # ∫(6x)dx = 3x^2 + C
    assert ip.coeffs == (5.0, 0.0, 3.0)