# src/algolib/maths/algebra/__init__.py
from .matrix_dense import MatrixDense
from .polynomial import Polynomial
from .lu import lu_factor, lu_solve, lu_det

__all__ = ["MatrixDense", "Polynomial", "lu_factor", "lu_solve", "lu_det"]
