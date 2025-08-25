# src/algolib/numerics/trig.py
r"""
Numerical trig functions: sin / cos / tan

- No stdlib math usage in implementation
- Cody-Waite style range reduction by π/2
- Polynomial approximation on [-π/4, π/4]
"""

from algolib.numerics.constants import (
    INV_PI_2_HI, INV_PI_2_LO,
    PI2_HI, PI2_MID, PI2_LO,
    PI_4
)

PI4_HI = PI2_HI * 0.5
PI4_MID = PI2_MID * 0.5
PI4_LO = PI2_LO * 0.5




_SPLIT = 134217729.0

def _split(a: float) -> tuple[float, float]:
    C_SPLIT = 134217729.0  # 2**27 + 1
    c = C_SPLIT * a
    ah = c - (c - a)
    al = a - ah
    return ah, al

def _two_sum(a: float, b: float) -> tuple[float, float]:
    s = a + b
    bp = s - a
    e = (a - (s - bp)) + (b - bp)
    return s, e

def _two_prod(a: float, b: float) -> tuple[float, float]:
    p = a * b
    ah, al = _split(a)
    bh, bl = _split(b)
    err = ((ah * bh - p) + ah * bl + al * bh) + al * bl
    return p, err

def _compensated_div(n: float, d: float) -> float:
    """
    计算 n/d ，Kahan 补偿除法：
      q0 = n/d
      r  = n - q0*d  （用 two_prod 得到无损乘积，残差更准）
      q1 = q0 + r/d
    再做一次残差修正，进一步压误差。
    """
    # 第一次修正
    q0 = n / d
    p, pe = _two_prod(q0, d)    # p ≈ q0*d, pe 是乘法的舍入误差
    r = (n - p) - pe
    q = q0 + r / d

    # 第二次（通常很小，但能把难点例子压下去）
    p2, pe2 = _two_prod(q, d)
    r2 = (n - p2) - pe2
    return q + r2 / d

def _dd_norm(h: float, l: float):
    # 归一化 double-double：保证 |l| <= 0.5 ulp(h)
    return _two_sum(h, l)

def _dd_from_three(a_hi: float, a_mid: float, a_lo: float):
    # 把三段拼成规范化的 (H, L)
    s, e = _two_sum(a_hi, a_mid)
    h, t = _two_sum(s, a_lo)
    return _dd_norm(h, e + t)

PI4_H, PI4_L = _dd_from_three(PI4_HI, PI4_MID, PI4_LO)

def _floor(x: float) -> int:
    # no math.floor; consistent for negatives
    i = int(x)
    return i if (x >= 0.0 or i == x) else (i - 1)

def _round_nearest_even_dd(yh: float, yl: float) -> int:
    """
    round(yh+yl) to nearest-even, 在 double-double 里严格处理 .5 的粘连。
    """
    k = _floor(yh)                 # 先用 yh 的 floor 做基准
    r = (yh - k) + yl              # 剩余分数（包含低位）
    if r > 0.5 or (r == 0.5 and (k & 1) == 1):
        return k + 1
    if r < -0.5 or (r == -0.5 and (k & 1) == 1):
        return k - 1
    return k


_INF = float("inf")
_NAN = float("nan")

def _nearest_int(y: float) -> int:
    # round-to-nearest, ties-to-even
    i = int(y)                  # toward zero
    f = y - i
    if y >= 0.0:
        if f > 0.5 or (f == 0.5 and (i & 1) == 1):
            i += 1
    else:
        if f < -0.5 or (f == -0.5 and (i & 1) == 1):
            i -= 1
    return i

def _is_finite(x: float) -> bool:
    # NaN: x != x ;  inf: |x| == inf
    if x != x:
        return False
    # compare against infinities without math
    return not (x == _INF or x == -_INF)

def _round_half_even(y: float) -> int:
    # 银行家舍入：最近整数；恰好在 .5 时取偶数
    k = int(y)          # toward zero
    frac = y - k
    if y >= 0.0:
        if frac > 0.5 or (frac == 0.5 and (k & 1) == 1):
            k += 1
    else:
        if frac < -0.5 or (frac == -0.5 and (k & 1) == 1):
            k -= 1
    return k


