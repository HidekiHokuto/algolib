# ---------------------------------------------------------------------------
# Smoke tests for physics constants (raise coverage for algolib.physics)
# NOTE: These tests only verify basic invariants/relationships; they are not
# meant to validate CODATA numerics beyond coarse tolerances.
# ---------------------------------------------------------------------------

import math
import pytest

from algolib.physics import constants as P
from algolib.numerics import constants as C  # for PI

def _isclose(a: float, b: float, rel: float = 1e-12, abs_: float = 1e-15) -> bool:
    """Lightweight closeness check for floats."""
    return math.isclose(a, b, rel_tol=rel, abs_tol=abs_)

def test_defining_constants_are_exact_and_positive():
    """Defining SI constants must be exact (rel_unc==0) and positive."""
    for const in (P.c, P.h, P.e, P.k_B, P.N_A):
        assert const.value > 0.0
        assert const.rel_unc == 0.0
        assert isinstance(const.unit, str) and const.unit != ""
        assert const.source == P.CODATA_VINTAGE

def test_hbar_matches_h_over_two_pi_within_tolerance():
    """ħ should equal h/(2π) within a tight numerical tolerance."""
    expected = P.h.value / (2.0 * C.PI)
    # π is irrational, so this cannot be exact in binary64; allow a tiny rel tol
    assert _isclose(P.hbar.value, expected, rel=1e-9, abs_=2e-46)

def test_R_equals_NA_times_kB_within_tolerance():
    """Gas constant R equals N_A * k_B within floating-point tolerance."""
    expected = P.N_A.value * P.k_B.value
    assert _isclose(P.R.value, expected, rel=5e-11, abs_=0.0)

@pytest.mark.parametrize(
    "pc",
    [P.alpha, P.m_e, P.m_p, P.m_n, P.m_u, P.R_inf, P.a0, P.sigmaSB],
)
def test_non_defining_constants_have_units_and_uncertainty(pc):
    """Non-defining constants must have a unit and a non-negative rel_unc."""
    assert isinstance(pc.unit, str) and pc.unit != ""
    assert pc.rel_unc is None or pc.rel_unc >= 0.0