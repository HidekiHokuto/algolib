from __future__ import annotations
from typing import Any
from ._backend import get_backend

def sin(x: Any) -> float:
    """
    Sine of an angle (system backend).

    Parameters
    ----------
    x : float
        Input angle in radians.

    Returns
    -------
    float
        ``sin(x)`` evaluated by the active numerics backend.
    """
    return get_backend().sin(x)

def cos(x: Any) -> float:
    """
    Cosine of an angle (system backend).

    Parameters
    ----------
    x : float
        Input angle in radians.

    Returns
    -------
    float
        ``cos(x)`` evaluated by the active numerics backend.
    """
    return get_backend().cos(x)

def tan(x: Any) -> float:
    """
    Tangent of an angle (system backend).

    Notes
    -----
    Argument-reduction and non-finite handling are performed inside the
    active backend (see ``_backend.SystemTrigBackend.tan``). Keeping this
    wrapper free of extra reduction ensures consistent periodicity tests.

    Parameters
    ----------
    x : float
        Input angle in radians.

    Returns
    -------
    float
        ``tan(x)`` evaluated by the active numerics backend.
    """
    return get_backend().tan(x)