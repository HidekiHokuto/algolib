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
        """
        r = self.modulus()
        if r == 0.0:
            raise InvalidValueError("cannot normalize 0+0i.")
        return Complex(self.re / r, self.im / r)

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
        Divide two complex numbers using conjugate.

        Formula
        -------
        :math:`\dfrac{a+bi}{c+di} = \dfrac{(a+bi)(c-di)}{c^2+d^2}`.

        :raises InvalidValueError: If ``other`` is zero.
        """
        if not isinstance(other, Complex):
            raise InvalidTypeError("other must be Complex.")
        den = other.re * other.re + other.im * other.im
        if den == 0.0:
            raise InvalidValueError("division by zero complex.")
        num = self * other.conjugate()
        return Complex(num.re / den, num.im / den)

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