_BIG_ARG = 1 << 17


# ---- helpers to add/remove one (pi/2) in double-double ----
def _dd_add(a_hi: float, a_lo: float, b: float):
    s, e = _two_sum(a_hi, b)
    t, f = _two_sum(a_lo, e)
    return _two_sum(s, t + f)  # renormalize

def _dd_add_pi2(r_hi: float, r_lo: float, sign: int):
    # 稳定顺序：先高段相加，再把中段并入低位，最后把误差和最末段一次性收尾
    s0, e0 = _two_sum(r_hi, sign * PI2_HI)     # 高位合并
    s1, e1 = _two_sum(r_lo, sign * PI2_MID)    # 低位合并
    s2, e2 = _two_sum(s0, s1)                  # 归并
    tail = e0 + e1 + e2 + sign * PI2_LO        # 所有尾项 + 最末段
    return _dd_norm(s2, tail)

def _dd_sub(a_hi: float, a_lo: float, b_hi: float, b_lo: float):
    s, e = _two_sum(a_hi, -b_hi)
    t, f = _two_sum(a_lo, -b_lo)
    return _two_sum(s, t + f)

# ---------------- range reduction with post-correction ----------------
# 词典序比较：判断 (a_hi+a_lo) 是否大于 (b_hi+b_lo)
def _dd_gt(a_hi: float, a_lo: float, b_hi: float, b_lo: float) -> bool:
    if a_hi > b_hi: return True
    if a_hi < b_hi: return False
    return a_lo > b_lo

def _dd_lt(a_hi: float, a_lo: float, b_hi: float, b_lo: float) -> bool:
    if a_hi < b_hi: return True
    if a_hi > b_hi: return False
    return a_lo < b_lo





# -------- 改造后的规约：round-to-even + 事后校正把 r 拉回 [-pi/4, pi/4] --------
def _reduce_pi2(x: float):
    # y = x*(2/pi) （double-double）
    p1, e1 = _two_prod(x, INV_PI_2_HI)
    p2, e2 = _two_prod(x, INV_PI_2_LO)
    s, t = _two_sum(p1, p2)  # s≈y 的高位
    e = e1 + e2
    yh, u = _two_sum(s, e)  # 先把 e 推到高位上
    yl = t + u  # 剩余都归到低位
    yh, yl = _dd_norm(yh, yl)  # <--- 新增：规范化 (yh, yl)

    # k = round-to-even
    # k = _round_nearest_even_dd(yh, yl)
    k = _round_half_even(yh + yl)  # 直接对 yh+yl 做最近偶数
    kh = float(k)

    # r = x - k*(pi/2)  （double-double）
    p, pe = _two_prod(kh, PI2_HI)
    r, re = _two_sum(x, -p)
    err   = (-pe) + re

    p, pe = _two_prod(kh, PI2_MID)
    r, re = _two_sum(r, -p);   err += (-pe) + re

    p, pe = _two_prod(kh, PI2_LO)
    r, re = _two_sum(r, -p);   err += (-pe) + re

    r_hi, r_lo = _two_sum(r, err)

    # 事后校正到 [-pi/4, pi/4]
    d_hi, d_lo = _dd_sub(r_hi, r_lo, PI4_H, PI4_L)
    if d_hi > 0.0 or (d_hi == 0.0 and d_lo > 0.0):
        k += 1
        r_hi, r_lo = _dd_add_pi2(r_hi, r_lo, -1)
        d_hi, d_lo = _dd_sub(r_hi, r_lo, PI4_H, PI4_L)
        if d_hi > 0.0 or (d_hi == 0.0 and d_lo > 0.0):
            k += 1
            r_hi, r_lo = _dd_add_pi2(r_hi, r_lo, -1)
    else:
        d2_hi, d2_lo = _dd_sub(-r_hi, -r_lo, PI4_H, PI4_L)
        if d2_hi > 0.0 or (d2_hi == 0.0 and d2_lo > 0.0):
            k -= 1
            r_hi, r_lo = _dd_add_pi2(r_hi, r_lo, +1)
            d2_hi, d2_lo = _dd_sub(-r_hi, -r_lo, PI4_H, PI4_L)
            if d2_hi > 0.0 or (d2_hi == 0.0 and d2_lo > 0.0):
                k -= 1
                r_hi, r_lo = _dd_add_pi2(r_hi, r_lo, +1)

    q = k & 3
    return q, r_hi, r_lo

