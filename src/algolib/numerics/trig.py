# src/algolib/numerics/trig.py
from __future__ import annotations
from typing import Any
from ._backend import get_backend
import math
import algolib.numerics.constants as C

def sin(x: Any) -> float:
    return get_backend().sin(x)

def cos(x: Any) -> float:
    return get_backend().cos(x)

def tan(x: Any) -> float:
    xr = math.remainder(x, C.TAU)
    return get_backend().tan(x)