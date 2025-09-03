# tests/property/numerics/test_pow_properties.py
import pytest
from hypothesis import given, settings, strategies as st
import math

from algolib.numerics import pow as algo_pow
from algolib.core.complex import Complex

# --- Helper: ensure behavior parity with Python's built-in `**` ---
def _assert_pow_same_behavior(x, e):
    """Assert that algolib.numerics.pow mirrors Python's built-in `**` behavior.

    This compares both value results and exception types. If both computations
    succeed, values must be equal. If either raises, the other must raise the
    same exception type.
    """
    # Left: algolib
    try:
        a = algo_pow(x, e)
        a_ok, a_exc = True, None
    except Exception as ex:  # noqa: BLE001 - compare exception types explicitly
        a_ok, a_exc = False, type(ex)

    # Right: Python built-in
    try:
        b = (x ** e)
        b_ok, b_exc = True, None
    except Exception as ex:  # noqa: BLE001 - compare exception types explicitly
        b_ok, b_exc = False, type(ex)

    if a_ok and b_ok:
        assert a == b
    else:
        assert a_ok == b_ok and a_exc is b_exc

# --- Helper: compare Complex power vs. reference, including exceptions ---
def _assert_complex_pow_matches_reference(z: Complex, e: int) -> None:
    """Assert Complex integer power matches the reference implementation in value
    or in exception type when errors occur (e.g., zero to a negative power).
    """
    # algolib side
    try:
        a = algo_pow(z, e)
        a_ok, a_exc = True, None
    except Exception as ex:  # noqa: BLE001
        a_ok, a_exc = False, type(ex)

    # reference side
    try:
        b = _repeat_mul(z, e)
        b_ok, b_exc = True, None
    except Exception as ex:  # noqa: BLE001
        b_ok, b_exc = False, type(ex)

    if a_ok and b_ok:
        assert _complex_almost_equal(a, b), f"Complex pow mismatch: a={a!r}, b={b!r}, z={z!r}, e={e}"
    else:
        assert a_ok == b_ok and a_exc is b_exc

def _complex_almost_equal(a: Complex, b: Complex, rel: float = 5e-13, abs_: float = 1e-12) -> bool:
    """Numerical equality for Complex allowing -0.0/+0.0 and tiny roundoff.

    Tries `abs(a-b)` if supported, otherwise falls back to componentwise math.isclose.
    """
    # Fast path: exact structural equality first (handles +inf/-inf, signed zeros)
    try:
        if a == b:
            return True
    except Exception:
        pass

    # If all components are finite, use magnitude-based tolerance on the difference
    try:
        are_finite = math.isfinite(a.re) and math.isfinite(a.im)
        bre_finite = math.isfinite(b.re) and math.isfinite(b.im)
        if are_finite and bre_finite:
            try:
                diff = a - b  # type: ignore[operator]
                return abs(diff) <= max(abs_, rel * max(abs(a), abs(b)))  # type: ignore[arg-type]
            except Exception:
                pass
    except Exception:
        pass

    # Componentwise fallback with special handling for infinities and signed zeros
    try:
        # Real parts
        if math.isinf(a.re) or math.isinf(b.re):
            if not (math.isinf(a.re) and math.isinf(b.re) and (a.re > 0) == (b.re > 0)):
                return False
        else:
            if not ((a.re == b.re) or math.isclose(a.re, b.re, rel_tol=rel, abs_tol=abs_)):
                return False

        # Imag parts
        if math.isinf(a.im) or math.isinf(b.im):
            if not (math.isinf(a.im) and math.isinf(b.im) and (a.im > 0) == (b.im > 0)):
                return False
        else:
            if not ((a.im == b.im) or math.isclose(a.im, b.im, rel_tol=rel, abs_tol=abs_)):
                return False

        return True
    except Exception:
        return False

def _repeat_mul(z: Complex, n: int) -> Complex:
    """Reference implementation for integer power using repeated multiplication."""
    if n == 0:
        return type(z)(1.0, 0.0)
    if n < 0:
        return type(z)(1.0, 0.0) / _repeat_mul(z, -n)
    acc = type(z)(1.0, 0.0)
    for _ in range(n):
        acc = acc * z
    return acc

# ---------- Built-in integers ----------
@given(
    a=st.integers(min_value=-10**6, max_value=10**6),
    e=st.integers(min_value=0, max_value=64), # keep it moderate
)
def test_pow_int_equals_builtin(a, e):
    assert algo_pow(a, e) == (a ** e)

# ---------- Built-in floats with integer exponents ----------
@given(
    x=st.floats(allow_nan=False, allow_infinity=False, width=64, min_value=-1e3, max_value=1e3),
    e=st.integers(min_value=-10, max_value=10),
)
def test_pow_float_intexp_equals_builtin(x, e):
    # For float base with int exponent, compare behavior (value or exception).
    _assert_pow_same_behavior(x, e)

# ---------- Complex integer exponents ----------
def test_complex_basic_integer_exponents():
    z = Complex(2.0, -1.0)
    assert algo_pow(z, 0) == Complex(1.0, 0.0)
    assert algo_pow(z, 1) == z
    assert algo_pow(z, 2) == z * z
    assert algo_pow(z, -1) == Complex(1.0, 0.0) / z


@given(
    re=st.floats(allow_nan=False, allow_infinity=False, width=64, min_value=-5.0, max_value=5.0),
    im=st.floats(allow_nan=False, allow_infinity=False, width=64, min_value=-5.0, max_value=5.0),
    e=st.integers(min_value=-8, max_value=8),
)
@settings(max_examples=60)
def test_complex_integer_power_matches_reference(re, im, e):
    z = Complex(re, im)
    _assert_complex_pow_matches_reference(z, e)