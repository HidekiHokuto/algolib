# tests/unit/maths/geometry/test_geometry_smoke.py
import math
from algolib.maths.geometry.geometry import Point, Vector, GeometryUtils

def test_point_vector_basic():
    p = Point([0, 0, 0])
    q = Point([1, 2, 2])
    v = Vector([1, 2, 2])
    assert p.dimension() == 3
    assert math.isclose(v.norm(), 3.0)
    assert math.isclose(GeometryUtils.distance(p, q), 3.0)