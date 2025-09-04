# tests/unit/numerics/test_trig_pure_smoke.py
import math
import pytest

from algolib.numerics import trig_pure as tp


def test_basic_values():
    # 基本点
    assert abs(tp.sin(0.0)) < 1e-15
    assert abs(tp.cos(0.0) - 1.0) < 1e-15
    assert abs(tp.tan(0.0)) < 1e-15


def test_quadrant_symmetry():
    # 特殊角度
    assert pytest.approx(tp.sin(math.pi / 2), rel=1e-12) == 1.0
    assert pytest.approx(tp.cos(math.pi), rel=1e-12) == -1.0
    # tan(pi/4) ≈ 1
    assert pytest.approx(tp.tan(math.pi / 4), rel=1e-12) == 1.0


def test_large_inputs():
    # 大数 → 看规约是否工作，不要求极高精度
    for x in [1e3, 1e5, -1e6]:
        s = tp.sin(x)
        c = tp.cos(x)
        t = tp.tan(x)
        # 应该都在有限范围内
        assert math.isfinite(s)
        assert math.isfinite(c)
        # tan 可能很大，但不能是 nan
        assert not math.isnan(t)


def test_nan_inf_inputs():
    for x in [float("nan"), float("inf"), float("-inf")]:
        assert math.isnan(tp.sin(x))
        assert math.isnan(tp.cos(x))
        assert math.isnan(tp.tan(x))
