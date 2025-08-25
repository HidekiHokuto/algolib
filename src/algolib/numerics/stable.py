# src/algolib/numerics/stable.py

from __future__ import annotations
from typing import Iterable
import math

def hypot(x: float, y: float) -> float:
    r"""
    Stable :math:`\sqrt{x^2 + y^2}` with overflow/underflow protections.
    """
    x, y = abs(x), abs(y)
    if x < y:
        x, y = y, x
    if x == 0.0:
        return 0.0
    r = y / x # |r| <= 1
    return x * math.sqrt(1.0 + r*r)

def hypot_n(*xs: float) -> float:
    r"""
    Stable Euclidean norm for :math:`N` components:
    :math:`\sqrt{\sum_i xs[i]^2}`.
    """
    acc = 0.0
    for v in xs:
        acc = hypot(acc, float(v))
    return acc

def hypot_iter(vals: Iterable[float]) -> float:
    acc = 0.0
    for v in vals:
        acc = hypot(acc, float(v))
    return acc
