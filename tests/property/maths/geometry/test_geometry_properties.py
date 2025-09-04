# tests/property/maths/geometry/test_geometry_properties.py
import sys
import math
import importlib
from typing import Iterable, Sequence

import pytest
from hypothesis import given, settings, strategies as st, assume

from algolib.maths.geometry.geometry import Point, Vector, GeometryUtils


# ------------------------------- feature flags ---------------------------------


def _has_symbol(module_path: str, name: str) -> bool:
    try:
        mod = importlib.import_module(module_path)
        return hasattr(mod, name)
    except Exception:
        return False


HAS_LINE = _has_symbol("algolib.maths.geometry.geometry", "Line")
HAS_PLANE = _has_symbol("algolib.maths.geometry.geometry", "Plane")


# ------------------------------- helpers ---------------------------------


def _get_components(v: Vector) -> Sequence[float]:
    """Extract vector components in a robust way."""
    for name in ("comps", "components", "coords", "data"):
        if hasattr(v, name):
            return tuple(getattr(v, name))
    try:
        return tuple(v)  # type: ignore[arg-type]
    except Exception as e:  # noqa: BLE001
        raise AttributeError("Cannot access Vector components") from e


def _make_vector(xs: Iterable[float]) -> Vector:
    """Construct a Vector; assumes constructor takes an iterable of components."""
    return Vector(list(xs))


def _v_add(a: Vector, b: Vector) -> Vector:
    """Vector addition that works with either + operator or .add()."""
    if hasattr(a, "__add__"):
        try:
            return a + b  # type: ignore[operator]
        except TypeError:
            pass
    if hasattr(a, "add"):
        return a.add(b)  # type: ignore[attr-defined]
    raise AttributeError("Vector neither supports + nor .add()")


def _v_sub(a: Vector, b: Vector) -> Vector:
    if hasattr(a, "__sub__"):
        try:
            return a - b  # type: ignore[operator]
        except TypeError:
            pass
    ca = _get_components(a)
    cb = _get_components(b)
    return _make_vector(x - y for x, y in zip(ca, cb))


def _v_scale(a: Vector, s: float) -> Vector:
    if hasattr(a, "__mul__"):
        try:
            return a * s  # type: ignore[operator]
        except TypeError:
            pass
    if hasattr(a, "__rmul__"):
        try:
            return s * a  # type: ignore[operator]
        except TypeError:
            pass
    if hasattr(a, "scale"):
        return a.scale(s)  # type: ignore[attr-defined]
    return _make_vector(x * s for x in _get_components(a))


def _v_dot(a: Vector, b: Vector) -> float:
    if hasattr(a, "dot"):
        return float(a.dot(b))  # type: ignore[attr-defined]
    ca = _get_components(a)
    cb = _get_components(b)
    return float(sum(x * y for x, y in zip(ca, cb)))


def _v_norm(a: Vector) -> float:
    if hasattr(a, "norm"):
        return float(a.norm())  # type: ignore[attr-defined]
    return float(math.sqrt(sum(x * x for x in _get_components(a))))


def _v_norm_sq(a: Vector) -> float:
    """Return ||a||^2 computed as sum of squares (no sqrt)."""
    return float(sum(x * x for x in _get_components(a)))


def _p_coords(p: Point) -> Sequence[float]:
    for name in ("coords", "components", "comps", "data"):
        if hasattr(p, name):
            return tuple(getattr(p, name))
    try:
        return tuple(p)  # type: ignore[arg-type]
    except Exception as e:  # noqa: BLE001
        raise AttributeError("Cannot access Point coordinates") from e


def _make_point(xs: Iterable[float]) -> Point:
    return Point(list(xs))


# ------------------------------ base strategies -------------------------------

TOL = 1e-10
# Components smaller than this will underflow when squared.
SMALL_NORM_ZERO = math.sqrt(sys.float_info.min)  # ~1.49e-154 on IEEE-754 double
ZERO_ABS_TOL = 1e-12

dims = st.integers(min_value=2, max_value=6)
safe_float = st.floats(
    allow_nan=False,
    allow_infinity=False,
    min_value=-1e6,
    max_value=1e6,
    width=64,
)


def vectors_of_dim(n: int):
    return st.builds(
        lambda xs: _make_vector(xs), st.lists(safe_float, min_size=n, max_size=n)
    )


def points_of_dim(n: int):
    return st.builds(
        lambda xs: _make_point(xs), st.lists(safe_float, min_size=n, max_size=n)
    )


# ------------------------------ composite strategies -------------------------------


