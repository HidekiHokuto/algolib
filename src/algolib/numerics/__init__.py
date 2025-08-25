# src/algolib/numerics/__init__.py
from ._backend import set_backend, get_backend_name
from .constants import *
from .stable import hypot, hypot_n, hypot_iter

from .constants import __all__ as _CONSTANTS_ALL  # 这里直接拿 constants.py 里的

__all__ = [
    "set_backend",
    "get_backend_name",
    "hypot",
    "hypot_n",
    "hypot_iter",
    *_CONSTANTS_ALL,
    ]
