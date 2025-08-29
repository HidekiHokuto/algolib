# src/algolib/numerics/constants.py
"""
Centralized numerical constants for algolib.

- No imports from `math` or third-party libs: *pure Python floats only*.
- Values are given either as exact decimal, or with comments showing hex-float
    for traceability.
- Includes Cody-Waite style splits for stable range-reduction in exp/sin/cos.
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
PI   = 3.1415926535897932384626433832795028841971693993751058209749445923078164062862090
PI_2 = 1.5707963267948966192313216916397514420985846996875529104874722961539082031431045   # π/2
PI_4 = 0.78539816339744830961566084581987572104929234984377645524373614807695410157155225   # π/4
TAU  = 6.2831853071795864769252867665590057683943387987502116419498891846156328125724180   # 2π
INV_PI     = 3.1830988618379067153776752674502872406891929148091289749533468811779359526845307e-1       # 1/π
INV_PI_2   = 6.3661977236758134307553505349005744813783858296182579499066937623558719053690614e-1       # 2/π
E          = 2.7182818284590452353602874713526624977572470936999595749669676277240766303535476
LN2        = 6.9314718055994530941723212145817656807550013436025525412068000949339362196969472e-1
INV_LN2    = 1.4426950408889634073599246810018921374266459541529859341354494069311092191811851       # 1/ln 2
LOG2E      = INV_LN2                                                     # alias
LN10       = 2.3025850929940456840179914546843642076011014886287729760333279009675726096773525
INV_LN10   = 4.3429448190325182765112891891660508229439700580366656611445378316586464920887077e-1
SQRT2      = 1.4142135623730950488016887242096980785696718753769480731766797379907324784621070
INV_SQRT2  = 7.0710678118654752440084436210484903928483593768847403658833986899536623923105352e-1

# ----------------------------------------------------
# Cody–Waite splits for stable range reduction / exp()
# ----------------------------------------------------
# ln(2) = LN2_HI + LN2_LO (sum exactly equals LN2 in double)
LN2_HI = 0.6931471805599453
LN2_LO = 9.4172321214581765e-18

# π/2 triple split for high-accuracy range reduction
# Values compatible with fdlibm-style splits
PI2_HI  = 1.5707963267948966
PI2_MID = 1.9231321691639753e-17       # 0x3c91a62633145c07
PI2_LO  = -1.5579014153003124e-33      # 0x3b2a19c036e2eb4f

# 2/π double split for accurate k = round(x*(2/π))
# High part truncated to ~28 bits precision; low part is the residual.
INV_PI_2_HI = 0.6366197723675814          # high part of 2/π
INV_PI_2_LO = -5.692446494650995e-17

# Optional: π split (rarely needed if you reduce by π/2)
PI_HI = 3.141592653589793
PI_LO = 2.3846264338327950e-16

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

__all__ = [
    "NumericOverflowError",
    "DBL_MANT_DIG", "DBL_EPS", "DBL_MIN_EXP", "DBL_MAX_EXP",
    "DBL_MIN", "DBL_DENORM_MIN", "DBL_MAX",
    "PI", "PI_2", "PI_4", "TAU", "INV_PI", "INV_PI_2", "E", "LN2",
    "PI_HI", "PI_LO",
]
