# tests/unit/numerics/test_constants.py

import math
import sys

import pytest

import algolib.numerics.constants as C
from algolib.exceptions import NumericOverflowError


# ---------------------------
# 基础常数数值与相互关系
# ---------------------------

@pytest.mark.parametrize(
    "name, val, ref",
    [
        ("PI",      C.PI,      math.pi),
        ("PI_2",    C.PI_2,    math.pi / 2.0),
        ("PI_4",    C.PI_4,    math.pi / 4.0),
        ("TAU",     C.TAU,     math.tau),
        ("INV_PI",  C.INV_PI,  1.0 / math.pi),
        ("INV_PI_2",C.INV_PI_2,2.0 / math.pi),
        ("E",       C.E,       math.e),
        ("LN2",     C.LN2,     math.log(2.0)),
        ("INV_LN2", C.INV_LN2, 1.0 / math.log(2.0)),
        ("LOG2E",   C.LOG2E,   1.0 / math.log(2.0)),
        ("LN10",    C.LN10,    math.log(10.0)),
        ("INV_LN10",C.INV_LN10,1.0 / math.log(10.0)),
        ("SQRT2",   C.SQRT2,   math.sqrt(2.0)),
        ("INV_SQRT2",C.INV_SQRT2, 1.0 / math.sqrt(2.0)),
    ],
)
def test_numeric_values(name, val, ref):
    # 双精度范围内严苛比较
    assert math.isclose(val, ref, rel_tol=1e-15, abs_tol=1e-15), f"{name} mismatch"


def test_tau_vs_two_pi():
    assert math.isclose(C.TAU, 2.0 * C.PI, rel_tol=0.0, abs_tol=0.0)


def test_log_alias_identity():
    # LOG2E 是 INV_LN2 的别名（同一对象值）
    assert C.LOG2E is C.INV_LN2
    assert math.isclose(C.LOG2E, C.INV_LN2, rel_tol=0.0, abs_tol=0.0)


# ---------------------------
# Cody–Waite 拆分验证
# ---------------------------

def test_ln2_split_exact_sum():
    # 设计上应当在 double 加法下“恰好”复原 LN2
    assert (C.LN2_HI + C.LN2_LO) == C.LN2


def test_pi_over_2_split_exact_sum():
    assert (C.PI2_HI + C.PI2_LO) == C.PI_2


def test_pi_split_exact_sum():
    assert abs((C.PI_HI + C.PI_LO) - C.PI) < 1e-20


# ---------------------------
# IEEE754 相关常量的关系校验
# ---------------------------

def test_ieee754_basic_relations():
    # 精度 & 单位舍入
    assert C.DBL_MANT_DIG == 53
    assert C.DBL_EPS == 2.0 ** -52

    # 最小/最大正规数与非正规数边界关系
    assert C.DBL_MIN == 2.0 ** -1022
    assert C.DBL_DENORM_MIN == 2.0 ** -1074
    assert math.isclose(
        C.DBL_MAX, (2.0 - 2.0 ** -52) * (2.0 ** 1023), rel_tol=0.0, abs_tol=0.0
    )

    # 内部一致性（不和 sys.float_info 的命名细节掰扯）
    assert C.DBL_MIN == C.pow2_int(C.DBL_MIN_EXP)
    # 非正规最小值应当等于 MIN * 2**(-(mantissa_bits-1))
    assert C.DBL_DENORM_MIN == C.DBL_MIN * (2.0 ** (-(C.DBL_MANT_DIG - 1)))


# ---------------------------
# 小工具函数
# ---------------------------

@pytest.mark.parametrize("k", list(range(-1100, 1101, 137)) + [0, -1, 1, -1074, -1022, 1023, 1092])
def test_pow2_int_matches_builtin(k):
    # builtin 侧先探路（捕获异常/得到值）
    try:
        builtin = 2.0 ** k
        builtin_exc = None
    except OverflowError as e:
        builtin = None
        builtin_exc = e

    # 被测侧
    try:
        got = C.pow2_int(k)
        got_exc = None
    except OverflowError as e:  # NumericOverflowError 也是它的子类
        got = None
        got_exc = e

    # 两侧都溢出了：通过
    if builtin_exc is not None and got_exc is not None:
        return

    # 两侧都没溢出：数值相等
    assert builtin_exc is None and got_exc is None
    assert got == builtin


@pytest.mark.parametrize(
    "x,y,expected",
    [
        (3.5,  +2.0, +3.5),
        (3.5,  -2.0, -3.5),
        (-4.0, +0.0, +4.0),
        (-4.0, -0.0, -4.0),
        (0.0,  float("nan"), 0.0),  # y 为 NaN 时按实现应返回 x 本身
        (-7.0, float("nan"), -7.0),
    ],
)
def test_copysign1(x, y, expected):
    got = C.copysign1(x, y)
    # 仅比较数值与符号，不做 NaN 的等号比较
    if math.isnan(y):
        assert got == x
    else:
        assert got == expected


# ---------------------------
# 默认容差
# ---------------------------

def test_default_tolerances():
    assert C.REL_EPS_DEFAULT == 2e-12
    assert C.ABS_EPS_DEFAULT == 1e-12