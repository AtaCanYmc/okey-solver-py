# src/okey_vision/errors.py


class OkeyVisionError(Exception):
    """Base exception for all okey-vision errors."""

    pass


class VisionPipelineError(OkeyVisionError):
    """Raised when pipeline execution fails."""

    pass


class ProviderError(OkeyVisionError):
    """Raised when a vision provider model or api call fails."""

    pass
