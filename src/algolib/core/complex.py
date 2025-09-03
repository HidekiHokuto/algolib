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

from algolib.exceptions import InvalidTypeError, InvalidValueError, NotImplementedAlgolibError
from algolib.numerics import hypot
from algolib.numerics.trig_pure import sin, cos
from algolib.numerics.sqrt import newton_sqrt as sqrt


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
        """
        Post-initialization validation and normalization.

        Ensures that the real and imaginary parts are valid numbers (int or float)
        and converts them to floats for consistency.

        Raises
        ------
        InvalidTypeError
        If `re` or `im` is not a real number.
        """
        if not isinstance(self.re, (int, float)) or not isinstance(self.im, (int, float)):
            raise InvalidTypeError("re and im must be real numbers (int or float).")

        # freeze as floats (even if ints given)
        object.__setattr__(self, "re", float(self.re))
        object.__setattr__(self, "im", float(self.im))

    @staticmethod
    def from_polar(r: Number, theta: Number) -> "Complex":
        r"""
        Construct a complex number from polar coordinates.

        Parameters
        ----------
        r : float
            The modulus (radius) of the complex number. Must be non-negative.
        theta : float
            The argument (angle in radians) of the complex number.

        Returns
        -------
        Complex
            The complex number corresponding to the polar coordinates.

        Raises
        ------
        InvalidTypeError
            If `r` or `theta` is not a real number.
        InvalidValueError
            If `r` is negative.

        Examples
        --------
        >>> z = Complex.from_polar(2, math.pi / 2)
        >>> z
        Complex(re=1.2246467991473532e-16, im=2.0)
        """
        if not isinstance(r, (int, float)) or not isinstance(theta, (int, float)):
            raise InvalidTypeError("r and theta must be real numbers (int or float).")
        if r < 0:
            raise InvalidValueError(f"radius r must be non-negative, got {r}")
        return Complex(r * cos(theta), r * sin(theta))

    @staticmethod
    def from_cartesian(re: Number, im: Number) -> "Complex":
        """
        Construct a complex number from Cartesian coordinates.

        Parameters
        ----------
        re : float
            The real part of the complex number.
        im : float
            The imaginary part of the complex number.

        Returns
        -------
        Complex
            The complex number corresponding to the Cartesian coordinates.

        Examples
        --------
        >>> z = Complex.from_cartesian(3, 4)
        >>> z
        Complex(re=3.0, im=4.0)
        """
        return Complex(re, im)

    @staticmethod
    def from_iterable(pair: Iterable[Number]) -> "Complex":
        r"""
        Construct a complex number from an iterable of two numbers.

        Parameters
        ----------
        pair : Iterable[float]
            An iterable containing exactly two elements: the real and imaginary parts.

        Returns
        -------
        Complex
            The complex number constructed from the iterable.

        Raises
        ------
        InvalidTypeError
            If the iterable does not contain exactly two numeric elements.

        Examples
        --------
        >>> z = Complex.from_iterable([3, 4])
        >>> z
        Complex(re=3.0, im=4.0)
        """
        try:
            re, im = pair  # type: ignore[misc]
        except Exception as e:  # noqa: BLE001
            raise InvalidTypeError("pair must be an iterable of length 2 (re, im).") from e
        return Complex(re, im)

    # ------------------------------- properties ---------------------------------

    def to_tuple(self) -> Tuple[Number, Number]:
        r"""
        Convert the complex number to a tuple of its real and imaginary parts.

        Returns
        -------
        tuple of float
            A tuple `(re, im)` representing the real and imaginary parts.

        Examples
        --------
        >>> z = Complex(3, 4)
        >>> z.to_tuple()
        (3.0, 4.0)
        """
        return (self.re, self.im)

    # --------------------------------- queries ----------------------------------

    def modulus(self) -> float:
        r"""
        Compute the modulus (absolute value) of the complex number.

        Returns
        -------
        float
            The modulus :math:`\sqrt{a^2 + b^2}`.

        Examples
        --------
        >>> z = Complex(3, 4)
        >>> z.modulus()
        5.0
        """
        x, y = abs(self.re), abs(self.im)
        if x < y:
            x, y = y, x
        if x == 0.0:  # avoid 0/0
            return 0.0
        r = y / x
        return x * (1.0 + r * r) ** 0.5

    def argument(self) -> float:
        r"""
        Compute the principal argument of the complex number.

        Returns
        -------
        float
            The argument (angle in radians) in the range :math:`(-\pi, \pi]`.

        Examples
        --------
        >>> z = Complex(0, 1)
        >>> z.argument()
        1.5707963267948966
        """
        return math.atan2(self.im, self.re)

    def conjugate(self) -> "Complex":
        r"""
        Compute the complex conjugate of the number.

        Returns
        -------
        Complex
            The conjugate :math:`a - b \mathrm{i}`.

        Examples
        --------
        >>> z = Complex(3, 4)
        >>> z.conjugate()
        Complex(re=3.0, im=-4.0)
        """
        return Complex(self.re, -self.im)

    def normalized(self) -> "Complex":
        r"""
        Normalize the complex number by :math:`z/|z|` to have a modulus of 1.

        Returns
        -------
        Complex
            The normalized complex number.

        Raises
        ------
        InvalidValueError
            If the complex number is zero.

        Examples
        --------
        >>> z = Complex(3, 4)
        >>> z.normalized()
        Complex(re=0.6, im=0.8)
        """
        # r = math.hypot(self.re, self.im)
        r = hypot(self.re, self.im)
        if r == 0.0:
            raise InvalidValueError("cannot normalize 0+0i.")
        # normalize first
        x, y = self.re / r, self.im / r
        # compute modulus squared after normalization; should be 1 in theory but rounding occurs
        m2 = x * x + y * y
        # apply one-time scaling to adjust modulus back to 1
        # note: sqrt and multiplication introduce tiny rounding errors, but within ~1e-15
        if m2 != 1.0 and m2 > 0.0 and math.isfinite(m2):
            adj = 1.0 / sqrt(m2)
            x, y = x * adj, y * adj
        return Complex(x, y)

    # ---------------------------------- algebra ---------------------------------

    def __add__(self, other: "Complex") -> "Complex":
        """
        Add two complex numbers.

        Parameters
        ----------
        other : :class:`Complex`
            The complex number to add.

        Returns
        -------
        :class:`Complex`
            The sum of the two complex numbers.

        Raises
        ------
        InvalidTypeError
            If ``other`` is not :class:`Complex`.

        Examples
        --------
        >>> z1 = Complex(3, 4)
        >>> z2 = Complex(1, -1)
        >>> z1 + z2
        Complex(re=4.0, im=3.0)
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

        # ---- unified scaling to avoid overflow/underflow ----
        scale = max(abs(a), abs(b), abs(c), abs(d))
        if scale > 0.0:
            a /= scale
            b /= scale
            c /= scale
            d /= scale
        # if scale==0, this means self==0 and other!=0, applying formulas directly is safe

        ac = abs(c)
        ad = abs(d)
        if ac >= ad:
            # |c| >= |d|
            t = d / c  # |t| <= 1
            denom = c + d * t  # numerically ~ (c^2 + d^2)/c
            re = (a + b * t) / denom
            im = (b - a * t) / denom
        else:
            t = c / d  # |t| <= 1
            denom = d + c * t  # numerically ~ (c^2 + d^2)/d
            re = (a * t + b) / denom
            im = (b * t - a) / denom

        return Complex(re, im)

    def __neg__(self) -> "Complex":
        """Unary minus."""
        return Complex(-self.re, -self.im)

    def __abs__(self) -> float:
        """Builtin ``abs(z)`` -> modulus."""
        return self.modulus()

    def __pow__(self, exponent: int) -> "Complex":
        r"""
        Raise this Complex number to an integer power.

        Implements exponentiation by squaring for integer exponents.
        Non-integer exponents are not supported here and will return
        NotImplemented to allow the Python runtime to dispatch elsewhere.

        Parameters
        ----------
        exponent : int
            The integer exponent. Booleans are treated as integers.

        Returns
        -------
        Complex
            The result of raising `self` to `exponent`.

        Notes
        -----
        - This implementation does not import any external math library.
        - Negative exponents are handled via reciprocal:
            `self ** (-n)` is computed first (with `n > 0`), then inverted.
        """
        # Accept bool as int (True -> 1, False -> 0)
        if isinstance(exponent, bool):
            exponent = int(exponent)

        if not isinstance(exponent, int):
            return NotImplementedAlgolibError # defer to other implementations if any

        # 0-th power yields multiplicative identity 1 + 0i
        if exponent == 0:
            return type(self)(1.0, 0.0)

        # Handle negative exponents via reciprocal
        if exponent < 0:
            pos = -exponent
            return type(self)(1.0, 0.0) / (self.__pow__(pos))

        # Fast exponentiation (exponentiation by squaring)
        result = type(self)(1.0, 0.0)
        base = self
        n =  exponent

        while n > 0:
            if n & 1:
                result = result * base
            base = base * base
            n >>= 1

        return result

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
        r"""
        Convert the complex number to polar coordinates.

        Returns
        -------
        tuple of float
            A tuple ``(r, theta)`` where ``r`` is the modulus and ``theta`` is the argument.

        Examples
        --------
        >>> z = Complex(3, 4)
        >>> z.to_polar()
        (5.0, 0.9272952180016122)
        """
        return (self.modulus(), self.argument())

    # --------------------------------- display ----------------------------------

    def __repr__(self) -> str:
        return f"Complex(re={self.re:.12g}, im={self.im:.12g})"

    def __str__(self) -> str:
        sign = "+" if self.im >= 0 else "-"
        return f"{self.re:.12g} {sign} {abs(self.im):.12g}i"