# -----------------------------
# -----------------------------
# Polynomial kernels on small |r|
# -----------------------------
# 采用 fdlibm 风格的极小极大系数（double 精度）
# sin(r) ≈ r + r^3 * (S1 + r^2 * (S2 + ... + r^2 * S6))
_S1 = -1.66666666666666666666666666667e-01  # -1/3!，微调后
_S2 =  8.33333333333333333333333333333e-03
_S3 = -1.98412698412698412698412698413e-04
_S4 =  2.75573192239858906525573192240e-06
_S5 = -2.50521083854417187750521083854e-08
_S6 =  1.60590438368216145993923771702e-10
_S7 = -7.64716373181981647590113198579e-13

# cos(r) ≈ 1 + r^2 * (C1 + r^2 * (C2 + ... + r^2 * C6))
_C1 = -5.00000000000000000000000000000e-01
_C2 =  4.16666666666666666666666666667e-02
_C3 = -1.38888888888888888888888888889e-03
_C4 =  2.48015873015873015873015873016e-05
_C5 = -2.75573192239858906525573192240e-07
_C6 =  2.08767569878680989792100903212e-09
_C7 = -1.14707455977297247138516979787e-11
_C8 =  4.77947733238738529743820749112e-14
# 注：fdlibm 里还有 C7≈-1.13596475577881948265e-11；是否加到 7 次由你权衡。
# 先到 C6 通常就足以把误差压过你当前阈值。


def _sin_kernel(r: float) -> float:
    z = r * r
    p = (((((((_S7 * z + _S6) * z + _S5) * z + _S4) * z + _S3) * z + _S2) * z + _S1))
    return r + r * z * p

def _cos_kernel(r: float) -> float:
    z = r * r
    p = ((((((((_C8 * z + _C7) * z + _C6) * z + _C5) * z + _C4) * z + _C3) * z + _C2) * z + _C1))
    return 1.0 + z * p


_STICKY = 2**-40  # ≈ 9.09e-13，仅在 r 极小才触发

def _sin_cos_dd(r_hi: float, r_lo: float):
    """Return (sin(r), cos(r)) for r = r_hi + r_lo using higher-order correction in b=r_lo.

    We keep the polynomial kernels at a = r_hi, and include b terms up to O(b^5):
        sin(a+b) ≈ sin a * (1 - b^2/2 + b^4/24) + cos a * (b - b^3/6 + b^5/120)
        cos(a+b) ≈ cos a * (1 - b^2/2 + b^4/24) - sin a * (b - b^3/6 + b^5/120)
    This tightens errors near |r| ≈ π/4 and for large-argument reductions.
    """
    s0 = _sin_kernel(r_hi)
    c0 = _cos_kernel(r_hi)

    b  = r_lo
    # 极小 b 直接返回，避免无谓的舍入噪声
    if b == 0.0:
        return s0, c0

    b2 = b * b
    b3 = b2 * b
    b4 = b2 * b2
    b5 = b4 * b

    # 泰勒系数
    sb = b - (1.0 / 6.0) * b3 + (1.0 / 120.0) * b5         # b - b^3/6 + b^5/120
    cb = 1.0 - 0.5 * b2 + (1.0 / 24.0) * b4                # 1 - b^2/2 + b^4/24

    s = s0 * cb + c0 * sb
    c = c0 * cb - s0 * sb
    return s, c


# --- 3) 顶层 sin/cos/tan 用新的规约 + 二阶补偿 ---
# src/algolib/numerics/trig.py 里，保持 _sin_kernel / _cos_kernel 不变
# 只改顶层 sin / cos / tan

