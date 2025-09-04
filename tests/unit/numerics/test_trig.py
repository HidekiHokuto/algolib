# tests/unit/numerics/test_trig.py
import math
import pytest

from algolib.numerics import constants as C


from algolib.numerics.trig_pure import sin as my_sin, cos as my_cos, tan as my_tan

# -----------------------
# helpers / configurations
# -----------------------

REL = getattr(C, "REL_EPS_DEFAULT", 2e-12)
ABS = getattr(C, "ABS_EPS_DEFAULT", 1e-12)


def _isclose(
    a: float, b: float, rel: float = REL, abs_: float = ABS, ulps: int | None = None
) -> bool:
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


def _dist_to_half_pi_grid(x: float) -> float:
    t = (x - C.PI_2) / C.PI
    k = math.floor(t + 0.5)
    r = x - (k * C.PI + C.PI_2)
    if r > C.PI_2:
        r -= C.PI
    elif r < -C.PI_2:
        r += C.PI
    return abs(r)


# -----------------------
# basic values & symmetry
# -----------------------


@pytest.mark.parametrize(
    "x",
    [
        0.0,
        C.PI_6 if hasattr(C, "PI_6") else C.PI / 6.0,
        C.PI_4,
        C.PI_3 if hasattr(C, "PI_3") else C.PI / 3.0,
        C.PI_2,
        C.PI,
        -C.PI_2,
        10.0,
        -10.0,
        1e5,
        -1e5,
    ],
)
def test_against_math_known_points(x):
    assert _isclose(my_sin(x), math.sin(x), ulps=16)
    assert _isclose(my_cos(x), math.cos(x), ulps=16)
    if _dist_to_half_pi_grid(x) > 1e-6:
        assert _isclose(my_tan(x), math.tan(x), rel=2e-11, abs_=2e-11, ulps=64)


def test_symmetry_identities():
    xs = [0.0, 0.1, 1.0, 10.0, -0.5, 123.456]
    for x in xs:
        assert _isclose(my_sin(-x), -my_sin(x), ulps=16)
        assert _isclose(my_cos(-x), my_cos(x), ulps=16)
        if _dist_to_half_pi_grid(x) > 1e-6:
            assert _isclose(my_tan(-x), -my_tan(x), rel=2e-11, abs_=2e-11, ulps=64)


# -----------------------
# edge cases: NaN / Inf
# -----------------------


@pytest.mark.parametrize("x", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_returns_nan(x):
    assert math.isnan(my_sin(x))
    assert math.isnan(my_cos(x))
    assert math.isnan(my_tan(x))
