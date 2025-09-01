import math
import random
from algolib.numerics.stable import frexp, ldexp

def test_frexp_basic_cases():
    assert frexp(0.0) == (0.0, 0)
    m, e = frexp(3.0)
    assert (m, e) == (0.75, 2)          # 3 = 0.75 * 2**2
    m, e = frexp(30.0)
    assert (m, e) == (0.9375, 5)        # 30 = 0.9375 * 2**5
    assert frexp(float('inf')) == (float('inf'), 0)
    mn, en = frexp(float('nan'))
    assert math.isnan(mn) and en == 0

def test_frexp_reconstruct_roundtrip():
    for x in [1e-300, -1e-300, 1e-100, 1.0, 2.0, 3.0, 1e100, -1e100]:
        m, e = frexp(x)
        if x == 0.0 or x != x or math.isinf(x):
            continue
        # 逐位重构应当精确（或至少到 ULP）
        assert ldexp(m, e) == x

def test_frexp_mantissa_range():
    # 如果范围是(-1e308, 1e308)则通不过测试
    for x in [random.uniform(-1e307, 1e307) for _ in range(1000)] + [0.0]:
        m, e = frexp(x)
        if x == 0.0:
            assert m == 0.0 and e == 0
        else:
            assert 0.5 <= abs(m) < 1.0

def test_ldexp_basic_cases():
    assert ldexp(0.0, 0) == math.ldexp(0.0, 0)
    for _ in range(100):
        m, e = (random.random()*2-1)*1e200, random.randint(-100, 100)
        assert ldexp(m, e) == math.ldexp(m, e)
