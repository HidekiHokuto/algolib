# tests/maths/complex/test_core.py
import math
import pytest

from algolib.core.complex import Complex
from algolib.exceptions import InvalidTypeError, InvalidValueError


def test_ctor_and_float_coercion():
    z = Complex(1, -2)
    assert z.re == 1.0 and z.im == -2.0  # coerced to float
    z2 = Complex(3, 4.0)
    assert isinstance(z2.re, float) and isinstance(z2.im, float)

@pytest.mark.parametrize("bad", [
    ("1", 2), (1, "2"), (None, 0), (object(), 0), (1, object())
])
def test_ctor_type_error(bad):
    with pytest.raises(InvalidTypeError):
        Complex(*bad)  # type: ignore[arg-type]

def test_from_cartesian_and_iterable():
    z1 = Complex.from_cartesian(3, -4)
    z2 = Complex.from_iterable((3, -4))
    assert z1 == z2 == Complex(3, -4)

@pytest.mark.parametrize("bad_iter", [
    (1,), (1, 2, 3), "12", [1, "x"], object()
])
def test_from_iterable_errors(bad_iter):
    if isinstance(bad_iter, (tuple, list)) and len(bad_iter) == 2 and any(
        not isinstance(x, (int, float)) for x in bad_iter
    ):
        # 解包成功，但内部构造会因类型报错
        with pytest.raises(InvalidTypeError):
            Complex.from_iterable(bad_iter)  # type: ignore[arg-type]
    else:
        # 解包本身会失败（长度不等于2或不可迭代）
        with pytest.raises(InvalidTypeError):
            Complex.from_iterable(bad_iter)  # type: ignore[arg-type]

def test_from_polar_roundtrip_and_errors():
    r, theta = 5.0, 1.234
    z = Complex.from_polar(r, theta)
    r2, th2 = z.to_polar()
    assert math.isclose(r2, r, rel_tol=1e-12, abs_tol=1e-12)

    # 角度对 2π 等价，做归一化再比
    def norm(t): return (t + math.pi) % (2 * math.pi) - math.pi
    assert math.isclose(norm(th2), norm(theta), rel_tol=1e-12, abs_tol=1e-12)

    with pytest.raises(InvalidValueError):
        Complex.from_polar(-1, 0)

    with pytest.raises(InvalidTypeError):
        Complex.from_polar("1", 0)  # type: ignore[arg-type]

def test_modulus_argument_conjugate_normalize():
    z = Complex(3, 4)
    assert math.isclose(z.modulus(), 5.0, rel_tol=0, abs_tol=1e-12)
    assert math.isclose(z.argument(), math.atan2(4, 3), rel_tol=1e-12, abs_tol=1e-12)

    zc = z.conjugate()
    assert zc.re == 3.0 and zc.im == -4.0

    u = z.normalized()
    assert math.isclose(u.modulus(), 1.0, rel_tol=1e-12, abs_tol=1e-12)
    # 方向一致：比例相同
    assert math.isclose(u.re / z.re, u.im / z.im, rel_tol=1e-12, abs_tol=1e-12)

    with pytest.raises(InvalidValueError):
        Complex(0, 0).normalized()

@pytest.mark.parametrize(
    "a,b,expected",
    [
        (Complex(1, 2), Complex(3, 4), Complex(4, 6)),
        (Complex(-1, 0), Complex(1, 0), Complex(0, 0)),
    ],
)
def test_add(a, b, expected):
    assert a + b == expected

@pytest.mark.parametrize(
    "a,b,expected",
    [
        (Complex(1, 2), Complex(3, 4), Complex(-2, -2)),
        (Complex(5, 0), Complex(1, 7), Complex(4, -7)),
    ],
)
def test_sub(a, b, expected):
    assert a - b == expected

@pytest.mark.parametrize(
    "a,b,expected",
    [
        # (a+bi)(c+di) = (ac - bd) + (ad + bc)i
        (Complex(1, 2), Complex(3, 4), Complex(1*3 - 2*4, 1*4 + 2*3)),
        (Complex(-2, 5), Complex(0, 1), Complex(-5, -2)),  # 乘 i 相当于旋转 90°
    ],
)
def test_mul(a, b, expected):
    assert a * b == expected

