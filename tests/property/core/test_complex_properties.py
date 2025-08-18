# tests/property/core/test_complex_properties.py
import math
from hypothesis import given, strategies as st, settings, assume
from algolib.core.complex import Complex

# =========================
# Helpers
# =========================
def _ulp_around_one(k: int = 8) -> float:
    # 1.0 的 ULP ~ 2**-52 ≈ 2.22e-16
    return k * math.ulp(1.0)

def _ulp(x: float) -> float:
    # 1 ULP around |x|；对 0 给一个极小兜底
    return math.ulp(x if x != 0.0 else 1.0)

TOL = 1e-10  # 常规比较用的松一点容差

# =========================
# 安全范围策略（日常性质测试用）
# =========================
finite_floats_safe = st.floats(
    allow_nan=False,
    allow_infinity=False,
    min_value=-1e6,
    max_value=1e6,
)
complexes_safe = st.builds(Complex, finite_floats_safe, finite_floats_safe)
nonzero_complexes_safe = complexes_safe.filter(
    lambda z: not (z.re == 0.0 and z.im == 0.0)
)

# =========================
# 全范围策略（极限测试用）
# =========================
def finite_floats_fullrange():
    base = st.floats(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1e308,
        max_value=1e308,
        allow_subnormal=True,
        width=64,
    )
    specials = st.sampled_from([
        0.0,
        math.ldexp(1.0, -1074),  # 最小 subnormal
        math.ldexp(1.0, -1022),  # 最小 normal
        math.ldexp(1.0, 1023),   # 最大阶
        math.pi, -math.pi, math.e, -math.e,
        2**-500, 2**-1000, 2**-1070,
        2**500, 2**900,
    ])
    return st.one_of(base, specials)

@st.composite
def complexes_torture(draw):
    re = draw(finite_floats_fullrange())
    im = draw(finite_floats_fullrange())
    return Complex(re, im)

@st.composite
def nonzero_complexes_torture(draw):
    z = draw(complexes_torture())
    assume(not (z.re == 0.0 and z.im == 0.0))  # 注意用的是 hypothesis.assume
    return z

# =========================
# 基本代数性质（安全范围）
# =========================
@given(z1=complexes_safe, z2=complexes_safe)
@settings(max_examples=100)
def test_add_commutative(z1: Complex, z2: Complex):
    assert (z1 + z2).almost_equal(z2 + z1, tol=TOL)

@given(z1=complexes_safe, z2=complexes_safe)
@settings(max_examples=100)
def test_mul_commutative(z1: Complex, z2: Complex):
    assert (z1 * z2).almost_equal(z2 * z1, tol=TOL)

@given(z=complexes_safe)
@settings(max_examples=100)
def test_conjugate_involution(z: Complex):
    assert z.conjugate().conjugate().almost_equal(z, tol=TOL)

# =========================
# 模长相关（安全范围）
# =========================
@given(z=complexes_safe)
@settings(max_examples=100)
def test_modulus_non_negative(z: Complex):
    r = z.modulus()
    assert r >= 0.0
    if z.re == 0.0 and z.im == 0.0:
        assert r == 0.0
    else:
        assert r > 0.0

@given(z1=complexes_safe, z2=complexes_safe)
@settings(max_examples=100)
def test_modulus_multiplicative(z1: Complex, z2: Complex):
    left = (z1 * z2).modulus()
    right = z1.modulus() * z2.modulus()
    assert math.isclose(left, right, rel_tol=1e-12, abs_tol=1e-12)

# =========================
# 除法/单位化（极限范围 + ULP 判据）
# =========================
@given(z=nonzero_complexes_torture())
@settings(max_examples=100)
def test_normalized_has_unit_modulus_ulps(z: Complex):
    zn = z.normalized()
    # |zn| 与 1 的误差控制在若干 ULP（更严格）
    assert abs(abs(zn) - 1.0) <= _ulp_around_one(8)

@given(z=nonzero_complexes_torture())
@settings(max_examples=100)
def test_dividing_by_self_is_one_ulps(z: Complex):
    w = z / z
    # 用 almost_equal + 紧一些的 tol；也可换 ULP 判据（需要针对 re/im 写 ulp 比较）
    assert w.almost_equal(Complex(1.0, 0.0), tol=1e-12)

# =========================
# 极坐标往返（安全范围）
# =========================
@given(z=complexes_safe)
@settings(max_examples=100)
def test_polar_roundtrip(z: Complex):
    r, theta = z.to_polar()
    if r == 0.0:
        zp = Complex.from_polar(0.0, 0.0)
        assert zp.almost_equal(Complex(0.0, 0.0), tol=TOL)
    else:
        zp = Complex.from_polar(r, theta)
        assert zp.almost_equal(z, tol=1e-9)

# =========================
# 三角不等式（安全范围）
# =========================
@given(z1=complexes_safe, z2=complexes_safe)
@settings(max_examples=100)
def test_triangle_inequality(z1: Complex, z2: Complex):
    left = (z1 + z2).modulus()
    right = z1.modulus() + z2.modulus()
    # Allow a handful of ULPs to account for rounding in (+) and hypot()
    eps = 8 * _ulp(right)
    assert left <= right + eps