# src/okey_solver/errors.py
from typing import Any, Dict, Optional


class OkeySolverError(Exception):
    """Base exception for all okey-solver errors."""

    def __init__(self, message: str, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.payload = payload or {}


class InvalidTileError(OkeySolverError):
    """Raised when an invalid tile config is processed."""

    pass


class InvalidArrangementError(OkeySolverError):
    """Raised when an arrangement operation fails rules validation."""

    pass
