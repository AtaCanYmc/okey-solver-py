from typing import Dict, List, Optional
import numpy as np
from okey_vision.types import FrameInput, Detection, BoundingBox
from okey_core.types import Tile, TileColor
from okey_vision.providers.base import DEFAULT_COLOR_ALIASES, parse_default_tile


class LocalYoloProvider:
    """
    Directly runs local YOLO using the ultralytics package.
    """

    def __init__(
        self,
        model_path: str,
        label_map: Optional[Dict[str, TileColor]] = None,
        confidence_threshold: float = 0.25,
    ):
        from ultralytics import YOLO

        self.model = YOLO(model_path)
        self.color_aliases = {**DEFAULT_COLOR_ALIASES, **(label_map or {})}
        self.confidence_threshold = confidence_threshold

    def preprocess(self, frame: FrameInput) -> FrameInput:
        return frame

    def detect(self, frame: FrameInput) -> List[Detection]:
        # Ultralytics accepts numpy arrays natively
        if not isinstance(frame.data, np.ndarray):
            raise ValueError(
                "LocalYoloProvider requires FrameInput.data to be numpy.ndarray."
            )

        results = self.model.predict(frame.data, conf=self.confidence_threshold)
        detections: List[Detection] = []

        if not results:
            return detections

        result = results[0]
        boxes = result.boxes
        if boxes is not None:
            for idx, box in enumerate(boxes):
                xyxy = box.xyxy[0].tolist()  # left, top, right, bottom
                conf = float(box.conf[0])
                cls_idx = int(box.cls[0])
                label = result.names[cls_idx]

                width = xyxy[2] - xyxy[0]
                height = xyxy[3] - xyxy[1]

                detections.append(
                    Detection(
                        id=f"det-{idx}",
                        bounds=BoundingBox(
                            x=xyxy[0], y=xyxy[1], width=width, height=height
                        ),
                        confidence=conf,
                        label=label,
                        metadata={"class_idx": cls_idx, "box_xyxy": xyxy},
                    )
                )

        return detections

    def classify(self, frame: FrameInput, detections: List[Detection]) -> List[Tile]:
        return [
            parse_default_tile(det, idx, self.color_aliases)
            for idx, det in enumerate(detections)
        ]
