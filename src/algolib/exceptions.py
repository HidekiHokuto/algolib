# src/algolib/exceptions.py
class AlgolibError(Exception):
    """Base exception for this library."""

class InvalidTypeError(AlgolibError, TypeError):
    """Raised when an argument has an invalid type."""

class InvalidValueError(AlgolibError, ValueError):
    """Raised when an argument has an invalid value."""