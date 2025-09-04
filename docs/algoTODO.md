# 📌 algolib 开发路线图 / TODO 纲领

目标：构建一个 纯 Python + 可选 C/Rust 加速 的统一数值计算库，保证 数值契约一致性、可追溯性、可复现性。
范围：algorithms（通用算法）、numerics（数值核）、maths（代数/几何/数论）、physics、utils。
Python baseline: 3.10，向后兼容 3.11+ / 3.12+ 新增 API。


# 🧩 核心原则

- 纯内核优先：所有基础函数有纯 Python 权威实现，避免依赖 math/numpy/scipy。
- 契约一致：非有限/出域 → NaN，不抛异常；±0.0 保留；周期规约一致。
- 可追溯：预留 provenance 记录接口，计算可溯源。
- 模块分层：
    - algorithms/ → 前置科技（分治、素数筛、乘积树、Newton、FFT…）
    - numerics/ → 标量核（sqrt, exp, gamma, trig…）
    - maths/ → 高阶代数/几何/数论（矩阵、组合数、几何对象）
    - physics/ → 常量与物理公式
    - utils/ → 杂项工具



# 📐 数值函数 (numerics)

- Number-theoretic
	- factorial (product-tree, prime-swing) P0
	- gcd
	- lcm P1
	- comb, perm P1
	- isqrt P0

- Floating-point arithmetic & rounding
	- ceil, floor, trunc P1
    - round (ties-to-even) P0
	- fabs, fmod, modf, remainder P0
	- fma P1

- Power & logarithmic
	- sqrt, pow, exp
	- exp2 (3.11+), expm1, log, log1p, cbrt (3.11+) P0/P1
	- log2, log10

- Trigonometric
	- sin, cos, tan
	- asin, acos, atan, atan2 P1

- Hyperbolic
	- sinh, cosh, tanh
	- asinh, acosh, atanh

- Special functions
	- gamma, lgamma P0（先 Spouge，再 Lanczos）
	- erf, erfc P1

- Constants
	- pi, e, tau, inf, nan

- Angular conversion
	- degrees, radians P2

- Summation & product
	- hypot
	- fsum, prod, sumprod (3.12+), dist P1/P2

- Float ops & predicates
	- copysign, nextafter, ulp, isclose, isfinite, isinf, isnan P0/P1
	- frexp, ldexp



# 📊 通用算法 (algorithms)

- [x] rootfinding (newton, bisection)
- [ ] product-tree (P0, factorial/combinatorics 用)
- [ ] sieve (P0, prime-swing 用)
- [ ] fast power (modular exponentiation)
- [ ] FFT / convolution (P2)
- [ ] matrix multiplication (naive, block, Strassen)
- [ ] LU/QR/Cholesky decomposition P1
- [ ] polynomial tools (division, gcd, interpolation)



# 📚 数学模块 (maths)
- algebra/
  - matrix_dense: 完善矩阵类，调用 algorithms 里的矩阵运算 P0
  - polynomial: 补充多项式运算 P1
- geometry/
  - Point, Line, Plane 基础对象
  - 更复杂的几何对象/运算（交点、凸包） P2
- number_theory/
    - factorial.py (接入 algorithms.product_tree, prime-swing) P0
    - combinatorics (nCr, nPr)



# ⚛️ 物理模块 (physics)
  - constants (c, G, h, …)
  - formula (ideal gas, Planck law, …) P2

# 🔎 溯源模块 (provenance)
  - trace / evidence (记录计算证据链) P0
  - schema (可序列化结构：常量哈希、误差界、分支路径)
  - 上下文/装饰器（provenance context, @trace）

# 🛠️ 工具模块 (utils)
  - random (统一 RNG/seed 管理，支持 provenance) P1
  - stable accumulators (Kahan sum etc.) P1