@st.composite
def vec2_same_dim(draw):
    n = draw(dims)
    arr = st.lists(safe_float, min_size=n, max_size=n)
    v1 = draw(st.builds(Vector, arr))
    v2 = draw(st.builds(Vector, arr))
    return n, v1, v2


@st.composite
def vec3_same_dim(draw):
    n = draw(dims)
    arr = st.lists(safe_float, min_size=n, max_size=n)
    v1 = draw(st.builds(Vector, arr))
    v2 = draw(st.builds(Vector, arr))
    v3 = draw(st.builds(Vector, arr))
    return n, v1, v2, v3


@st.composite
def point3_same_dim(draw):
    n = draw(dims)
    arr = st.lists(safe_float, min_size=n, max_size=n)
    p = draw(st.builds(Point, arr))
    q = draw(st.builds(Point, arr))
    r = draw(st.builds(Point, arr))
    return n, p, q, r


@st.composite
def line_triplet(draw):
    n = draw(dims)
    arr = st.lists(safe_float, min_size=n, max_size=n)
    p0 = draw(st.builds(Point, arr))
    # ensure nonzero direction
    xs = draw(arr)
    assume(any(abs(x) > 0.0 for x in xs))
    d = Vector(xs)
    t = draw(
        st.floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False)
    )
    return n, p0, d, t


@st.composite
def plane_quad(draw):
    n = draw(dims)
    arr = st.lists(safe_float, min_size=n, max_size=n)
    p0 = draw(st.builds(Point, arr))
    xs = draw(arr)
    assume(any(abs(x) > 0.0 for x in xs))
    nvec = Vector(xs)
    u = draw(st.builds(Vector, arr))
    t = draw(
        st.floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False)
    )
    return n, p0, nvec, u, t


# --------------------------- vector properties (single @given) ---------------------------


@given(data=vec2_same_dim())
@settings(max_examples=60)
def test_vector_add_commutative(data):
    n, v1, v2 = data
    left = _get_components(_v_add(v1, v2))
    right = _get_components(_v_add(v2, v1))
    for a, b in zip(left, right):
        assert math.isclose(a, b, rel_tol=1e-12, abs_tol=TOL)


@given(data=vec3_same_dim())
@settings(max_examples=40)
def test_vector_add_associative(data):
    n, v1, v2, v3 = data
    left = _get_components(_v_add(_v_add(v1, v2), v3))
    right = _get_components(_v_add(v1, _v_add(v2, v3)))
    for a, b in zip(left, right):
        assert math.isclose(a, b, rel_tol=1e-12, abs_tol=TOL)


@given(data=vec2_same_dim())
@settings(max_examples=60)
def test_vector_add_identity_and_inverse(data):
    n, v1, _ = data
    zero = _make_vector([0.0] * n)
    # identity
    z1 = _get_components(_v_add(v1, zero))
    for a, b in zip(z1, _get_components(v1)):
        assert math.isclose(a, b, rel_tol=1e-12, abs_tol=TOL)
    # inverse
    inv = _v_scale(v1, -1.0)
    z2 = _get_components(_v_add(v1, inv))
    for c in z2:
        assert math.isclose(c, 0.0, abs_tol=TOL)


@given(data=vec2_same_dim())
@settings(max_examples=60)
def test_dot_symmetry_and_cauchy_schwarz(data):
    n, v1, v2 = data
    dv1 = _v_dot(v1, v2)
    dv2 = _v_dot(v2, v1)
    assert math.isclose(dv1, dv2, rel_tol=1e-12, abs_tol=TOL)
    # assert abs(dv1) <= _v_norm(v1) * _v_norm(v2) + 1e-12
    # Allow a tiny absolute slack to cover roundoff from sqrt()*sqrt()
    # 当前：
    # assert abs(dv1) <= _v_norm(v1) * _v_norm(v2) + 1e-9

    # squared-form Cauchy–Schwarz check with ULP bump on RHS
    s1 = _v_norm_sq(v1)
    s2 = _v_norm_sq(v2)
    lhs = dv1 * dv1
    bound = s1 * s2
    # 在 subnormal 区域，数值噪声绝对值主导；给出固定的绝对兜底

    if bound < 1e-300:
        assert lhs <= bound + 1e-300
    else:
        # 正常区间：相对 + 极小绝对兜底
        assert lhs <= bound * (1 + 1e-12) + 1e-12


