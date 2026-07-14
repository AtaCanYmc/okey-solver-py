from typing import Dict, List, Optional, Union
import numpy as np
import requests
import httpx
from okey_vision.types import FrameInput, Detection, BoundingBox
from okey_core.types import Tile, TileColor
from okey_vision.errors import ProviderError
from okey_vision.providers.base import DEFAULT_COLOR_ALIASES, parse_default_tile


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

    def preprocess(self, frame: FrameInput) -> FrameInput:
        return frame

    def detect(self, frame: FrameInput) -> List[Detection]:
        import base64

        img_bytes = self._prepare_image_bytes(frame)
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")

        url = f"{self.base_url}/{self.model_id}/{self.model_version}"
        params = {"api_key": self.api_key}

        try:
            response = requests.post(
                url,
                params=params,
                data=img_b64,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10.0,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            status_code = getattr(getattr(e, "response", None), "status_code", None)
            response_text = getattr(getattr(e, "response", None), "text", "")
            raise ProviderError(
                f"Roboflow API connection failed: {e}",
                payload={"url": url, "status_code": status_code, "response_text": response_text}
            ) from e

        try:
            res_data = response.json()
        except ValueError as e:
            raise ProviderError(
                "Failed to parse Roboflow API response JSON.",
                payload={"response_text": response.text}
            ) from e

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

        img_bytes = self._prepare_image_bytes(frame)
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")

        url = f"{self.base_url}/{self.model_id}/{self.model_version}"
        params = {"api_key": self.api_key}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    params=params,
                    content=img_b64,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=10.0,
                )
                response.raise_for_status()
        except httpx.HTTPError as e:
            status_code = getattr(getattr(e, "response", None), "status_code", None)
            response_text = getattr(getattr(e, "response", None), "text", "")
            raise ProviderError(
                f"Roboflow API async connection failed: {e}",
                payload={"url": url, "status_code": status_code, "response_text": response_text}
            ) from e

        try:
            res_data = response.json()
        except ValueError as e:
            raise ProviderError(
                "Failed to parse Roboflow API response JSON.",
                payload={"response_text": response.text}
            ) from e

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
