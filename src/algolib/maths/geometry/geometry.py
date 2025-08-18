# src/algolib/maths/geometry/geometry.py
"""
A professional-grade :math:`N`-dimensional geometry module.

It implements:

- **Point**: a location in :math:`\\mathbb{R}^N`.
- **Vector**: a displacement in :math:`\\mathbb{R}^N`.
- **Line**: parametric line :math:`P(t) = P_0 + t\\,d`.
- **Plane**: hyperplane :math:`\\{X:\\; n\\cdot(X-P_0)=0\\}`.
- **GeometryUtils**: utility routines.

All classes validate dimensions and numeric inputs, and raise
:class:`algolib.exceptions.InvalidTypeError` or
:class:`algolib.exceptions.InvalidValueError` on invalid usage.
"""

from __future__ import annotations

import math
from typing import Iterable, List, Sequence, Union

from algolib.exceptions import InvalidTypeError, InvalidValueError

Number = Union[int, float]


def _ensure_numbers(xs: Iterable[Number]) -> List[float]:
    try:
        out = [float(x) for x in xs]
    except Exception as e:  # noqa: BLE001
        raise InvalidTypeError("all coordinates/components must be real numbers.") from e
    return out


def _same_dim(a_len: int, b_len: int) -> None:
    if a_len != b_len:
        raise InvalidValueError("dimensions must match.")


def _is_zero_vector(v: Sequence[float]) -> bool:
    return all(c == 0.0 for c in v)


class Point:
    r"""
    Point in :math:`N`-dimensional Euclidean space.

    Parameters
    ----------
    coords : Sequence[Number]
        Coordinates of the point; length defines the dimension.

    Notes
    -----
    A point has location but no direction or magnitude:
    :math:`P=(x_1,x_2,\\dots,x_N)`.
    """

    def __init__(self, coords: Sequence[Number]):
        cs = _ensure_numbers(coords)
        if len(cs) == 0:
            raise InvalidValueError("point must have at least one coordinate.")
        self.coords: List[float] = cs

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"Point({self.coords})"

    def dimension(self) -> int:
        """Return the dimension (number of coordinates)."""
        return len(self.coords)


class Vector:
    r"""
    Vector in :math:`N`-dimensional Euclidean space.

    Parameters
    ----------
    comps : Sequence[Number]
        Components of the vector.

    Notes
    -----
    A vector represents both magnitude and direction.
    """

    def __init__(self, comps: Sequence[Number]):
        cs = _ensure_numbers(comps)
        if len(cs) == 0:
            raise InvalidValueError("vector must have at least one component.")
        self.comps: List[float] = cs

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"Vector({self.comps})"

    def dimension(self) -> int:
        """Return the dimension (number of components)."""
        return len(self.comps)

    def norm(self) -> float:
        r"""
        Return the Euclidean norm :math:`\\lVert v\\rVert = \\sqrt{\\sum_i v_i^2}`.
        """
        return math.sqrt(sum(c * c for c in self.comps))

    def dot(self, other: "Vector") -> float:
        r"""
        Return the dot product with another vector.

        Formula
        -------
        :math:`v\\cdot w = \\sum_i v_i w_i`.
        """
        if not isinstance(other, Vector):
            raise InvalidTypeError("other must be Vector.")
        _same_dim(self.dimension(), other.dimension())
        return sum(a * b for a, b in zip(self.comps, other.comps))

    # convenience ops
    def __add__(self, other: "Vector") -> "Vector":
        """Component-wise addition."""
        if not isinstance(other, Vector):
            raise InvalidTypeError("other must be Vector.")
        _same_dim(self.dimension(), other.dimension())
        return Vector([a + b for a, b in zip(self.comps, other.comps)])

    def __sub__(self, other: "Vector") -> "Vector":
        """Component-wise subtraction."""
        if not isinstance(other, Vector):
            raise InvalidTypeError("other must be Vector.")
        _same_dim(self.dimension(), other.dimension())
        return Vector([a - b for a, b in zip(self.comps, other.comps)])

    def __mul__(self, k: Number) -> "Vector":
        """Scalar multiplication ``v * k``."""
        if not isinstance(k, (int, float)):
            raise InvalidTypeError("scalar must be real.")
        return Vector([k * a for a in self.comps])

    __rmul__ = __mul__  # k * v


