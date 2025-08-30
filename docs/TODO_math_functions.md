# TODO: Implement/Wrap Python math functions in algolib.numerics

## Number-theoretic
- [ ] factorial
- [ ] gcd
- [ ] lcm
- [ ] comb
- [ ] perm
- [ ] isqrt

## Floating-point arithmetic
- [ ] ceil
- [ ] floor
- [ ] trunc
- [ ] fabs
- [ ] fmod
- [ ] modf
- [ ] remainder
- [ ] fma

## Power & logarithmic
- [x] sqrt
- [x] pow
- [x] exp
- [ ] exp2
- [ ] expm1
- [ ] log
- [ ] log1p
- [ ] log2
- [ ] log10
- [ ] cbrt

## Trigonometric
- [x] sin, cos, tan
- [ ] asin, acos, atan, atan2

## Hyperbolic
- [x] sinh, cosh, tanh
- [ ] asinh, acosh, atanh

## Special functions
- [ ] erf, erfc
- [ ] gamma, lgamma

## Constants
- [x] pi, e, tau, inf, nan

## Angular conversion
- [ ] degrees
- [ ] radians

## Summation & product
- [ ] fsum
- [ ] prod
- [ ] sumprod
- [ ] dist
- [x] hypot

## Float ops & predicates
- [ ] copysign
- [ ] frexp
- [ ] ldexp
- [ ] nextafter
- [ ] ulp
- [ ] isclose
- [ ] isfinite
- [ ] isinf
- [ ] isnan
# TODO: Implement/Wrap CPython `math` APIs in `algolib.numerics`

> Scope: scalar real-valued APIs first (baseline Py3.10), while tracking newer additions.  
> Tags: `(3.11+)` and `(3.12+)` mark functions added in those Python versions.

## Number-theoretic
- [ ] factorial
- [ ] gcd
- [ ] lcm
- [ ] comb
- [ ] perm
- [ ] isqrt

## Floating-point arithmetic & rounding
- [ ] ceil
- [ ] floor
- [ ] trunc
- [x] **round** (bankers’ rounding; ties to even)
- [ ] fabs
- [ ] fmod
- [ ] modf
- [ ] remainder
- [ ] fma

## Power & logarithmic
- [x] sqrt
- [ ] pow
- [x] exp
- [ ] exp2 (3.11+)
- [ ] expm1
- [ ] log
- [ ] log1p
- [ ] log2
- [ ] log10
- [ ] cbrt (3.11+)

## Trigonometric
- [x] sin
- [x] cos
- [x] tan
- [ ] asin
- [ ] acos
- [ ] atan
- [ ] atan2

## Hyperbolic
- [x] sinh
- [x] cosh
- [x] tanh
- [ ] asinh
- [ ] acosh
- [ ] atanh

## Special functions
- [ ] erf
- [ ] erfc
- [ ] gamma
- [ ] lgamma

## Constants
- [x] pi
- [x] e
- [x] tau
- [x] inf
- [x] nan

## Angular conversion
- [ ] degrees
- [ ] radians

## Summation & product
- [ ] fsum
- [ ] prod
- [ ] sumprod (3.12+)
- [ ] dist
- [x] hypot

## Float ops & predicates
- [ ] copysign
- [ ] frexp
- [ ] ldexp
- [ ] nextafter
- [ ] ulp
- [ ] isclose
- [ ] isfinite
- [ ] isinf
- [ ] isnan

---

### Notes for implementation
- Keep uniform API placement under `algolib.numerics` with thin wrappers where appropriate (e.g., trig via backend), and stable pure-python reference implementations where we own the kernel (e.g., `round`, `hypot`, `exp`).
- For Py3.11+ / 3.12+ items, guard imports/exports via feature gates to maintain baseline Py3.10 compatibility while allowing optional support when available.
- Later phases: complex inputs and vectorization via optional backends (numpy/torch) with identical reduction/rounding rules.