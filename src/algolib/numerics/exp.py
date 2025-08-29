# src/algolib/numerics/exp.py
from __future__ import annotations

from typing import Final

# NOTE: We intentionally avoid importing math to keep numerics self-contained.

# Split constants for ln(2) to reduce cancellation during range reduction.

LN2_HI: Final[float] = 0.

