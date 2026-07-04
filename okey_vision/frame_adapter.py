# okey_vision/frame_adapter.py
import base64
import os
from typing import Any, List, Protocol
from PIL import Image
import numpy as np
import cv2
from okey_vision.types import FrameInput


class FrameAdapter(Protocol):
    def can_adapt(self, input_val: Any) -> bool: ...
    def adapt(self, input_val: Any) -> FrameInput: ...


class PassthroughFrameAdapter:
    def can_adapt(self, input_val: Any) -> bool:
        return isinstance(input_val, FrameInput)

    def adapt(self, input_val: Any) -> FrameInput:
        return input_val


class NumpyFrameAdapter:
    def can_adapt(self, input_val: Any) -> bool:
        return isinstance(input_val, np.ndarray)

    def adapt(self, input_val: Any) -> FrameInput:
        h, w = input_val.shape[:2]
        return FrameInput(data=input_val, width=w, height=h, mime_type="image/raw")


class PILImageFrameAdapter:
    def can_adapt(self, input_val: Any) -> bool:
        return isinstance(input_val, Image.Image)

    def adapt(self, input_val: Any) -> FrameInput:
        # Convert PIL to Numpy array
        arr = np.array(input_val)
        w, h = input_val.size
        return FrameInput(data=arr, width=w, height=h, mime_type="image/raw")


class BytesFrameAdapter:
    def can_adapt(self, input_val: Any) -> bool:
        return isinstance(input_val, (bytes, bytearray))

    def adapt(self, input_val: Any) -> FrameInput:
        nparr = np.frombuffer(input_val, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return FrameInput(data=input_val, mime_type="application/octet-stream")
        h, w = img.shape[:2]
        return FrameInput(data=img, width=w, height=h, mime_type="image/raw")


class Base64FrameAdapter:
    def can_adapt(self, input_val: Any) -> bool:
        if not isinstance(input_val, str):
            return False
        return (
            input_val.startswith("data:image") or len(input_val) > 100
        )  # Simple heuristic

    def adapt(self, input_val: Any) -> FrameInput:
        if "," in input_val:
            input_val = input_val.split(",")[1]
        decoded = base64.b64decode(input_val)
        nparr = np.frombuffer(decoded, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return FrameInput(data=decoded, mime_type="application/octet-stream")
        h, w = img.shape[:2]
        return FrameInput(data=img, width=w, height=h, mime_type="image/raw")


class PathFrameAdapter:
    def can_adapt(self, input_val: Any) -> bool:
        return isinstance(input_val, str) and os.path.exists(input_val)

    def adapt(self, input_val: Any) -> FrameInput:
        img = cv2.imread(input_val)
        if img is None:
            raise ValueError(f"Could not read image from path: {input_val}")
        h, w = img.shape[:2]
        return FrameInput(data=img, width=w, height=h, mime_type="image/raw")


def default_frame_adapters() -> List[FrameAdapter]:
    return [
        PassthroughFrameAdapter(),
        NumpyFrameAdapter(),
        PILImageFrameAdapter(),
        BytesFrameAdapter(),
        Base64FrameAdapter(),
        PathFrameAdapter(),
    ]


def adapt_to_frame_input(input_val: Any, adapters: List[FrameAdapter]) -> FrameInput:
    for adapter in adapters:
        if adapter.can_adapt(input_val):
            return adapter.adapt(input_val)
    raise ValueError("No frame adapter found for the provided input.")
