# src/algolib/exceptions.py
"""
Centralized exception hierarchy for algolib.

- Keep backward compatibility with existing exceptions:
  - AlgolibError
  - InvalidTypeError
  - InvalidValueError
- Add more specific exceptions grouped by area (args/dimension, algebra,
  geometry, numeric/convergence, feature support).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional


# -------------------- base --------------------


class AlgolibError(Exception):
    """Base exception for this library."""


# -------------------- arguments / dimensions --------------------


class InvalidTypeError(AlgolibError, TypeError):
    """Raised when an argument has an invalid type."""


class InvalidValueError(AlgolibError, ValueError):
    """Raised when an argument has an invalid value."""


class DimensionMismatchError(AlgolibError):
    """Incompatible shapes/dimensions."""

    def __init__(self, expected: Any, got: Any, message: Optional[str] = None):
        self.expected = expected
        self.got = got
        super().__init__(
            message or f"Dimension mismatch: expected {expected}, got {got}"
        )


class DegeneracyError(AlgolibError):
    """Degenerate configuration (e.g., zero-length direction, collinear)."""


# -------------------- algebra / linear algebra --------------------


class SingularMatrixError(AlgolibError):
    """Matrix is singular / not invertible."""


class NotPositiveDefiniteError(AlgolibError):
    """Matrix expected to be (strictly) positive-definite."""


# -------------------- geometry --------------------


class NoIntersectionError(AlgolibError):
    """No intersection between geometric entities."""


class AmbiguousGeometryError(AlgolibError):
    """Constraints are insufficient or solution is not unique."""


# -------------------- numeric / convergence --------------------


@dataclass
class ConvergenceError(AlgolibError):
    """Iteration did not converge within budget/tolerance."""

    iterations: int
    residual: float | None = None
    target_tol: float | None = None

    def __str__(self) -> str:
        parts = [f"ConvergenceError after {self.iterations} iterations"]
        if self.residual is not None:
            parts.append(f"residual={self.residual!r}")
        if self.target_tol is not None:
            parts.append(f"target_tol={self.target_tol!r}")
        return ", ".join(parts)


class NumericOverflowError(AlgolibError, OverflowError):
    """Numeric overflow exposed as algolib-specific error."""


class NumericUnderflowError(AlgolibError):
    """Numeric underflow to zero/denormals that invalidates the result."""


class LossOfSignificanceError(AlgolibError):
    """Severe cancellation/rounding made the result unreliable."""


class ToleranceError(AlgolibError, AssertionError):
    """An expected property did not hold within tolerance."""


# -------------------- feature / support --------------------


class NotSupportedError(AlgolibError):
    """Feature not supported in this backend/type/platform."""


class NotImplementedAlgolibError(AlgolibError, NotImplementedError):
    """Public API declared but not implemented yet."""


__all__ = [
    # base
    "AlgolibError",
    # args/dim
    "InvalidTypeError",
    "InvalidValueError",
    "DimensionMismatchError",
    "DegeneracyError",
    # algebra
    "SingularMatrixError",
    "NotPositiveDefiniteError",
    # geometry
    "NoIntersectionError",
    "AmbiguousGeometryError",
    # numeric
    "ConvergenceError",
    "NumericOverflowError",
    "NumericUnderflowError",
    "LossOfSignificanceError",
    "ToleranceError",
    # feature
    "NotSupportedError",
    "NotImplementedAlgolibError",
]
