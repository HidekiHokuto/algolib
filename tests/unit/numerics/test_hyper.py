# tests/unit/numerics/test_hyper.py
import math
import pytest

# 测试只对比“有限输入”的数值等价；非有限输入按 algolib 约定应返回 NaN
from algolib.numerics.hyper import sinh, cosh, tanh

REL = 1e-12
ABS = 1e-12


@pytest.mark.parametrize(
    "x", [0.0, 1e-12, -1e-12, 1.0, -1.0, 10.0, -10.0, 350.0, -350.0]
)
def test_sinh_matches_math(x):
    got = sinh(x)
    exp = math.sinh(x)
    assert math.isclose(got, exp, rel_tol=REL, abs_tol=ABS)


@pytest.mark.parametrize(
    "x", [0.0, 1e-12, -1e-12, 1.0, -1.0, 10.0, -10.0, 350.0, -350.0]
)
def test_cosh_matches_math(x):
    got = cosh(x)
    exp = math.cosh(x)
    assert math.isclose(got, exp, rel_tol=REL, abs_tol=ABS)


@pytest.mark.parametrize(
    "x", [0.0, 1e-12, -1e-12, 1.0, -1.0, 10.0, -10.0, 350.0, -350.0]
)
def test_tanh_matches_math(x):
    got = tanh(x)
    exp = math.tanh(x)
    assert math.isclose(got, exp, rel_tol=REL, abs_tol=ABS)


def test_identity_cosh2_minus_sinh2_is_one():
    # 在中等范围内验证 cosh^2 - sinh^2 = 1
    # 直接做 (cosh^2 - sinh^2) 在 |x| 较大时会有数值消消乐；
    # 用等价但更稳定的形式 (cosh+sinh)*(cosh-sinh) = exp(x) * exp(-x) = 1
    for x in [-10.0, -3.0, -1.0, -0.1, 0.0, 0.1, 1.0, 3.0, 10.0]:
        c = cosh(x)
        s = sinh(x)
        lhs = (c + s) * (c - s)
        assert math.isclose(lhs, 1.0, rel_tol=1e-12, abs_tol=5e-8)


def test_tanh_limits_saturate():
    # 大值下 tanh -> ±1（算法使用 exp(-2|x|) 的稳定式）
    assert math.isclose(tanh(1000.0), 1.0, rel_tol=0.0, abs_tol=0.0)
    assert math.isclose(tanh(-1000.0), -1.0, rel_tol=0.0, abs_tol=0.0)


def test_odd_even_properties():
    # 奇偶性：sinh/tanh 为奇函数，cosh 为偶函数
    for x in [0.0, 0.25, 1.3, 5.0]:
        assert math.isclose(sinh(-x), -sinh(x), rel_tol=REL, abs_tol=ABS)
        assert math.isclose(tanh(-x), -tanh(x), rel_tol=REL, abs_tol=ABS)
        assert math.isclose(cosh(-x), cosh(x), rel_tol=REL, abs_tol=ABS)


def test_nonfinite_returns_nan_per_contract():
    # algolib 约定：非有限输入返回 NaN（与 math.* 行为不同，这里按库契约测试）
    for bad in [float("nan"), float("inf"), -float("inf")]:
        for f in (sinh, cosh, tanh):
            out = f(bad)
            assert isinstance(out, float)
            assert math.isnan(out)
