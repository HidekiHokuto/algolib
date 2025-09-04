# tests/maths/algebra/test_matrix_dense.py
import math
import pytest

from algolib.maths.algebra import MatrixDense
from algolib.exceptions import InvalidValueError, InvalidTypeError


def test_basic_shape_and_identity():
    A = MatrixDense([[1, 2], [3, 4]])
    assert A.shape == (2, 2)
    I = MatrixDense.identity(2)
    assert (A * I).equals(A)
    assert (I * A).equals(A)


def test_add_sub():
    A = MatrixDense([[1, 2], [3, 4]])
    B = MatrixDense([[5, 6], [7, 8]])
    C = MatrixDense([[6, 8], [10, 12]])
    assert (A + B).equals(C)
    assert (C - B).equals(A)


def test_scalar_mul_and_matmul():
    A = MatrixDense([[1, 2, 3], [4, 5, 6]])
    B = 2 * A
    assert B.equals(MatrixDense([[2, 4, 6], [8, 10, 12]]))
    # matmul
    M = MatrixDense([[1, 0], [0, 1], [1, -1]])  # 3x2
    # A(2x3) * M(3x2) => 2x2
    P = A * M
    assert P.equals(
        MatrixDense(
            [
                [1 + 0 + 3 * 1, 0 + 2 * 1 + 3 * (-1)],
                [4 + 0 + 6 * 1, 0 + 5 * 1 + 6 * (-1)],
            ]
        )
    )


def test_matvec_and_transpose():
    A = MatrixDense([[1, 2], [3, 4], [5, 6]])
    v = [10, -2]
    assert A.matvec(v) == [1 * 10 + 2 * (-2), 3 * 10 + 4 * (-2), 5 * 10 + 6 * (-2)]
    assert A.T().equals(MatrixDense([[1, 3, 5], [2, 4, 6]]))


def test_determinant_and_inverse_2x2():
    A = MatrixDense([[4, 7], [2, 6]])
    detA = A.det()
    assert abs(detA - (4 * 6 - 7 * 2)) < 1e-12
    invA = A.inv()
    # A * A^{-1} = I
    I = MatrixDense.identity(2)
    assert (A * invA).equals(I, tol=1e-10)
    assert (invA * A).equals(I, tol=1e-10)


def test_invalid_inputs():
    with pytest.raises(InvalidValueError):
        MatrixDense([])  # empty
    with pytest.raises(InvalidValueError):
        MatrixDense([[1, 2], [3]])  # ragged
    with pytest.raises(InvalidTypeError):
        MatrixDense([["x", 2]])  # non-number element
    with pytest.raises(InvalidValueError):
        MatrixDense.identity(0)
    with pytest.raises(InvalidValueError):
        MatrixDense.zeros(2, 0)
    with pytest.raises(InvalidValueError):
        MatrixDense([[1, 2]]).matvec([1, 2, 3])  # length mismatch
    with pytest.raises(InvalidTypeError):
        MatrixDense([[1, 2]]).matvec([1, "x"])  # non-number
    with pytest.raises(InvalidValueError):
        MatrixDense([[1, 2, 3], [4, 5, 6]]).det()  # non-square
    with pytest.raises(InvalidValueError):
        MatrixDense([[1, 2], [2, 4]]).inv()  # singular


def test_compare_equals_tolerance():
    A = MatrixDense([[1.0, 2.0], [3.0, 4.0]])
    B = MatrixDense([[1.0, 2.0 + 1e-13], [3.0, 4.0]])
    assert A.equals(B)  # within default tol
    assert not A.equals(B, tol=1e-15)
