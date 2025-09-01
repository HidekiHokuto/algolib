# tests/unit/algorithms/test_log.py
import math
import pytest

from algolib.numerics.log import log, log10

def test_log_natural():
    # natural log
    x = 200000
    assert log(x) == pytest.approx(math.log(x), rel=1e-15, abs=1e-18)

def test_log_with_base():
    # arbitrary base
    x = 256
    b = 2
    assert log(x, b) == pytest.approx(math.log(x, b), rel=1e-15, abs=1e-18)

def test_log10():
    x = 20000
    assert log10(x) == pytest.approx(math.log10(x), rel=1e-15, abs=1e-18)
    # consistency with log(x, 10)
    assert log10(x) == pytest.approx(log(x, 10), rel=1e-15, abs=1e-18)

def test_log_1_equal0():
    assert log(1) == pytest.approx(0.0, abs=1e-18)
    # for any valid base, log(1, base) = 0
    for b in [2, 10, math.e]:
        assert log(1, b) == pytest.approx(0.0, abs=1e-18)
