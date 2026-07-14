# okey_vision/providers.py
import re
import difflib
import logging
from typing import Dict, List, Optional, Union
import numpy as np
import requests
from okey_vision.types import FrameInput, Detection, BoundingBox
from okey_solver.types import Tile, TileColor

logger = logging.getLogger(__name__)

DEFAULT_COLOR_ALIASES = {
    "RED": TileColor.RED,
    "R": TileColor.RED,
    "KIRMIZI": TileColor.RED,
    "BLACK": TileColor.BLACK,
    "B": TileColor.BLACK,
    "SIYAH": TileColor.BLACK,
    "BLUE": TileColor.BLUE,
    "MAVI": TileColor.BLUE,
    "YELLOW": TileColor.YELLOW,
    "ORANGE": TileColor.YELLOW,
    "Y": TileColor.YELLOW,
    "SARI": TileColor.YELLOW,
}


def parse_default_tile(
    detection: Detection, index: int, color_aliases: Dict[str, TileColor]
) -> Tile:
    raw_label = detection.label
    if not raw_label:
        raise ValueError(
            f"Detection {detection.id or index} does not contain a class label."
        )

    normalized = raw_label.strip().upper()
    if "JOKER" in normalized:
        return Tile(id=detection.id, color=TileColor.JOKER, value=0)

    # Extract alphabetic (including Turkish characters) and digit-like characters
    letters = "".join(c for c in normalized if c.isalpha() or c in "ÇĞİÖŞÜ")
    digits_raw = "".join(c for c in normalized if c.isdigit() or c in "SOILZGB")

    # OCR Digit Confusions translation
    confusion_map = {
        'S': '5',
        'O': '0',
        'I': '1',
        'L': '1',
        'Z': '2',
        'G': '6',
        'B': '8'
    }
    digits_cleaned = "".join(confusion_map.get(c, c) for c in digits_raw)

    # Match color using fuzzy matching against aliases
    matched_color_key = None
    if letters in color_aliases:
        matched_color_key = letters
    else:
        # Try close matches using difflib
        matches = difflib.get_close_matches(letters, list(color_aliases.keys()), n=1, cutoff=0.5)
        if matches:
            matched_color_key = matches[0]

    if not matched_color_key:
        raise ValueError(
            f'Unsupported or unrecognized tile color/label "{raw_label}" on detection {detection.id or index}.'
        )

    color = color_aliases[matched_color_key]

    if not digits_cleaned.isdigit():
        raise ValueError(
            f'No valid numeric value found in label "{raw_label}" on detection {detection.id or index}.'
        )

    value = int(digits_cleaned)
    if value < 1 or value > 13:
        raise ValueError(
            f'Unsupported tile value "{value}" on detection {detection.id or index}.'
        )

    return Tile(id=detection.id, color=color, value=value)


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


class RoboflowProvider:
    """
    Uses the Roboflow API to detect tiles.
    """

    def __init__(
        self,
        api_key: str,
        model_id: str = "rummikub-5bldr",
        model_version: Union[int, str] = 1,
        label_map: Optional[Dict[str, TileColor]] = None,
    ):
        self.api_key = api_key
        self.model_id = model_id
        self.model_version = str(model_version)
        self.color_aliases = {**DEFAULT_COLOR_ALIASES, **(label_map or {})}
        self.base_url = "https://detect.roboflow.com"

    def _prepare_image_bytes(self, frame: FrameInput) -> bytes:
        import cv2

        if isinstance(frame.data, np.ndarray):
            _, buffer = cv2.imencode(".jpg", frame.data)
            return buffer.tobytes()
        elif isinstance(frame.data, (bytes, bytearray)):
            return bytes(frame.data)
        else:
            raise ValueError(
                "RoboflowProvider requires raw image bytes or numpy array."
            )

    def detect(self, frame: FrameInput) -> List[Detection]:
        import base64

        img_bytes = self._prepare_image_bytes(frame)
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")

        url = f"{self.base_url}/{self.model_id}/{self.model_version}"
        params = {"api_key": self.api_key}

        response = requests.post(
            url,
            params=params,
            data=img_b64,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if response.status_code != 200:
            raise ValueError(
                f"Roboflow API returned error {response.status_code}: {response.text}"
            )

        res_data = response.json()
        predictions = res_data.get("predictions", [])
        detections: List[Detection] = []

        for idx, pred in enumerate(predictions):
            cx = pred["x"]
            cy = pred["y"]
            width = pred["width"]
            height = pred["height"]
            conf = pred["confidence"]
            label = pred["class"]

            left = cx - width / 2
            top = cy - height / 2

            detections.append(
                Detection(
                    id=pred.get("prediction_id", f"rf-{idx}"),
                    bounds=BoundingBox(x=left, y=top, width=width, height=height),
                    confidence=conf,
                    label=label,
                    metadata=pred,
                )
            )

        return detections

    async def detect_async(self, frame: FrameInput) -> List[Detection]:
        import base64
        import httpx

        img_bytes = self._prepare_image_bytes(frame)
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")

        url = f"{self.base_url}/{self.model_id}/{self.model_version}"
        params = {"api_key": self.api_key}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                params=params,
                data=img_b64,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30.0,
            )

        if response.status_code != 200:
            raise ValueError(
                f"Roboflow API returned error {response.status_code}: {response.text}"
            )

        res_data = response.json()
        predictions = res_data.get("predictions", [])
        detections: List[Detection] = []

        for idx, pred in enumerate(predictions):
            cx = pred["x"]
            cy = pred["y"]
            width = pred["width"]
            height = pred["height"]
            conf = pred["confidence"]
            label = pred["class"]

            left = cx - width / 2
            top = cy - height / 2

            detections.append(
                Detection(
                    id=pred.get("prediction_id", f"rf-{idx}"),
                    bounds=BoundingBox(x=left, y=top, width=width, height=height),
                    confidence=conf,
                    label=label,
                    metadata=pred,
                )
            )

        return detections

    def classify(self, frame: FrameInput, detections: List[Detection]) -> List[Tile]:
        return [
            parse_default_tile(det, idx, self.color_aliases)
            for idx, det in enumerate(detections)
        ]


