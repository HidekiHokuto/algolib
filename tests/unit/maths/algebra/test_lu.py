import math
import random
import pytest

from algolib.maths.algebra.lu import lu_factor, lu_solve, lu_det


def _matmul(A, x):
    return [sum(a * b for a, b in zip(row, x)) for row in A]


def test_lu_solve_identity():
    A = [[1.0, 0.0], [0.0, 1.0]]
    b = [3.0, -2.0]
    LU, piv, sign = lu_factor(A)
    x = lu_solve(LU, piv, b)
    assert x == pytest.approx(b, rel=0, abs=0)


def test_lu_solve_small_dense():
    A = [[3.0, 2.0, -1.0],
         [2.0, -2.0, 4.0],
         [-1.0, 0.5, -1.0]]
    b = [1.0, -2.0, 0.0]
    LU, piv, sign = lu_factor(A)
    x = lu_solve(LU, piv, b)
    # residual check
    r = _matmul(A, x)
    assert r == pytest.approx(b, rel=1e-12, abs=1e-12)
    # determinant non-zero
    assert abs(lu_det(LU, sign)) > 1e-14


def test_lu_multiple_rhs():
    A = [[2.0, 1.0],
         [5.0, 7.0]]
    B = [[11.0, 1.0],
         [13.0, 0.0]]  # two RHS as columns stored by rows
    LU, piv, sign = lu_factor(A)
    X = lu_solve(LU, piv, B)
    for col in range(2):
        rhs = [B[i][col] for i in range(2)]
        prod = _matmul(A, [X[i][col] for i in range(2)])
        assert prod == pytest.approx(rhs, rel=1e-12, abs=1e-12)


def test_lu_singular_raises():
    A = [[1.0, 2.0],
         [2.0, 4.0]]  # rank-1
    with pytest.raises(ValueError):
        lu_factor(A, piv_tol=0.0)