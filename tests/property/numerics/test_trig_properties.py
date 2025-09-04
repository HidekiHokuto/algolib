# tests/property/numerics/test_trig_properties.py

# 顶部先固定 system 后端（一定要在导入 trig 函数之前）
import math


from algolib.numerics.trig import sin as my_sin, cos as my_cos, tan as my_tan
from algolib.numerics import constants as C
from hypothesis import given, settings, strategies as st, assume

# -----------------------
# property-based sampling
# -----------------------

REL = getattr(C, "REL_EPS_DEFAULT", 2e-12)
ABS = getattr(C, "ABS_EPS_DEFAULT", 1e-12)


def _isclose(
    a: float, b: float, rel: float = REL, abs_: float = ABS, ulps: int | None = None
) -> bool:
    """相对 + 绝对 + 可选 ULP 兜底。"""
    d = abs(a - b)
    scale = max(1.0, abs(a), abs(b))
    tol = rel * scale + abs_
    if ulps is not None and math.isfinite(a) and math.isfinite(b):
        try:
            ulp = math.ulp(scale)
        except AttributeError:
            ulp = 2**-52 * scale
        tol = max(tol, ulps * ulp)
    return d <= tol


# “离奇点 π/2 + kπ 的最小距离”，用于 tan 的采样过滤
def _dist_to_half_pi_grid(x: float) -> float:
    # 令 x ≈ (π/2 + kπ) + r, 求 |r| 的最小代表元
    # 先映射到一个周期内
    t = (x - C.PI_2) / C.PI
    k = math.floor(t + 0.5)  # round to nearest integer
    r = x - (k * C.PI + C.PI_2)
    # 折回到 [-π/2, π/2]
    if r > C.PI_2:
        r -= C.PI
    elif r < -C.PI_2:
        r += C.PI
    return abs(r)


safe = st.floats(allow_nan=False, allow_infinity=False, min_value=-1e6, max_value=1e6)


@settings(max_examples=120)
@given(x=safe)
def test_sin_cos_match_math(x: float):
    assert _isclose(my_sin(x), math.sin(x), rel=6e-11, abs_=2e-11, ulps=64)
    assert _isclose(my_cos(x), math.cos(x), rel=6e-11, abs_=2e-11, ulps=64)


@settings(max_examples=120)
@given(x=safe)
def test_tan_matches_math_away_from_poles(x: float):
    # 与实现保持一致：先规约到 [-π/2, π/2] 再比较
    xr = math.remainder(x, C.TAU)
    assume(_dist_to_half_pi_grid(x) > 1.0e-10)
    assert _isclose(my_tan(x), math.tan(x), rel=1.2e-8, abs_=8e-10, ulps=4096)


# -----------------------
# identities (approximate)
# -----------------------


@settings(max_examples=100)
@given(x=safe)
def test_pythagorean_identity(x: float):
    # sin^2 + cos^2 ≈ 1
    s = my_sin(x)
    c = my_cos(x)
    left = s * s + c * c
    assert _isclose(left, 1.0, rel=1e-12, abs_=2e-11, ulps=64)


@settings(max_examples=80)
@given(x=safe, y=safe)
def test_periodicity(x: float, y: float):
    # 2π 周期
    k = int(round(y / C.TAU))
    yk = k * C.TAU
    assert _isclose(my_sin(x + yk), my_sin(x), rel=5e-10, abs_=3e-10, ulps=1024)
    assert _isclose(my_cos(x + yk), my_cos(x), rel=5e-10, abs_=3e-10, ulps=1024)

    # π 周期（tan）
    k2 = int(round(y / C.PI))
    yk2 = k2 * C.PI
    # 两端都远离极点
    # assume(_dist_to_half_pi_grid(x) > 8e-4 and _dist_to_half_pi_grid(x + yk2) > 8e-4)
    # 用同一个代表元体系判断“远离极点”，避免两端判定口径不一致
    xr = math.remainder(x, C.TAU)
    xr2 = math.remainder(x + yk2, C.TAU)
    assume(_dist_to_half_pi_grid(xr) > 2.0e-3 and _dist_to_half_pi_grid(xr2) > 2.0e-3)
    assert _isclose(my_tan(x + yk2), my_tan(x), rel=7e-8, abs_=2e-8, ulps=8192)
