# src/algolib/numerics/constants.py
"""
Centralized numerical constants for algolib.

- No imports from `math` or third-party libs: *pure Python floats only*.
- Values are given either as exact decimal, or with comments showing hex-float
  for traceability.
- Includes Cody–Waite style splits for stable range-reduction in exp/sin/cos.
"""

from algolib.exceptions import NumericOverflowError

# -----------------------------
# IEEE-754 double "machine" info
# -----------------------------
# Python float is IEEE-754 binary64 on CPython.
DBL_MANT_DIG      = 53                    # significand bits
DBL_EPS           = 2.0 ** -52            # ~= 2.220446049250313e-16 (unit roundoff)
DBL_MIN_EXP       = -1022                 # min exponent for normal numbers
DBL_MAX_EXP       = 1024                  # max exponent (exclusive bound for 2^e)
DBL_MIN           = 2.0 ** -1022          # ~= 2.2250738585072014e-308 (min normal)
DBL_DENORM_MIN    = 2.0 ** -1074          # ~= 5e-324 (min subnormal)
DBL_MAX           = (2.0 - 2.0 ** -52) * (2.0 ** 1023)  # ~= 1.7976931348623157e+308

# --------------------------------
# Fundamental mathematical constants
# --------------------------------
PI   = 3.14159265358979323846264338327950288419716939937510
PI_2 = 1.57079632679489661923132169163975144209858469968755   # π/2
PI_4 = 0.78539816339744830961566084581987572104929234984378   # π/4
TAU  = 6.28318530717958647692528676655900576839433879875021   # 2π
INV_PI     = 0.31830988618379067153776752674502872406891929148091       # 1/π
INV_PI_2   = 0.63661977236758134307553505349005744813783858296183       # 2/π
E          = 2.71828182845904523536028747135266249775724709369996
LN2        = 0.69314718055994530941723212145817656807550013436026
INV_LN2    = 1.44269504088896340735992468100189213742664595415299       # 1/ln 2
LOG2E      = INV_LN2                                                     # alias
LN10       = 2.30258509299404568401799145468436420760110148862877
INV_LN10   = 0.43429448190325182765112891891660508229439700580366
SQRT2      = 1.41421356237309504880168872420969807856967187537694
INV_SQRT2  = 0.70710678118654752440084436210484903928483593768847

# ----------------------------------------------------
# Cody–Waite splits for stable range reduction / exp()
# ----------------------------------------------------
# ln(2) = LN2_HI + LN2_LO (sum exactly equals LN2 in double)
LN2_HI = 0.6931471803691238
LN2_LO = 1.9082149292705877e-10

# π/2 split helps reduce cancellation in quadrant reduction
PI2_HI = 1.5707963267948966        # high part of π/2
PI2_LO = 6.123233995736766e-17     # low  part of π/2

# Optional: π split (rarely needed if you reduce by π/2)
PI_HI = 3.141592653589793
PI_LO = 1.2246467991473532e-16

# -----------------------------------
# Default, *general* numerical tolerances
# -----------------------------------
# These are library-wide suggestions; tests may override.
REL_EPS_DEFAULT = 2e-12
ABS_EPS_DEFAULT = 1e-12

# ------------------------------------------------
# Small helpers (no math.*; keep them dependency-free)
# ------------------------------------------------
def pow2_int(k: int) -> float:
    """Compute 2**k using only multiplies (supports negative k) with IEEE754-style bounds.

    Behavior:
      - k >  1023 -> raise NumericOverflowError (subclass of OverflowError)
      - k < -1074 -> 0.0 (underflow to zero)
      - -1074 <= k <= -1023 -> exact subnormal via halving from DBL_MIN
      - otherwise -> exponentiation-by-squaring (<= 1023 以及 >= -1022)
    """
    if k == 0:
        return 1.0
    if k > 1023:
        # mirror builtin overflow, 但用库内异常（是 OverflowError 的子类）
        raise NumericOverflowError("Result too large")
    if k < -1074:
        # underflow to zero
        return 0.0

    if k >= DBL_MIN_EXP:  # 正规区间（包含 -1022）
        if k > 0:
            y = 1.0
            base = 2.0
            n = k
            while n:
                if (n & 1) != 0:
                    y *= base
                base *= base
                n >>= 1
            return y
        else:
            # -1022 <= k <= -1：用 0.5 的平方幂，稳定且不会一路掉成 0
            y = 1.0
            base = 0.5  # 2**-1
            n = -k
            while n:
                if (n & 1) != 0:
                    y *= base
                base *= base
                n >>= 1
            return y

    # 次正规：-1074 <= k <= -1023
    # 思路：从最小正规 DBL_MIN = 2**-1022 开始，做 (-(k+1022)) 次“乘 0.5”。
    # 这里最多 52 次，能得到精确的 subnormal。
    steps = -(k + 1022)  # 介于 1..52
    y = DBL_MIN
    for _ in range(steps):
        y *= 0.5
    # k = -1074 时 y == DBL_DENORM_MIN（5e-324）
    return y

def copysign1(x: float, y: float) -> float:
    r"""Return :math:\\abs{x} with the sign of y. No math module, handles ±0.0 and NaN."""
    # y 是 NaN：按约定返回 x 本身（测试也是这么期望的）
    if y != y:  # NaN 自不等
        return x

    # 取 |x|
    ax = x if x >= 0.0 else -x

    # y == 0.0 时，用十六进制表示判断符号位
    if y == 0.0:
        neg = float.hex(y).startswith("-")
        return -ax if neg else ax

    # 其余情况：比较即可
    return ax if y > 0.0 else -ax