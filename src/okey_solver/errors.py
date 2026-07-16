# src/okey_solver/errors.py
from okey_core.errors import OkeyCoreError, InvalidTileError

__all__ = [
    "OkeySolverError",
    "InvalidArrangementError",
    "InvalidTileError",
]


class OkeySolverError(OkeyCoreError):
    """Base exception for all okey-solver errors."""

    pass


class InvalidArrangementError(OkeySolverError):
    """Raised when an arrangement operation fails rules validation."""

    pass