class Line:
    r"""
    Parametric line :math:`P(t) = P_0 + t\\,d` in :math:`\\mathbb{R}^N`.

    Parameters
    ----------
    point : Point
        A point on the line (:math:`P_0`).
    direction : Vector
        Direction vector :math:`d` (must be non-zero).
    """

    def __init__(self, point: Point, direction: Vector):
        if not isinstance(point, Point) or not isinstance(direction, Vector):
            raise InvalidTypeError("point must be Point and direction must be Vector.")
        _same_dim(point.dimension(), direction.dimension())
        if _is_zero_vector(direction.comps):
            raise InvalidValueError("direction vector must be non-zero.")
        self.point = point
        self.direction = direction

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"Line(point={self.point}, direction={self.direction})"

    def point_at(self, t: Number) -> Point:
        """Return the point :math:`P_0 + t\\,d`."""
        if not isinstance(t, (int, float)):
            raise InvalidTypeError("t must be real.")
        return Point([p + float(t) * d for p, d in zip(self.point.coords, self.direction.comps)])

    def contains(self, p: Point, tol: float = 1e-12) -> bool:
        """
        Return True if ``p`` lies on the line (within tolerance).

        We check that :math:`p - P_0` is colinear with :math:`d` by comparing ratios;
        component pairs with :math:`|d_i| \\le \\text{tol}` are skipped.
        """
        _same_dim(self.point.dimension(), p.dimension())
        ratios = []
        for (pi, p0i), di in zip(zip(p.coords, self.point.coords), self.direction.comps):
            if abs(di) <= tol:
                if abs(pi - p0i) > tol:
                    return False  # movement along a zero direction -> off-line
                continue
            ratios.append((pi - p0i) / di)
        if not ratios:
            # direction is almost zero in all components -> treat as aligned if p == P0
            return all(abs(pi - p0i) <= tol for (pi, p0i) in zip(p.coords, self.point.coords))
        first = ratios[0]
        return all(abs(r - first) <= tol for r in ratios[1:])


class Plane:
    r"""
    Hyperplane :math:`\\{X:\\; n\\cdot(X-P_0)=0\\}` in :math:`\\mathbb{R}^N`.

    Parameters
    ----------
    point : Point
        A reference point :math:`P_0` on the plane.
    normal : Vector
        Normal vector :math:`n` (must be non-zero).
    """

    def __init__(self, point: Point, normal: Vector):
        if not isinstance(point, Point) or not isinstance(normal, Vector):
            raise InvalidTypeError("point must be Point and normal must be Vector.")
        _same_dim(point.dimension(), normal.dimension())
        if _is_zero_vector(normal.comps):
            raise InvalidValueError("normal vector must be non-zero.")
        self.point = point
        self.normal = normal

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"Plane(point={self.point}, normal={self.normal})"

    def signed_distance(self, p: Point) -> float:
        r"""
        Return signed distance :math:`\\frac{n\\cdot (p-P_0)}{\\lVert n\\rVert}`.
        """
        _same_dim(self.point.dimension(), p.dimension())
        n2 = self.normal.dot(self.normal)
        if n2 == 0.0:  # guarded at init; defensive
            raise InvalidValueError("normal vector must be non-zero.")
        diff = Vector([a - b for a, b in zip(p.coords, self.point.coords)])
        return self.normal.dot(diff) / math.sqrt(n2)

    def contains(self, p: Point, tol: float = 1e-12) -> bool:
        """Return True if ``|n·(p-P0)| <= tol * ||n||``."""
        return abs(self.signed_distance(p)) <= tol


class GeometryUtils:
    """Common geometry utilities."""

    @staticmethod
    def distance(p1: Point, p2: Point) -> float:
        r"""
        Euclidean distance :math:`\\sqrt{\\sum_i (x_{1i}-x_{2i})^2}`.
        """
        _same_dim(p1.dimension(), p2.dimension())
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1.coords, p2.coords)))