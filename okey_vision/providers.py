# okey_vision/providers.py
import re
from typing import Any, Dict, List, Optional, Union
import numpy as np
import requests
from okey_vision.types import FrameInput, Detection, BoundingBox
from okey_solver.types import Tile, TileColor

DEFAULT_COLOR_ALIASES = {
    'RED': TileColor.RED,
    'R': TileColor.RED,
    'KIRMIZI': TileColor.RED,
    'BLACK': TileColor.BLACK,
    'B': TileColor.BLACK,
    'SIYAH': TileColor.BLACK,
    'BLUE': TileColor.BLUE,
    'MAVI': TileColor.BLUE,
    'YELLOW': TileColor.YELLOW,
    'ORANGE': TileColor.YELLOW,
    'Y': TileColor.YELLOW,
    'SARI': TileColor.YELLOW,
}

def parse_default_tile(
    detection: Detection,
    index: int,
    color_aliases: Dict[str, TileColor]
) -> Tile:
    raw_label = detection.label
    if not raw_label:
        raise ValueError(f"Detection {detection.id or index} does not contain a class label.")

    normalized = raw_label.strip().upper()
    if 'JOKER' in normalized:
        return Tile(id=detection.id, color=TileColor.JOKER, value=0)

    # Regex search for color and number
    # Support "RED-5", "5-BLUE", "5R", "B12" etc.
    left_match = re.match(r'^([A-ZÇĞİÖŞÜ]+)[\s\-_]?(\d{1,2})$', normalized)
    parsed_color = None
    parsed_value = None

    if left_match:
        parsed_color = left_match.group(1)
        parsed_value = left_match.group(2)
    else:
        right_match = re.match(r'^(\d{1,2})[\s\-_]?([A-ZÇĞİÖŞÜ]+)$', normalized)
        if right_match:
            parsed_color = right_match.group(2)
            parsed_value = right_match.group(1)

    if not parsed_color or not parsed_value:
        # Fallback to general finding
        # e.g. look for digits
        digits = re.findall(r'\d+', normalized)
        letters = re.findall(r'[A-ZÇĞİÖŞÜ]+', normalized)
        if digits and letters:
            parsed_value = digits[0]
            parsed_color = letters[0]

    if not parsed_color or not parsed_value:
        raise ValueError(f"Unsupported tile label \"{raw_label}\" on detection {detection.id or index}.")

    color = color_aliases.get(parsed_color)
    if not color:
        raise ValueError(f"Unsupported tile color \"{parsed_color}\" on detection {detection.id or index}.")

    value = int(parsed_value)
    if value < 1 or value > 13:
        raise ValueError(f"Unsupported tile value \"{parsed_value}\" on detection {detection.id or index}.")

    return Tile(id=detection.id, color=color, value=value)

class LocalYoloProvider:
    """
    Directly runs local YOLO using the ultralytics package.
    """
    def __init__(
        self,
        model_path: str,
        label_map: Optional[Dict[str, TileColor]] = None,
        confidence_threshold: float = 0.25
    ):
        from ultralytics import YOLO
        self.model = YOLO(model_path)
        self.color_aliases = {**DEFAULT_COLOR_ALIASES, **(label_map or {})}
        self.confidence_threshold = confidence_threshold

    def detect(self, frame: FrameInput) -> List[Detection]:
        # Ultralytics accepts numpy arrays natively
        if not isinstance(frame.data, np.ndarray):
            raise ValueError("LocalYoloProvider requires FrameInput.data to be numpy.ndarray.")

        results = self.model.predict(frame.data, conf=self.confidence_threshold)
        detections: List[Detection] = []

        if not results:
            return detections

        result = results[0]
        boxes = result.boxes
        if boxes is not None:
            for idx, box in enumerate(boxes):
                xyxy = box.xyxy[0].tolist() # left, top, right, bottom
                conf = float(box.conf[0])
                cls_idx = int(box.cls[0])
                label = result.names[cls_idx]

                width = xyxy[2] - xyxy[0]
                height = xyxy[3] - xyxy[1]

                detections.append(Detection(
                    id=f"det-{idx}",
                    bounds=BoundingBox(x=xyxy[0], y=xyxy[1], width=width, height=height),
                    confidence=conf,
                    label=label,
                    metadata={"class_idx": cls_idx, "box_xyxy": xyxy}
                ))

        return detections

    def classify(self, frame: FrameInput, detections: List[Detection]) -> List[Tile]:
        return [parse_default_tile(det, idx, self.color_aliases) for idx, det in enumerate(detections)]

class RoboflowProvider:
    """
    Uses the Roboflow API to detect tiles.
    """
    def __init__(
        self,
        api_key: str,
        model_id: str = "rummikub-5bldr",
        model_version: Union[int, str] = 1,
        label_map: Optional[Dict[str, TileColor]] = None
    ):
        self.api_key = api_key
        self.model_id = model_id
        self.model_version = str(model_version)
        self.color_aliases = {**DEFAULT_COLOR_ALIASES, **(label_map or {})}
        self.base_url = "https://detect.roboflow.com"

    def detect(self, frame: FrameInput) -> List[Detection]:
        import cv2
        import base64

        # Needs to upload image to Roboflow
        if isinstance(frame.data, np.ndarray):
            _, buffer = cv2.imencode('.jpg', frame.data)
            img_bytes = buffer.tobytes()
        elif isinstance(frame.data, (bytes, bytearray)):
            img_bytes = bytes(frame.data)
        else:
            raise ValueError("RoboflowProvider requires raw image bytes or numpy array.")

        img_b64 = base64.b64encode(img_bytes).decode('utf-8')

        url = f"{self.base_url}/{self.model_id}/{self.model_version}"
        params = {
            "api_key": self.api_key
        }
        
        response = requests.post(
            url,
            params=params,
            data=img_b64,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if response.status_code != 200:
            raise ValueError(f"Roboflow API returned error {response.status_code}: {response.text}")

        res_data = response.json()
        predictions = res_data.get("predictions", [])
        detections: List[Detection] = []

        for idx, pred in enumerate(predictions):
            # Roboflow coordinates are center x, center y
            cx = pred["x"]
            cy = pred["y"]
            width = pred["width"]
            height = pred["height"]
            conf = pred["confidence"]
            label = pred["class"]

            left = cx - width / 2
            top = cy - height / 2

            detections.append(Detection(
                id=pred.get("prediction_id", f"rf-{idx}"),
                bounds=BoundingBox(x=left, y=top, width=width, height=height),
                confidence=conf,
                label=label,
                metadata=pred
            ))

        return detections

    def classify(self, frame: FrameInput, detections: List[Detection]) -> List[Tile]:
        return [parse_default_tile(det, idx, self.color_aliases) for idx, det in enumerate(detections)]
