"""
Lightweight LU factorization with partial pivoting (no NumPy).

This module implements a compact LU routine intended for teaching purposes
and small dense systems. It works with built-in Python types and does not
mutate the input matrix.

Notes
-----
- We factor a square matrix ``A`` so that ``P @ A = L @ U`` with partial
  pivoting. Here ``P`` is a permutation matrix encoded by an index array
  ``piv``; ``L`` has unit diagonal and is stored in the strictly lower part of
  the combined ``LU`` matrix; ``U`` occupies the upper part including the
  diagonal.
- The permutation parity ``sign`` is ``+1`` for an even number of row swaps and
  ``-1`` for an odd number. The determinant satisfies
  ``det(A) = sign * prod(diag(U))``.
- Right-hand sides for the solver can be either a vector (length ``n``) or a
  matrix stored **by rows** with shape ``(n, nrhs)`` (each column is one RHS).

References
----------
- Golub, G. H., & Van Loan, C. F. (2013). *Matrix Computations* (4th ed.).
"""

from __future__ import annotations

from typing import List, Sequence, Tuple


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _check_square(A: Sequence[Sequence[float]]) -> int:
    """Validate squareness and return dimension ``n``.

    Parameters
    ----------
    A : Sequence[Sequence[float]]
        Candidate square matrix.

    Returns
    -------
    n : int
        Dimension of the (assumed square) matrix.

    Raises
    ------
    ValueError
        If the matrix is empty, non-rectangular, or non-square.
    """
    m = len(A)
    if m == 0:
        raise ValueError("A must be non-empty")
    n = len(A[0])
    if any(len(row) != n for row in A):
        raise ValueError("A must be rectangular with consistent row lengths")
    if m != n:
        raise ValueError("A must be square")
    return n


def _deepcopy_2d(A: Sequence[Sequence[float]]) -> List[List[float]]:
    """Create a deep copy of a 2-D list-like structure."""
    return [list(row) for row in A]


# ---------------------------------------------------------------------------
# Core API
# ---------------------------------------------------------------------------


def lu_factor(
    A: Sequence[Sequence[float]], *, piv_tol: float = 0.0
) -> Tuple[List[List[float]], List[int], int]:
    """
    Compute the LU factorization with partial pivoting.

    Parameters
    ----------
    A : Sequence[Sequence[float]]
        Square coefficient matrix. It will not be modified.
    piv_tol : float, default=0.0
        If ``abs(pivot) <= piv_tol``, the matrix is treated as singular and a
        ``ValueError`` is raised. Use a small positive value (e.g. ``1e-15``)
        to guard nearly singular systems.

    Returns
    -------
    LU : list[list[float]]
        Combined LU factors. The strictly lower part stores ``L`` (with unit
        diagonal implied); the upper part including the diagonal stores ``U``.
    piv : list[int]
        Pivot index array encoding the row permutation ``P`` such that
        row ``k`` of ``LU`` corresponds to original row ``piv[k]`` of ``A``.
    sign : int
        Permutation parity indicator. ``+1`` means an even number of row swaps,
        ``-1`` means an odd number of swaps. Useful for determinant via
        ``det(A) = sign * prod(diag(U))``.

    Raises
    ------
    ValueError
        If the matrix is not square or a zero/too-small pivot is encountered.

    Notes
    -----
    This is the Doolittle scheme with partial pivoting (``P A = L U``).
    """
    n = _check_square(A)
    LU = _deepcopy_2d(A)
    piv = list(range(n))
    sign = 1

    for k in range(n):
        # Select pivot row by maximal absolute value in the current column
        piv_row = max(range(k, n), key=lambda i: abs(LU[i][k]))
        piv_val = LU[piv_row][k]
        if abs(piv_val) <= piv_tol:
            raise ValueError(f"singular matrix: zero (or tiny) pivot at k={k}")

        # Swap rows in LU and record permutation if necessary
        if piv_row != k:
            LU[k], LU[piv_row] = LU[piv_row], LU[k]
            piv[k], piv[piv_row] = piv[piv_row], piv[k]
            sign = -sign

        # Eliminate entries below the pivot
        pivot = LU[k][k]
        for i in range(k + 1, n):
            LU[i][k] /= pivot
            lik = LU[i][k]
            row_i = LU[i]
            row_k = LU[k]
            for j in range(k + 1, n):
                row_i[j] -= lik * row_k[j]

    return LU, piv, sign


