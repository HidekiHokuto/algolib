# src/algolib/numerics/pow.py
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from algolib.core.complex import Complex

Number = Union[int, float, "Complex"]


def pow(base: Number, exp: Any) -> Number:
    r"""
    Compute `base` raised to the exponent `exp`.

    This is a thin wrapper around Python's built-in exponentiation operator (`**`),
    provided for API consistency within algolib. For built-in numeric types (int, float),
    this function behaves exactly like `base ** exp`. For `algolib.core.complex.Complex`,
    integer exponents are supported via its `__pow__` implementation.

    Parameters
    ----------
    base : int or float or :class:`~algolib.core.complex.Complex`
        The base value.
    exp : Any
        The exponent. For built-in numeric types this follows Python semantics.
        For :class:`~algolib.core.complex.Complex`, only integer exponents are guaranteed to be supported.

    Returns
    -------
    int or float or :class:`~algolib.core.complex.Complex`
        The result of `base ** exp`.

    Notes
    -----
    - No attempt is made here to alter Python's semantics or to perform domain checking.
    - For :class:`~algolib.core.complex.Complex`, non-integer exponents return `NotImplemented` from `__pow__`,
        so the caller may need to handle that case if used directly.
    """
    return base**exp
