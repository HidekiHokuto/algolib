# src/algolib/maths/complex/complex.py
"""
A lightweight Complex number implementation (without using Python's built-in ``complex``).

This module provides a small, well-documented ``Complex`` class suitable for learning
and algorithmic implementations. It supports algebraic form (a + bi) and polar form
(r·e^{iθ}), with common operations.

Notes
-----
- This class uses plain floats and is immutable.
- We intentionally avoid Python's built-in :class:`complex` to practice fundamentals.

Examples
--------
>>> z1 = Complex(3, 4)
>>> z1.modulus()
5.0
>>> z2 = Complex.from_polar(2, math.pi/2)
>>> (z1 + z2).re  # doctest: +ELLIPSIS
3.0
>>> (z1.conjugate()).im
-4.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Tuple

from algolib.exceptions import InvalidTypeError, InvalidValueError


Number = float  # for readability


@dataclass(frozen=True)
class Complex:
    """
    Complex number in algebraic form :math:`a + b \\mathrm{i}`.

    Parameters
    ----------
    re : float
        Real part :math:`a`.
    im : float
        Imaginary part :math:`b`.

    Raises
    ------
    InvalidTypeError
        If either part is not a real number (int/float).
    """

    re: Number
    im: Number

    # ------------------------------- constructors -------------------------------

    def __post_init__(self) -> None:
        if not isinstance(self.re, (int, float)) or not isinstance(self.im, (int, float)):
            raise InvalidTypeError("re and im must be real numbers (int or float).")

        # freeze as floats (even if ints given)
        object.__setattr__(self, "re", float(self.re))
        object.__setattr__(self, "im", float(self.im))

    @staticmethod
    def from_polar(r: Number, theta: Number) -> "Complex":
        """
        Construct from polar coordinates :math:`(r, \\theta)`.

        :param r: Modulus (radius). Must be non-negative.
        :param theta: Argument (angle in radians).
        :raises InvalidValueError: If ``r < 0``.
        :returns: Complex number corresponding to :math:`r(\\cos\\theta + i\\sin\\theta)`.
        """
        if not isinstance(r, (int, float)) or not isinstance(theta, (int, float)):
            raise InvalidTypeError("r and theta must be real numbers (int or float).")
        if r < 0:
            raise InvalidValueError(f"radius r must be non-negative, got {r}")
        return Complex(r * math.cos(theta), r * math.sin(theta))

    @staticmethod
    def from_cartesian(re: Number, im: Number) -> "Complex":
        """
        Construct from Cartesian coordinates (re, im).
        :param re: Real part.
        :param im: Imaginary part.
        :returns: Complex number corresponding to :math:`(re, im)`.
        """
        return Complex(re, im)

    @staticmethod
    def from_iterable(pair: Iterable[Number]) -> "Complex":
        """
        Construct from an iterable of two numbers.

        :param pair: Iterable ``(re, im)``.
        :raises InvalidTypeError: If iterable does not have exactly two numeric elements.
        """
        try:
            re, im = pair  # type: ignore[misc]
        except Exception as e:  # noqa: BLE001
            raise InvalidTypeError("pair must be an iterable of length 2 (re, im).") from e
        return Complex(re, im)

    # ------------------------------- properties ---------------------------------

    def to_tuple(self) -> Tuple[Number, Number]:
        """Return ``(re, im)``."""
        return (self.re, self.im)

    # --------------------------------- queries ----------------------------------

    def modulus(self) -> float:
        r"""
        Return the modulus :math:`\\abs{z} = \\sqrt{a^2 + b^2}`.
        """
        # hypot is stable for large/small numbers
        return math.hypot(self.re, self.im)

    def argument(self) -> float:
        r"""
        Return the principal argument :math:`\arg z \in (-\pi, \pi]`.

        Uses :func:`math.atan2`.
        """
        return math.atan2(self.im, self.re)

    def conjugate(self) -> "Complex":
        r"""
        Return the complex conjugate :math:`\overline{z} = a - b i`.
        """
        return Complex(self.re, -self.im)

    def normalized(self) -> "Complex":
        r"""
        Return :math:`z / |z|`. Raises if :math:`z = 0`.

        This implementation performs a second, tiny rescaling step so that the
        final norm is ~1 within a few ULP even for subnormals.
        """
        r = math.hypot(self.re, self.im)
        if r == 0.0:
            raise InvalidValueError("cannot normalize 0+0i.")
        # 先标准化
        x, y = self.re / r, self.im / r
        # 计算（标准化后）的模长平方，理论应为 1，但会有舍入
        m2 = x * x + y * y
        # 用一次性的缩放把模长“微校准”到 1
        # 注意：sqrt 和乘法的舍入会再带来极小误差，但会压到 ~1e-15 量级
        if m2 != 1.0 and m2 > 0.0 and math.isfinite(m2):
            adj = 1.0 / math.sqrt(m2)
            x, y = x * adj, y * adj
        return Complex(x, y)

    # ---------------------------------- algebra ---------------------------------

    def __add__(self, other: "Complex") -> "Complex":
        """
        Add two complex numbers (component-wise).

        :raises InvalidTypeError: If ``other`` is not :class:`Complex`.
        """
        if not isinstance(other, Complex):
            raise InvalidTypeError("other must be Complex.")
        return Complex(self.re + other.re, self.im + other.im)

    def __sub__(self, other: "Complex") -> "Complex":
        """
        Subtract two complex numbers.
        """
        if not isinstance(other, Complex):
            raise InvalidTypeError("other must be Complex.")
        return Complex(self.re - other.re, self.im - other.im)

    def __mul__(self, other: "Complex") -> "Complex":
        r"""
        Multiply two complex numbers.

        Formula
        -------
        :math:`(a+bi)(c+di) = (ac - bd) + (ad + bc)i`.
        """
        if not isinstance(other, Complex):
            raise InvalidTypeError("other must be Complex.")
        a, b, c, d = self.re, self.im, other.re, other.im
        return Complex(a * c - b * d, a * d + b * c)

    def __truediv__(self, other: "Complex") -> "Complex":
        r"""
        Robust complex division using scaling + Smith's algorithm to avoid overflow/underflow.

        For z = a+bi, w = c+di:
          1) scale = max(|a|,|b|,|c|,|d|) ; divide all by scale (if scale>0)
          2) use Smith's branch on the scaled values.
        """
        if not isinstance(other, Complex):
            raise InvalidTypeError("other must be Complex.")
        a, b = self.re, self.im
        c, d = other.re, other.im
        if c == 0.0 and d == 0.0:
            raise InvalidValueError("division by zero complex.")

        # ---- 统一缩放，避免中间量溢出/下溢 ----
        scale = max(abs(a), abs(b), abs(c), abs(d))
        if scale > 0.0:
            a /= scale;
            b /= scale;
            c /= scale;
            d /= scale
        # 若 scale==0，这里意味着 self==0 且 other!=0，直接走下面公式也安全

        ac = abs(c)
        ad = abs(d)
        if ac >= ad:
            # |c| >= |d|
            t = d / c  # |t| <= 1
            denom = c + d * t  # 数值上 ~ (c^2 + d^2)/c
            re = (a + b * t) / denom
            im = (b - a * t) / denom
        else:
            t = c / d  # |t| <= 1
            denom = d + c * t  # 数值上 ~ (c^2 + d^2)/d
            re = (a * t + b) / denom
            im = (b * t - a) / denom

        return Complex(re, im)

    def __neg__(self) -> "Complex":
        """Unary minus."""
        return Complex(-self.re, -self.im)

    def __abs__(self) -> float:
        """Builtin ``abs(z)`` -> modulus."""
        return self.modulus()

    # ------------------------------- comparisons --------------------------------

    def almost_equal(self, other: "Complex", tol: float = 1e-12) -> bool:
        """
        Return True if each component differs by at most ``tol`` (absolute).

        This is safer than exact float equality.
        """
        if not isinstance(other, Complex):
            return False
        return (abs(self.re - other.re) <= tol) and (abs(self.im - other.im) <= tol)

    def __eq__(self, other: object) -> bool:  # exact equality
        if not isinstance(other, Complex):
            return NotImplemented
        return self.re == other.re and self.im == other.im

    # --------------------------------- polar ------------------------------------

    def to_polar(self) -> Tuple[float, float]:
        """
        Return ``(r, theta)`` with :math:`r = |z|` and :math:`\\theta = \\arg z`.
        """
        return (self.modulus(), self.argument())

    # --------------------------------- display ----------------------------------

    def __repr__(self) -> str:
        return f"Complex(re={self.re:.12g}, im={self.im:.12g})"

    def __str__(self) -> str:
        sign = "+" if self.im >= 0 else "-"
        return f"{self.re:.12g} {sign} {abs(self.im):.12g}i"