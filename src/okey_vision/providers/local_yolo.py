# okey_vision/providers/local_yolo.py
from typing import Dict, List, Optional
import numpy as np
from okey_vision.types import FrameInput, Detection, BoundingBox
from okey_core.types import Tile, TileColor
from okey_vision.providers.base import DEFAULT_COLOR_ALIASES, LabelParserStrategy, FuzzyLabelParser


class LocalYoloProvider:
    """
    Directly runs local YOLO using the ultralytics package.
    """

    def __init__(
        self,
        model_path: str,
        label_map: Optional[Dict[str, TileColor]] = None,
        confidence_threshold: float = 0.25,
        parser: Optional[LabelParserStrategy] = None,
    ):
        from ultralytics import YOLO

        self.model = YOLO(model_path)
        self.color_aliases = {**DEFAULT_COLOR_ALIASES, **(label_map or {})}
        self.confidence_threshold = confidence_threshold
        self.parser = parser or FuzzyLabelParser()

    def preprocess(self, frame: FrameInput) -> FrameInput:
        return frame

    def detect(self, frame: FrameInput) -> List[Detection]:
        if not isinstance(frame.data, np.ndarray):
            raise ValueError(
                "LocalYoloProvider requires FrameInput.data to be numpy.ndarray."
            )

        # Run inference using the YOLO model instance
        results = self.model.predict(
            source=frame.data, conf=self.confidence_threshold, verbose=False
        )

        detections: List[Detection] = []
        if not results:
            return detections

        result = results[0]
        boxes = result.boxes

        for idx, box in enumerate(boxes):
            cls_idx = int(box.cls[0])
            label = self.model.names[cls_idx]
            conf = float(box.conf[0])

            xyxy = box.xyxy[0].tolist()
            left = xyxy[0]
            top = xyxy[1]
            width = xyxy[2] - left
            height = xyxy[3] - top

            detections.append(
                Detection(
                    id=f"yolo-{idx}",
                    bounds=BoundingBox(x=left, y=top, width=width, height=height),
                    confidence=conf,
                    label=label,
                    metadata={"class_index": cls_idx},
                )
            )

        return detections

    async def detect_async(self, frame: FrameInput) -> List[Detection]:
        import asyncio

        return await asyncio.to_thread(self.detect, frame)

    def classify(self, frame: FrameInput, detections: List[Detection]) -> List[Tile]:
        return [
            self.parser.parse_tile(det, idx, self.color_aliases)
            for idx, det in enumerate(detections)
        ]