@pytest.mark.parametrize(
    "a,b,expected",
    [
        # (a+bi)/(c+di) = ((ac+bd) + (bc-ad)i) / (c^2 + d^2)
        (Complex(1, 2), Complex(3, 4),
         Complex((1*3 + 2*4) / (3*3 + 4*4), (2*3 - 1*4) / (3*3 + 4*4))),
        (Complex(-2, 5), Complex(0, 1), Complex(5, 2)),  # 除以 i 等于乘以 -i
    ],
)
def test_truediv(a, b, expected):
    out = a / b
    assert math.isclose(out.re, expected.re, rel_tol=1e-12, abs_tol=1e-12)
    assert math.isclose(out.im, expected.im, rel_tol=1e-12, abs_tol=1e-12)

def test_divide_by_zero():
    with pytest.raises(InvalidValueError):
        _ = Complex(1, 2) / Complex(0, 0)

def test_unary_and_abs_and_str_repr():
    z = Complex(1.25, -2.5)
    assert (-z) == Complex(-1.25, 2.5)
    assert math.isclose(abs(Complex(3, 4)), 5.0, rel_tol=0, abs_tol=1e-12)

    s = str(z)
    assert "1.25" in s and "2.5" in s and "i" in s

    r = repr(z)
    assert r.startswith("Complex(") and "re=" in r and "im=" in r

def test_eq_and_almost_equal():
    a = Complex(1.0, -0.0)
    b = Complex(1.0, 0.0)
    assert a == b  # +0.0 == -0.0 在浮点上为 True

    c = Complex(1.000000000001, 2.0)
    d = Complex(1.0, 2.0)
    assert c != d  # __eq__ 是精确相等
    assert c.almost_equal(d, tol=1e-9)

def test_to_tuple_and_str_positive_im():
    z = Complex(1.5, 2.25)
    # to_tuple 覆盖
    assert z.to_tuple() == (1.5, 2.25)
    # __str__ 正号分支（我们之前只测了负号）
    s = str(z)
    assert "1.5" in s and "+ 2.25" in s and s.endswith("i")

def test_almost_equal_with_non_complex_and_eq_non_complex():
    z = Complex(1, 2)
    # almost_equal 对非 Complex 的早退 False
    assert z.almost_equal(123) is False  # type: ignore[arg-type]
    # __eq__ 遇到非 Complex 触发 NotImplemented 路径，== 结果应为 False
    assert (z == 123) is False  # type: ignore[comparison-overlap]

@pytest.mark.parametrize("op", ["add", "sub", "mul", "truediv"])
def test_binary_ops_type_errors(op):
    a = Complex(1, 2)
    other = 3  # 非 Complex
    with pytest.raises(InvalidTypeError):
        if op == "add":
            _ = a + other  # type: ignore[operator]
        elif op == "sub":
            _ = a - other  # type: ignore[operator]
        elif op == "mul":
            _ = a * other  # type: ignore[operator]
        else:
            _ = a / other  # type: ignore[operator]

def test_from_polar_theta_type_error():
    with pytest.raises(InvalidTypeError):
        Complex.from_polar(1.0, "ang")  # type: ignore[arg-type]

def almost(a, b, tol=1e-12):
    return abs(a - b) <= tol

def test_div_branch_c_dominant():
    # |c| >= |d| 分支：c 的绝对值更大
    z = Complex(1.0, 2.0)
    w = Complex(3.0, 0.1)   # |3.0| > |0.1|
    got = z / w
    ref = complex(1.0, 2.0) / complex(3.0, 0.1)
    assert almost(got.re, ref.real)
    assert almost(got.im, ref.imag)

def test_div_branch_d_dominant():
    # |d| > |c| 分支：d 的绝对值更大
    z = Complex(1.0, 2.0)
    w = Complex(0.1, 3.0)   # |3.0| > |0.1|
    got = z / w
    ref = complex(1.0, 2.0) / complex(0.1, 3.0)
    assert almost(got.re, ref.real)
    assert almost(got.im, ref.imag)