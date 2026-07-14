# src/okey_vision/errors.py


class OkeyVisionError(Exception):
    """Base exception for all okey-vision errors."""

    def __init__(self, message: str, payload: dict = None):
        super().__init__(message)
        self.payload = payload or {}


class VisionPipelineError(OkeyVisionError):
    """Raised when pipeline execution fails."""

    pass


class ProviderError(OkeyVisionError):
    """Raised when a vision provider model or api call fails."""

    pass