def sin(x: float) -> float:
    if not _is_finite(x):
        return _NAN
    q, a, b = _reduce_pi2(x)
    # 小残差“粘零”：避免周期性用例冒出 1e-12 级毛刺
    r_sum = a + b
    if -9.094947017729282e-13 < r_sum < 9.094947017729282e-13:  # 2**-40
        # 用 s≈r, c≈1 的最小近似，再做象限拼接
        s_small = r_sum
        c_small = 1.0
        if q == 0:  # sin
            return s_small
        if q == 1:
            return c_small
        if q == 2:
            return -s_small
        return -c_small
    s, c = _sin_cos_dd(a, b)
    if   q == 0: return s
    if   q == 1: return c
    if   q == 2: return -s
    return -c

def cos(x: float) -> float:
    if not _is_finite(x):
        return _NAN
    q, a, b = _reduce_pi2(x)
    r_sum = a + b
    if -9.094947017729282e-13 < r_sum < 9.094947017729282e-13:
        s_small = r_sum
        c_small = 1.0
        if q == 0:
            return c_small
        if q == 1:
            return -s_small
        if q == 2:
            return -c_small
        return s_small
    s, c = _sin_cos_dd(a, b)
    if   q == 0: return c
    if   q == 1: return -s
    if   q == 2: return -c
    return s

_T1 =  0.33333333333333333333
_T2 =  0.13333333333333333333
_T3 = 0.053968253968253968254
_T4 = 0.021869488536155202822
_T5 = 0.0088632355299021965689
_T6 = 0.0035921280365724810169
_T7 = 0.0014558343870513182682
_T8 = 0.00059002744094558598138
_T9 = 0.00023912911424355248149
_T10 = 0.000096915379569294503256
_T11 = 0.000039278323883316834053

def _tan_kernel(r: float) -> float:
    # Horner: tan(r) ≈ r + r^3*(T1 + z*(T2 + ...)),  z=r^2
    z = r * r
    p = (((((((((( _T11 * z + _T10) * z + _T9) * z + _T8) * z + _T7)
                * z + _T6) * z + _T5) * z + _T4) * z + _T3) * z + _T2) * z + _T1)
    return r + r * z * p

def _refined_inv(z: float) -> float:
    # 纯算术两步牛顿：先粗略 inv，然后两次 inv *= (2 - z*inv)。
    # 其中 z*inv 与校正用 two_prod / two_sum 做补偿，减少每步舍入。
    inv = 1.0 / z

    # step 1
    p, pe = _two_prod(z, inv)      # p ≈ z*inv
    t, te = _two_sum(2.0, -p)      # t ≈ 2 - p
    t += -pe + te                  # 把乘法与加法误差一并补上
    inv *= t

    # step 2
    p, pe = _two_prod(z, inv)
    t, te = _two_sum(2.0, -p)
    t += -pe + te
    inv *= t

    return inv

def tan(x: float) -> float:
    if not _is_finite(x):
        return _NAN

    q, r_hi, r_lo = _reduce_pi2(x)
    s, c = _sin_cos_dd(r_hi, r_lo)  # 你现有的高精核/返回 float 都行

    if q == 0 or q == 2:
        # tan = s / c  用补偿除法
        return _compensated_div(s, c)
    else:
        # tan = -c / s
        return -_compensated_div(c, s)

# --- backend thin wrapper for set_backend("pure") ---

import math as _math

# 避免名字冲突，先存一份指针
_sin_impl = sin
_cos_impl = cos
_tan_impl = tan

class PureTrigBackend:
    """Wrap current pure-Python trig implementations as a backend."""
    name = "pure"

    def sin(self, x):
        try:
            xf = float(x)
        except Exception:
            return float("nan")
        if not _math.isfinite(xf):
            return float("nan")
        return _sin_impl(xf)

    def cos(self, x):
        try:
            xf = float(x)
        except Exception:
            return float("nan")
        if not _math.isfinite(xf):
            return float("nan")
        return _cos_impl(xf)

    def tan(self, x):
        try:
            xf = float(x)
        except Exception:
            return float("nan")
        if not _math.isfinite(xf):
            return float("nan")
        return _tan_impl(xf)

# 明确导出，便于惰性注册 import
__all__ = [*globals().get("__all__", []), "PureTrigBackend"]