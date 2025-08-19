# src/algolib/maths/algebra/polynomial.py
"""
Lightweight univariate polynomial with real coefficients.

Notes
-----
- Coefficients are stored in **ascending** degree order: ``p(x) = c0 + c1*x + … + cn*x**n``.
- The public API is immutable; the internal representation is a tuple of ``float``.
- Supported operations include addition, subtraction, multiplication (convolution),
  evaluation (Horner scheme), derivative, and antiderivative (indefinite integral).

Examples
--------
>>> p = Polynomial([1, 2, 3])     # 1 + 2x + 3x^2
>>> q = Polynomial.identity()      # 1
>>> (p * q).coeffs == p.coeffs
True
>>> p.derivative().coeffs          # d/dx (1 + 2x + 3x^2) = 2 + 6x
(2.0, 6.0)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence, Tuple, Union

from algolib.exceptions import InvalidTypeError, InvalidValueError

Number = Union[int, float]


def _strip_trailing_zeros(cs: Sequence[Number]) -> Tuple[float, ...]:
    """Remove trailing zeros to keep a canonical representation.

    Parameters
    ----------
    cs : Sequence[Number]
        Input coefficients in ascending degree order.

    Returns
    -------
    Tuple[float, ...]
        Coefficients with all high‑degree zeros removed. At least one
        coefficient is preserved (the zero polynomial becomes ``(0.0,)``).
    """
    if not cs:
        return (0.0,)
    out = list(map(float, cs))
    # remove highest-degree zeros, keep at least one coefficient
    while len(out) > 1 and out[-1] == 0.0:
        out.pop()
    return tuple(out)

def _horner_kahan(coeffs: Sequence[Number], x: Number) -> Number:
    """Evaluate ``p(x)`` via Horner's method with Kahan compensation for the
    accumulating sum.

    Notes
    -----
    The Kahan term stabilizes the *addition* in each fused step ``s*x + c_k``.
    This is a lightweight compromise that improves accuracy for floating‑point
    inputs without adding significant overhead.

    Parameters
    ----------
    coeffs : Sequence[Number]
        Coefficients in ascending degree order.
    x : Number
        Evaluation point. Real and complex values are supported.

    Returns
    -------
    Number
        The evaluated value ``p(x)``.
    """
    n = len(coeffs)
    if n == 1:
        return float(coeffs[0])
    s: Number = float(coeffs[-1])
    c: Number = 0.0
    for k in range(n - 2, -1, -1):
        prod = s * x
        y = float(coeffs[k]) - c
        t = prod + y
        c = (t - prod) - y
        s = t
    return s



@dataclass(frozen=True, slots=True)
class Polynomial:
    """
    Univariate polynomial with real coefficients.

    Parameters
    ----------
    coeffs : Sequence[Number]
        Coefficients in ascending degree order:
        ``[c0, c1, ..., cn]`` represents :math:`\\sum_{k=0}^n c_k x^k`.

    Raises
    ------
    InvalidTypeError
        If any coefficient is not a real number.
    InvalidValueError
        If ``coeffs`` is empty.

    Notes
    -----
    - Construction enforces a **canonical form** by stripping trailing zeros; the
      zero polynomial is thus represented as ``(0.0,)`` and has degree 0.
    - All operations return new ``Polynomial`` instances (immutable API).
    """

    coeffs: Tuple[float, ...]  # stored canonical (no trailing zeros)

    # ------------------------------- construction -------------------------------

    def __init__(self, coeffs: Iterable[Number]) -> None:
        # Validate and convert to floats, mapping type errors to our domain error.
        tmp: list[float] = []
        try:
            for c in coeffs:
                if not isinstance(c, (int, float)):
                    raise InvalidTypeError("coeffs must contain real numbers (int or float)")
                tmp.append(float(c))
        except InvalidTypeError:
            # re-raise our own type error untouched
            raise
        except Exception as e:
            # any other conversion error -> InvalidTypeError for a clean API
            raise InvalidTypeError("coeffs must contain real numbers (int or float)") from e

        if len(tmp) == 0:
            raise InvalidValueError("coeffs must be non-empty")

        # Strip trailing zeros but keep at least one
        i = len(tmp) - 1
        while i > 0 and tmp[i] == 0.0:
            i -= 1
        object.__setattr__(self, "coeffs", tuple(tmp[: i + 1]))


    @staticmethod
    def zeros(deg: int) -> "Polynomial":
        """
        Return the (canonical) zero polynomial.

        Parameters
        ----------
        deg : int
            Requested degree (non‑negative). This value is accepted for API symmetry,
            but the canonical zero polynomial always has degree 0 after construction.

        Returns
        -------
        Polynomial
            The zero polynomial.
        """
        if deg < 0:
            raise InvalidValueError("degree must be non-negative.")
        return Polynomial([0.0] * (deg + 1))

    @staticmethod
    def constant(c: Number) -> "Polynomial":
        """Return a constant polynomial ``p(x) = c``."""
        return Polynomial([c])

    @staticmethod
    def identity() -> "Polynomial":
        """Return the multiplicative identity polynomial ``1``."""
        return Polynomial([1.0])

    # --------------------------------- queries ----------------------------------

    @property
    def degree(self) -> int:
        """Degree of the polynomial (``len(coeffs) - 1``). By convention, ``deg(0) = 0``."""
        return len(self.coeffs) - 1

    def __call__(self, x: Number) -> Number:
        """
        Evaluate ``p(x)``.

        Parameters
        ----------
        x : float or complex
            Evaluation point.

        Returns
        -------
        float or complex
            The value ``p(x)`` computed via Horner's method with lightweight
            Kahan compensation.
        """
        return _horner_kahan(self.coeffs, x)

    # -------------------------------- calculus ----------------------------------

    def derivative(self) -> "Polynomial":
        """
        Return the analytical derivative :math:`p'(x)`.

        Notes
        -----
        If :math:`p(x) = a_0 + a_1 x + \cdots + a_n x^n`, then
        :math:`p'(x) = a_1 + 2 a_2 x + \cdots + n a_n x^{n-1}`.
        """

        if self.degree == 0:
            return Polynomial([0.0])
        der = [k * self.coeffs[k] for k in range(1, len(self.coeffs))]
        return Polynomial(der)

    def integral(self, c0: Number = 0.0) -> "Polynomial":
        """
        Return an antiderivative :math:`\int p(x)\,dx` with constant term ``c0``.

        Parameters
        ----------
        c0 : Number, default=0.0
            Constant of integration (the coefficient of :math:`x^0`).

        Returns
        -------
        Polynomial
            An antiderivative whose derivative equals ``self``.
        """
        out = [float(c0)]
        out.extend(c / (k + 1.0) for k, c in enumerate(self.coeffs))
        return Polynomial(out)

    # --------------------------------- algebra ----------------------------------

    def __add__(self, other: "Polynomial") -> "Polynomial":
        if not isinstance(other, Polynomial):
            raise InvalidTypeError("other must be Polynomial")
        n = max(self.degree, other.degree) + 1
        cs = [0.0] * n
        for i, c in enumerate(self.coeffs):
            cs[i] += c
        for i, c in enumerate(other.coeffs):
            cs[i] += c
        return Polynomial(cs)

    def __sub__(self, other: "Polynomial") -> "Polynomial":
        if not isinstance(other, Polynomial):
            raise InvalidTypeError("other must be Polynomial")
        n = max(self.degree, other.degree) + 1
        cs = [0.0] * n
        for i, c in enumerate(self.coeffs):
            cs[i] += c
        for i, c in enumerate(other.coeffs):
            cs[i] -= c
        return Polynomial(cs)

    def __mul__(self, other: "Polynomial") -> "Polynomial":
        if not isinstance(other, Polynomial):
            raise InvalidTypeError("other must be Polynomial")
        na, nb = self.degree + 1, other.degree + 1
        out = [0.0] * (na + nb - 1)
        for i, ai in enumerate(self.coeffs):
            for j, bj in enumerate(other.coeffs):
                out[i + j] += ai * bj
        return Polynomial(out)

    # --------------------------------- display ----------------------------------

    def __repr__(self) -> str:
        """Unambiguous representation, e.g. ``Polynomial(coeffs=(1.0, 2.0))``."""
        return f"Polynomial(coeffs={self.coeffs})"


    def __str__(self) -> str:
        """Human‑readable form such as ``"3x^2 + 2x + 1"`` (or ``"0"`` for the zero polynomial)."""
        terms = []
        for k, c in enumerate(self.coeffs):
            if c == 0.0:
                continue
            if k == 0:
                terms.append(f"{c:.12g}")
            elif k == 1:
                terms.append(f"{c:.12g}x")
            else:
                terms.append(f"{c:.12g}x^{k}")
        return " + ".join(reversed(terms)) if terms else "0"