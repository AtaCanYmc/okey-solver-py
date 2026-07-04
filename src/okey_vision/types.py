# okey_vision/types.py
from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict
import numpy as np


class BoundingBox(BaseModel):
    x: float
    y: float
    width: float
    height: float


class Detection(BaseModel):
    id: str
    bounds: BoundingBox
    confidence: float
    label: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# In Python, we can support multiple types of binary/image frames natively.
BinaryFrame = Union[str, bytes, bytearray, np.ndarray]


class FrameInput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    data: BinaryFrame
    mime_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
