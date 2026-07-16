# okey_vision/providers/roboflow.py
import cv2
import numpy as np
from typing import Dict, List, Optional, Union
from roboflow import Roboflow
from okey_vision.types import FrameInput, Detection, BoundingBox
from okey_core.types import Tile, TileColor
from okey_vision.errors import ProviderError
from okey_vision.providers.base import (
    DEFAULT_COLOR_ALIASES,
    LabelParserStrategy,
    FuzzyLabelParser,
)


class RoboflowProvider:
    """
    Uses the official Roboflow Python SDK to detect tiles.
    """

    def __init__(
        self,
        api_key: str,
        model_id: str = "rummikub-p8akb-vr0ef-3-yolov8n-t1",
        workspace_name="ata-dc7ry",
        model_version: Union[int, str] = 1,
        label_map: Optional[Dict[str, TileColor]] = None,
        parser: Optional[LabelParserStrategy] = None,
        api_url: Optional[str] = None,
    ):
        self.api_key = api_key
        # Split workspace name if embedded in model_id (e.g. "workspace/project")
        if "/" in model_id:
            parts = model_id.split("/")
            if len(parts) == 2:
                self.workspace = parts[0]
                self.project = parts[1]
            else:
                self.workspace = workspace_name
                self.project = model_id
        else:
            self.workspace = workspace_name
            self.project = model_id

        self.model_version = str(model_version)
        self.color_aliases = {**DEFAULT_COLOR_ALIASES, **(label_map or {})}
        self.api_url = api_url
        self.parser = parser or FuzzyLabelParser()
        self._model = None

    def _get_model(self):
        if self._model is None:
            try:
                # Initialize the Roboflow client and load workspace/project/version/model
                rf = Roboflow(api_key=self.api_key)
                # If custom api_url is provided, try setting it on roboflow config
                if self.api_url:
                    import roboflow.config as rf_config

                    rf_config.API_URL = self.api_url

                project_client = rf.workspace(self.workspace).project(self.project)
                self._model = project_client.version(int(self.model_version)).model
            except Exception as e:
                raise ProviderError(
                    f"Roboflow API client initialization failed: {e}"
                ) from e
        return self._model

    def _prepare_image(self, frame: FrameInput) -> np.ndarray:
        if isinstance(frame.data, np.ndarray):
            return frame.data
        elif isinstance(frame.data, (bytes, bytearray)):
            nparr = np.frombuffer(frame.data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Could not decode image bytes into numpy array.")
            return img
        else:
            raise ValueError("RoboflowProvider requires numpy array or image bytes.")

    def detect(self, frame: FrameInput) -> List[Detection]:
        image = self._prepare_image(frame)

        try:
            model = self._get_model()
            # Predict using the loaded model
            res_data = model.predict(image, confidence=40, overlap=30).json()
            self.last_raw_response = res_data
        except Exception as e:
            raise ProviderError(f"Roboflow API connection failed: {e}") from e

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
        import asyncio

        try:
            return await asyncio.to_thread(self.detect, frame)
        except Exception as e:
            raise ProviderError(f"Roboflow API async connection failed: {e}") from e

    def preprocess(self, frame: FrameInput) -> FrameInput:
        return frame

    def classify(self, frame: FrameInput, detections: List[Detection]) -> List[Tile]:
        return [
            self.parser.parse_tile(det, idx, self.color_aliases)
            for idx, det in enumerate(detections)
        ]