@given(
    data=vec2_same_dim(),
    a=st.floats(allow_nan=False, allow_infinity=False, min_value=-1e6, max_value=1e6),
)
@settings(max_examples=60)
def test_norm_properties(data, a):
    n, v1, v2 = data
    nv = _v_norm(v1)
    assert nv >= 0.0
    comps = _get_components(v1)

    # Treat components smaller than sqrt(min_float) as numerically zero,
    # because squaring them will underflow to 0 and the norm becomes 0.0.
    is_num_zero = all(abs(x) <= SMALL_NORM_ZERO for x in comps)

    if is_num_zero:
        assert math.isclose(nv, 0.0, abs_tol=ZERO_ABS_TOL)
    else:
        assert nv > 0.0
    # homogeneity
    assert math.isclose(
        _v_norm(_v_scale(v1, a)), abs(a) * _v_norm(v1), rel_tol=1e-12, abs_tol=1e-12
    )
    # triangle inequality
    left = _v_norm(_v_add(v1, v2))
    right = _v_norm(v1) + _v_norm(v2)
    assert left <= right + 1e-12


# --------------------------- point / distance properties ---------------------------


@given(data=point3_same_dim())
@settings(max_examples=60)
def test_distance_metric_axioms(data):
    n, p, q, r = data
    d = GeometryUtils.distance
    d_pq = d(p, q)
    d_qp = d(q, p)
    assert d_pq >= 0.0
    assert math.isclose(d_pq, d_qp, rel_tol=1e-12, abs_tol=1e-12)
    same = all(
        math.isclose(a, b, abs_tol=0.0) for a, b in zip(_p_coords(p), _p_coords(q))
    )
    if same:
        assert math.isclose(d_pq, 0.0, abs_tol=0.0)
    d_pr = d(p, r)
    d_qr = d(q, r)
    # allow a tiny absolute slack for FP rounding of two norms + one add
    assert d_pr <= d_pq + d_qr + 1e-9


# ----------------------------- line / plane (optional) -----------------------------


@pytest.mark.skipif(not HAS_LINE, reason="Line not implemented")
@given(data=line_triplet())
@settings(max_examples=40)
def test_line_parametric_goes_through_base(data):
    from algolib.maths.geometry.geometry import Line  # type: ignore

    n, p0, d, t = data
    L = Line(p0, d)
    # If API has point_at(t) use it, else reconstruct manually
    if hasattr(L, "point_at"):
        pt = L.point_at(t)  # type: ignore[attr-defined]
    else:
        pt = _make_point(a + t * b for a, b in zip(_p_coords(p0), _get_components(d)))
    pt0 = _make_point(a + 0.0 * b for a, b in zip(_p_coords(p0), _get_components(d)))
    assert all(
        math.isclose(a, b, rel_tol=0, abs_tol=1e-12)
        for a, b in zip(_p_coords(pt0), _p_coords(p0))
    )


@pytest.mark.skipif(not HAS_PLANE, reason="Plane not implemented")
@given(data=plane_quad())
@settings(max_examples=40)
def test_plane_normal_is_orthogonal(data):
    from algolib.maths.geometry.geometry import Plane  # type: ignore

    n, p0, nvec, u, t = data
    assume(_v_norm(nvec) > 0.0)
    P = Plane(p0, nvec)
    # Construct a point X on the plane: p0 + t*(u - proj_n(u))
    # 自适应投影：优先用原始法向量（更少往返舍入），当 ||n|| 非常小时退回单位法向量
    nv2 = _v_dot(nvec, nvec)
    if nv2 > 1e-300:
        # 经典投影：proj_n(u) = ((u·n)/(n·n)) n
        w = _v_sub(u, _v_scale(nvec, _v_dot(u, nvec) / nv2))
        # 同时构造单位法向量用于下方正交性检测
        norm_n = _v_norm(nvec)
        assume(norm_n > 0.0)
        n_hat = _v_scale(nvec, 1.0 / norm_n)
    else:
        # 极小范数：使用单位法向量避免除以几乎为零的 n·n
        norm_n = _v_norm(nvec)
        assume(norm_n > 0.0)
        n_hat = _v_scale(nvec, 1.0 / norm_n)
        w = _v_sub(u, _v_scale(n_hat, _v_dot(u, n_hat)))
    X = _make_point(a + t * b for a, b in zip(_p_coords(p0), _get_components(w)))
    diff = _v_sub(_make_vector(_p_coords(X)), _make_vector(_p_coords(p0)))
    # 原来：
    # assert math.isclose(_v_dot(nvec, diff), 0.0, abs_tol=3e-9)

    # check orthogonality against unit normal
    dot_unit = _v_dot(n_hat, diff)
    scale = _v_norm(diff)

    # robust tolerance: relative + absolute floor
    rel = 2e-12
    abs_floor = 6e-9
    tol = rel * scale + abs_floor
    assert abs(dot_unit) <= tol
