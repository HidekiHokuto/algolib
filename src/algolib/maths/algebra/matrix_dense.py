# src/algolib/maths/algebra/matrix_dense.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple, Union, overload

from algolib.exceptions import InvalidTypeError, InvalidValueError

Number = Union[int, float]


@dataclass(frozen=True)
class MatrixDense:
    """
    A simple dense matrix (row-major) without external dependencies.

    Designed for correctness and clarity (teaching/learning oriented).
    Not optimized for large-scale numerical workloads.

    Parameters
    ----------
    rows : Sequence[Sequence[Number]]
        Row-major data. Must be rectangular (all rows same length).

    Raises
    ------
    InvalidTypeError
        If rows are not sequences of numbers.
    InvalidValueError
        If matrix is empty or not rectangular.

    Examples
    --------
    >>> A = MatrixDense([[1, 2], [3, 4]])
    >>> B = MatrixDense.identity(2)
    >>> C = (A * B).rows == A.rows
    True
    """

    rows: Tuple[Tuple[Number, ...], ...]  # immutable, rectangular

    # ---------- Constructors ----------

    def __init__(self, rows: Sequence[Sequence[Number]]):
        # Validate type & rectangular
        if not isinstance(rows, Sequence) or len(rows) == 0:
            raise InvalidValueError("rows must be a non-empty sequence of sequences.")
        n_cols = None
        norm_rows: List[Tuple[Number, ...]] = []
        for r in rows:
            if not isinstance(r, Sequence) or len(r) == 0:
                raise InvalidValueError("each row must be a non-empty sequence.")
            if n_cols is None:
                n_cols = len(r)
            elif len(r) != n_cols:
                raise InvalidValueError("matrix must be rectangular (same number of columns per row).")
            # check elements are numbers
            for x in r:
                if not isinstance(x, (int, float)):
                    raise InvalidTypeError("matrix elements must be int or float.")
            norm_rows.append(tuple(x for x in r))
        object.__setattr__(self, "rows", tuple(norm_rows))

    @staticmethod
    def from_rows(rows: Sequence[Sequence[Number]]) -> "MatrixDense":
        """Construct from row-major data (alias of the constructor)."""
        return MatrixDense(rows)

    @staticmethod
    def zeros(n_rows: int, n_cols: int) -> "MatrixDense":
        """Return an :math:`(n_{\\mathrm{rows}} × n_{\\mathrm{cols}})` zero matrix."""
        if n_rows <= 0 or n_cols <= 0:
            raise InvalidValueError("matrix dimensions must be positive.")
        return MatrixDense([[0.0] * n_cols for _ in range(n_rows)])

    @staticmethod
    def identity(n: int) -> "MatrixDense":
        """Return the :math:`n \\times n` identity matrix."""
        if n <= 0:
            raise InvalidValueError("size must be positive.")
        return MatrixDense([[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)])

    eye = identity
    """Alias of :func:`identity`."""

    # ---------- Basic properties ----------

    @property
    def shape(self) -> Tuple[int, int]:
        """(n_rows, n_cols)"""
        return (len(self.rows), len(self.rows[0]))

    def copy(self) -> "MatrixDense":
        """Shallow copy (rows are tuples; safe)."""
        return MatrixDense([list(r) for r in self.rows])

    # ---------- Equality (tolerant for floats) ----------

    def equals(self, other: "MatrixDense", tol: float = 1e-12) -> bool:
        """Element-wise comparison with tolerance for floats."""
        self._check_same_shape(other)
        for ra, rb in zip(self.rows, other.rows):
            for a, b in zip(ra, rb):
                if abs(a - b) > tol:
                    return False
        return True

    # ---------- Arithmetic ----------

    def _check_same_shape(self, other: "MatrixDense") -> None:
        if self.shape != other.shape:
            raise InvalidValueError(f"shape mismatch: {self.shape} vs {other.shape}")

    def __add__(self, other: "MatrixDense") -> "MatrixDense":
        """Matrix addition."""
        self._check_same_shape(other)
        return MatrixDense([[a + b for a, b in zip(ra, rb)] for ra, rb in zip(self.rows, other.rows)])

    def __sub__(self, other: "MatrixDense") -> "MatrixDense":
        """Matrix subtraction."""
        self._check_same_shape(other)
        return MatrixDense([[a - b for a, b in zip(ra, rb)] for ra, rb in zip(self.rows, other.rows)])

    @overload
    def __mul__(self, other: Number) -> "MatrixDense":
        ...

    @overload
    def __mul__(self, other: "MatrixDense") -> "MatrixDense":
        ...

    def __mul__(self, other: Union[Number, "MatrixDense"]) -> "MatrixDense":
        """
        Scalar or matrix multiplication.

        - If `other` is a number: scale this matrix.
        - If `other` is a MatrixDense: matrix-matrix product.
        """
        if isinstance(other, (int, float)):
            return MatrixDense([[a * other for a in r] for r in self.rows])
        if isinstance(other, MatrixDense):
            a_rows, a_cols = self.shape
            b_rows, b_cols = other.shape
            if a_cols != b_rows:
                raise InvalidValueError(f"incompatible shapes for matmul: {self.shape} * {other.shape}")
            out = []
            # naive triple loop (clear & correct)
            for i in range(a_rows):
                row = []
                for j in range(b_cols):
                    s = 0.0
                    for k in range(a_cols):
                        s += self.rows[i][k] * other.rows[k][j]
                    row.append(s)
                out.append(row)
            return MatrixDense(out)
        raise InvalidTypeError("unsupported operand for *: MatrixDense and non-(number|MatrixDense)")

    def __rmul__(self, other: Number) -> "MatrixDense":
        """Right scalar multiplication."""
        return self.__mul__(other)

    def matvec(self, v: Sequence[Number]) -> List[float]:
        """
        Matrix-vector product (Ax).

        Parameters
        ----------
        v : Sequence[Number]
            Vector of length equal to number of columns.

        Returns
        -------
        list[float]
            Resulting vector.
        """
        n_rows, n_cols = self.shape
        if not isinstance(v, Sequence) or len(v) != n_cols:
            raise InvalidValueError(f"vector length must be {n_cols}")
        for x in v:
            if not isinstance(x, (int, float)):
                raise InvalidTypeError("vector elements must be numbers.")
        out: List[float] = []
        for i in range(n_rows):
            s = 0.0
            for j in range(n_cols):
                s += self.rows[i][j] * v[j]
            out.append(s)
        return out

    # ---------- Linear algebra helpers (small n) ----------

    def T(self) -> "MatrixDense":
        """Transpose."""
        n_rows, n_cols = self.shape
        return MatrixDense([[self.rows[i][j] for i in range(n_rows)] for j in range(n_cols)])

    def det(self) -> float:
        """
        Determinant via Gaussian elimination with partial pivoting (O(n^3)).

        Raises
        ------
        InvalidValueError
            If matrix is not square.
        """
        n, m = self.shape
        if n != m:
            raise InvalidValueError("determinant is defined for square matrices.")
        # Work on a mutable copy
        a = [list(r) for r in self.rows]
        sign = 1.0
        det_val = 1.0
        for i in range(n):
            # pivot
            pivot_row = max(range(i, n), key=lambda r: abs(a[r][i]))
            if abs(a[pivot_row][i]) < 1e-15:
                return 0.0
            if pivot_row != i:
                a[i], a[pivot_row] = a[pivot_row], a[i]
                sign *= -1.0
            pivot = a[i][i]
            det_val *= pivot
            # eliminate
            for r in range(i + 1, n):
                factor = a[r][i] / pivot
                if factor == 0:
                    continue
                for c in range(i, n):
                    a[r][c] -= factor * a[i][c]
        return float(sign * det_val)

    def inv(self) -> "MatrixDense":
        """
        Inverse via Gauss-Jordan elimination (O(n^3)).

        Raises
        ------
        InvalidValueError
            If matrix is not square or singular.
        """
        n, m = self.shape
        if n != m:
            raise InvalidValueError("inverse is defined for square matrices.")
        # augmented [A | I]
        A = [list(row) + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(self.rows)]

        # Gauss-Jordan with partial pivoting
        for col in range(n):
            # pivot
            pivot_row = max(range(col, n), key=lambda r: abs(A[r][col]))
            if abs(A[pivot_row][col]) < 1e-15:
                raise InvalidValueError("matrix is singular; cannot invert.")
            if pivot_row != col:
                A[col], A[pivot_row] = A[pivot_row], A[col]
            pivot = A[col][col]
            # normalize pivot row
            inv_p = 1.0 / pivot
            for j in range(2 * n):
                A[col][j] *= inv_p
            # eliminate other rows
            for r in range(n):
                if r == col:
                    continue
                factor = A[r][col]
                if factor == 0:
                    continue
                for j in range(2 * n):
                    A[r][j] -= factor * A[col][j]

        inv_rows = [row[n:] for row in A]
        return MatrixDense(inv_rows)
