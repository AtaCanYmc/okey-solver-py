# okey_core/errors.py
from typing import Any, Dict, Optional


class OkeyCoreError(Exception):
    """Base exception for all okey-core errors."""

    def __init__(self, message: str, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.payload = payload or {}


class InvalidTileError(OkeyCoreError):
    """Raised when an invalid tile config is processed."""

    pass
