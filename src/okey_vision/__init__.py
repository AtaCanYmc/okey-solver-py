# okey_vision/__init__.py
from okey_vision.types import BoundingBox, Detection, FrameInput, BinaryFrame
from okey_vision.frame_adapter import (
    FrameAdapter,
    PassthroughFrameAdapter,
    NumpyFrameAdapter,
    PILImageFrameAdapter,
    BytesFrameAdapter,
    Base64FrameAdapter,
    PathFrameAdapter,
    default_frame_adapters,
    adapt_to_frame_input,
)
from okey_vision.engine import (
    VisionObserver,
    VisionPipeline,
    DefaultVisionPipeline,
    VisionEngine,
)
from okey_vision.providers import (
    LocalYoloProvider,
    RoboflowProvider,
    RoboflowWorkflowProvider,
    parse_default_tile,
    LabelParserStrategy,
    FuzzyLabelParser,
)
from okey_vision.errors import OkeyVisionError, VisionPipelineError, ProviderError

__all__ = [
    "BoundingBox",
    "Detection",
    "FrameInput",
    "BinaryFrame",
    "FrameAdapter",
    "PassthroughFrameAdapter",
    "NumpyFrameAdapter",
    "PILImageFrameAdapter",
    "BytesFrameAdapter",
    "Base64FrameAdapter",
    "PathFrameAdapter",
    "default_frame_adapters",
    "adapt_to_frame_input",
    "VisionObserver",
    "VisionPipeline",
    "DefaultVisionPipeline",
    "VisionEngine",
    "LocalYoloProvider",
    "RoboflowProvider",
    "RoboflowWorkflowProvider",
    "parse_default_tile",
    "LabelParserStrategy",
    "FuzzyLabelParser",
    "OkeyVisionError",
    "VisionPipelineError",
    "ProviderError",
]

import logging
logging.getLogger("okey_vision").addHandler(logging.NullHandler())
