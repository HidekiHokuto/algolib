"""

A professional-grade :math:`N`-dimensional geometry library with detailed documentation.

This module implements:
    - Point: Represents a point in :math:`N`-dimensional space.
    - Vector: Represents a vector in :math:`N`-dimensional space.
    - Line: Represents a line (infinite in both directions).
    - Plane: Represents a hyperplane in :math:`N`-dimensional space.
    - GeometryUtils: Common geometric computation utilities.

"""

from typing import List, Union
import math

Number = Union[int, float]


class Point:
    """
    Represents a point in :math:`N`-dimensional Euclidean space.

    Attributes
    ----------
    coords : List[Number]
        Coordinates of the point. Length determines the dimensionality.

    Notes
    -----
    A point is a location in space, with no direction or magnitude.
    In mathematics, a point :math:`P` in :math:`N`-dimensional space is represented as:
    :math:`P = (x_1, x_2, \cdots, x_N)`
    """

    def __init__(self, coords: List[Number]):
        """
        Parameters
        ----------
        coords : list of Number
            Coordinates of the point. The list length defines the dimension.
        """
        self.coords = list(coords)

    def __repr__(self):
        return f"Point({self.coords})"

    def dimension(self) -> int:
        """
        Returns the dimensionality of the point.

        Returns
        -------
        int
            Number of coordinates.
        """
        return len(self.coords)


class Vector:
    """
    Represents a vector in :math:`N`-dimensional Euclidean space.

    Attributes
    ----------
    comps : List[Number]
        Components of the vector.

    Notes
    -----
    A vector represents both magnitude and direction.
    """

    def __init__(self, comps: List[Number]):
        self.comps = list(comps)

    def __repr__(self):
        return f"Vector({self.comps})"

    def dimension(self) -> int:
        """Return the dimensionality of the vector."""
        return len(self.comps)

    def norm(self) -> float:
        """
        Compute the Euclidean norm (length) of the vector.

        Formula
        -------
        :math:`\\|v\\| = \\sqrt{\\sum v_i^2}`

        Returns
        -------
        float
        The Euclidean length of the vector.
        """
        return math.sqrt(sum(c**2 for c in self.comps))

    def dot(self, other: 'Vector') -> float:
        """
        Compute the dot product with another vector.

        Formula
        -------
        :math:`v \cdot w = \\sum(v_i \cdot w_i)`
        """
        if self.dimension() != other.dimension():
            raise ValueError("Dot product requires vectors of the same dimension.")
        return sum(a * b for a, b in zip(self.comps, other.comps))

    def add(self, other: 'Vector') -> 'Vector':
        """Return the sum of two vectors."""
        if self.dimension() != other.dimension():
            raise ValueError("Vector addition requires same dimension.")
        return Vector([a + b for a, b in zip(self.comps, other.comps)])


class Line:
    """
    Represents an infinite line in N-dimensional space.

    Attributes
    ----------
    point : Point
        A point through which the line passes.
    direction : Vector
        The direction vector of the line.

    Notes
    -----
    A line :math:`L` can be represented parametrically as:
        :math:`L(t) = P_0 + t \cdot d`
    where:
        - :math:`P_0` = a fixed point
        - :math:`d` = direction vector (non-zero)
        - :math:`t` = real parameter
    """

    def __init__(self, point: Point, direction: Vector):
        if point.dimension() != direction.dimension():
            raise ValueError("Point and direction must have same dimension.")
        self.point = point
        self.direction = direction

    def __repr__(self):
        return f"Line(point={self.point}, direction={self.direction})"


class Plane:
    """
    Represents a hyperplane in N-dimensional space.

    Attributes
    ----------
    point : Point
        A point on the plane.
    normal : Vector
        The normal vector to the plane.

    Notes
    -----
    In :math:`N` dimensions, a hyperplane is the set of points :math:`X` satisfying:
        :math:`\\mathbf{n} \cdot (X - P_0) = 0`
    where:
        - :math:`n` = normal vector
        - :math:`P_0` = a fixed point on the plane
    """

    def __init__(self, point: Point, normal: Vector):
        if point.dimension() != normal.dimension():
            raise ValueError("Point and normal must have same dimension.")
        self.point = point
        self.normal = normal

    def __repr__(self):
        return f"Plane(point={self.point}, normal={self.normal})"


class GeometryUtils:
    """
    Utility functions for :math:`N`-dimensional geometry.
    """

    @staticmethod
    def distance(p1: Point, p2: Point) -> float:
        """
        Compute Euclidean distance between two points.

        Formula
        -------
        :math:`d = \\sqrt{\\sum(x_{1i}-x_{2i})^2}`
        """
        if p1.dimension() != p2.dimension():
            raise ValueError("Points must have same dimension.")
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1.coords, p2.coords)))