def _permute_inplace_rhs(
    b: List[float] | List[List[float]], piv: Sequence[int]
) -> None:
    """Apply the permutation ``P`` to the right-hand side ``b`` in-place.

    Parameters
    ----------
    b : list[float] or list[list[float]]
        RHS vector of length ``n`` or a matrix stored by rows with shape
        ``(n, nrhs)``.
    piv : Sequence[int]
        Pivot index array from :func:`lu_factor` encoding the row mapping such
        that row ``k`` in ``LU`` corresponds to original row ``piv[k]`` in ``A``.

    Notes
    -----
    We need ``b' = P b`` to solve ``L y = P b`` followed by ``U x = y``.
    This function reorders rows as ``b'[k] = b[piv[k]]`` using a temporary copy
    to preserve aliasing semantics.
    """
    n = len(piv)
    if isinstance(b[0], list):  # multiple RHS stored by rows (n x nrhs)
        permuted = [list(b[piv[k]]) for k in range(n)]
        for k in range(n):
            b[k] = permuted[k]
    else:  # single RHS vector (length n)
        permuted_vec = [b[piv[k]] for k in range(n)]
        for k in range(n):
            b[k] = permuted_vec[k]


def lu_solve(
    LU: Sequence[Sequence[float]],
    piv: Sequence[int],
    b: Sequence[float] | Sequence[Sequence[float]],
) -> List[float] | List[List[float]]:
    """
    Solve ``A x = b`` given a precomputed LU factorization with partial pivoting.

    Parameters
    ----------
    LU : Sequence[Sequence[float]]
        Combined LU matrix produced by :func:`lu_factor`.
    piv : Sequence[int]
        Pivot index array returned by :func:`lu_factor`.
    b : Sequence[float] or Sequence[Sequence[float]]
        Right-hand side. A 1-D sequence is treated as a vector (single RHS).
        A 2-D sequence is treated as multiple RHS arranged **by rows** with
        shape ``(n, nrhs)``.

    Returns
    -------
    x : list[float] or list[list[float]]
        Solution vector or a matrix with the same RHS layout as ``b``.

    Raises
    ------
    ValueError
        If the dimensions are incompatible.

    Notes
    -----
    Performs forward substitution (``L y = P b``) followed by back substitution
    (``U x = y``).
    """
    n = len(LU)
    if n == 0:
        raise ValueError("LU must be non-empty")

    # Normalize RHS into a mutable (n x nrhs) list of rows
    if isinstance(b[0], list):
        if len(b) != n:
            raise ValueError("b has incompatible row count")
        nrhs = len(b[0])
        if any(len(row) != nrhs for row in b):
            raise ValueError("b has inconsistent column count")
        x = [list(row) for row in b]
    else:
        if len(b) != n:
            raise ValueError("b has incompatible size")
        x = [[float(val)] for val in b]  # shape (n, 1)
        nrhs = 1

    # Apply the permutation: x <- P b
    _permute_inplace_rhs(x, piv)

    # Forward substitution: solve L y = x  (L has unit diagonal)
    for k in range(n):
        row_k = LU[k]
        for j in range(nrhs):
            s = x[k][j]
            for i in range(k):
                s -= row_k[i] * x[i][j]
            x[k][j] = s  # y_k

    # Back substitution: solve U x = y
    for k in reversed(range(n)):
        row_k = LU[k]
        diag = row_k[k]
        for j in range(nrhs):
            s = x[k][j]
            for i in range(k + 1, n):
                s -= row_k[i] * x[i][j]
            s /= diag
            x[k][j] = s

    # Return in the same shape as input b
    if nrhs == 1 and not isinstance(b[0], list):
        return [row[0] for row in x]
    return x


def lu_det(LU: Sequence[Sequence[float]], sign: int) -> float:
    """
    Compute the determinant from a precomputed LU factorization.

    Parameters
    ----------
    LU : Sequence[Sequence[float]]
        Combined LU matrix returned by :func:`lu_factor`.
    sign : int
        Permutation parity returned by :func:`lu_factor`.

    Returns
    -------
    det : float
        Determinant of the original matrix ``A``.
    """
    det = float(sign)
    for i in range(len(LU)):
        det *= LU[i][i]
    return det
