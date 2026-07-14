# src/okey_solver/errors.py
from typing import Any, Dict, Optional
from okey_core.errors import OkeyCoreError, InvalidTileError


class OkeySolverError(OkeyCoreError):
    """Base exception for all okey-solver errors."""
    pass


class InvalidArrangementError(OkeySolverError):
    """Raised when an arrangement operation fails rules validation."""
    pass
