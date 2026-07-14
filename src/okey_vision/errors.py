# src/okey_vision/errors.py
from typing import Any, Dict, Optional


class OkeyVisionError(Exception):
    """Base exception for all okey-vision errors."""

    def __init__(self, message: str, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.payload = payload or {}


class VisionPipelineError(OkeyVisionError):
    """Raised when pipeline execution fails."""

    pass


class ProviderError(OkeyVisionError):
    """Raised when a vision provider model or api call fails."""

    pass
