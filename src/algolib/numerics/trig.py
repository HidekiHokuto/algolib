# src/algolib/numerics/trig.py
from __future__ import annotations
from typing import Any
from ._backend import get_backend

def sin(x: Any) -> float:
    return get_backend().sin(x)

def cos(x: Any) -> float:
    return get_backend().cos(x)

def tan(x: Any) -> float:
    return get_backend().tan(x)