class RoboflowWorkflowProvider:
    """
    Uses the Roboflow Inference SDK Workflow API to detect tiles.
    """

    def __init__(
        self,
        api_key: str,
        workspace_name: str = "ata-dc7ry",
        workflow_id: str = "rummikub-vrummikub-p8akb-vr0ef-3-yolov8n-t1-logic",
        api_url: str = "https://serverless.roboflow.com",
        label_map: Optional[Dict[str, TileColor]] = None,
    ):
        from inference_sdk import InferenceHTTPClient

        self.client = InferenceHTTPClient(api_url=api_url, api_key=api_key)
        self.workspace_name = workspace_name
        self.workflow_id = workflow_id
        self.color_aliases = {**DEFAULT_COLOR_ALIASES, **(label_map or {})}

    def detect(self, frame: FrameInput) -> List[Detection]:
        import cv2

        if isinstance(frame.data, np.ndarray):
            image_input = frame.data
        elif isinstance(frame.data, (bytes, bytearray)):
            nparr = np.frombuffer(frame.data, np.uint8)
            image_input = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image_input is None:
                raise ValueError("Could not decode image bytes into numpy array.")
        else:
            raise ValueError(
                "RoboflowWorkflowProvider requires FrameInput.data to be numpy.ndarray or bytes."
            )

        try:
            result = self.client.run_workflow(
                workspace_name=self.workspace_name,
                workflow_id=self.workflow_id,
                images={"image": image_input},
                use_cache=True,
            )
        except Exception as e:
            logger.error(f"Error querying Roboflow Workflow API: {e}", exc_info=True)
            raise e

        if isinstance(result, list):
            if not result:
                return []
            result = result[0]

        predictions = []
        if isinstance(result, dict):
            # Attempt to extract predictions from common workflow output block names
            for key in ["predictions", "output", "detections"]:
                if key in result and isinstance(result[key], list):
                    predictions = result[key]
                    break
            if not predictions:
                # Fallback: check any list of dicts with bounding box properties
                for val in result.values():
                    if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
                        if "x" in val[0] and "y" in val[0] and "width" in val[0] and "confidence" in val[0]:
                            predictions = val
                            break
        else:
            logger.warning(f"Unexpected workflow result format: {type(result)}")

        detections: List[Detection] = []
        for idx, pred in enumerate(predictions):
            cx = pred["x"]
            cy = pred["y"]
            width = pred["width"]
            height = pred["height"]
            conf = pred.get("confidence", 1.0)
            label = pred.get("class", pred.get("label"))

            left = cx - width / 2
            top = cy - height / 2

            detections.append(
                Detection(
                    id=pred.get("prediction_id", f"rf-wf-{idx}"),
                    bounds=BoundingBox(x=left, y=top, width=width, height=height),
                    confidence=conf,
                    label=label,
                    metadata=pred,
                )
            )

        return detections

    async def detect_async(self, frame: FrameInput) -> List[Detection]:
        import asyncio

        return await asyncio.to_thread(self.detect, frame)

    def classify(self, frame: FrameInput, detections: List[Detection]) -> List[Tile]:
        return [
            parse_default_tile(det, idx, self.color_aliases)
            for idx, det in enumerate(detections)
        ]
