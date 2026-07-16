import logging
from typing import Dict, List, Optional
import numpy as np
from okey_vision.types import FrameInput, Detection, BoundingBox
from okey_core.types import Tile, TileColor
from okey_vision.errors import ProviderError
from okey_vision.providers.base import DEFAULT_COLOR_ALIASES, LabelParserStrategy, FuzzyLabelParser

logger = logging.getLogger(__name__)


class RoboflowWorkflowProvider:
    """
    Uses the Roboflow Inference SDK Workflow API to detect tiles.
    """

    def __init__(
        self,
        api_key: str,
        workspace_name: str = "ata-dc7ry",
        workflow_id: str = "okey-and-rummikub-vrummikub-p8akb-vr0ef-3-yolov8n-t1-logic",
        api_url: str = "https://serverless.roboflow.com",
        label_map: Optional[Dict[str, TileColor]] = None,
        parser: Optional[LabelParserStrategy] = None,
    ):
        from inference_sdk import InferenceHTTPClient

        self.client = InferenceHTTPClient(api_url=api_url, api_key=api_key)
        self.workspace_name = workspace_name
        self.workflow_id = workflow_id
        self.color_aliases = {**DEFAULT_COLOR_ALIASES, **(label_map or {})}
        self.parser = parser or FuzzyLabelParser()

    def preprocess(self, frame: FrameInput) -> FrameInput:
        return frame

    def detect(self, frame: FrameInput) -> List[Detection]:
        import cv2

        image_input: np.ndarray
        if isinstance(frame.data, np.ndarray):
            image_input = frame.data
        elif isinstance(frame.data, (bytes, bytearray)):
            nparr = np.frombuffer(frame.data, np.uint8)
            decoded = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if decoded is None:
                raise ValueError("Could not decode image bytes into numpy array.")
            image_input = decoded
        else:
            raise ValueError(
                "RoboflowWorkflowProvider requires FrameInput.data to be numpy.ndarray or bytes."
            )

        try:
            result = self.client.run_workflow(
                workspace_name=self.workspace_name,
                workflow_id=self.workflow_id,
                images={"images": image_input},
                use_cache=True,
            )
        except Exception as e:
            logger.error(f"Error querying Roboflow Workflow API: {e}", exc_info=True)
            raise ProviderError(
                f"Error querying Roboflow Workflow API: {e}",
                payload={"workspace_name": self.workspace_name, "workflow_id": self.workflow_id}
            ) from e

        def find_predictions_list(data) -> Optional[List[dict]]:
            if isinstance(data, list):
                if len(data) > 0 and isinstance(data[0], dict):
                    first = data[0]
                    # Bounding box structures typically have at least x, y, width, height
                    if "x" in first and "y" in first and "width" in first and "height" in first:
                        return data
                for item in data:
                    found = find_predictions_list(item)
                    if found is not None:
                        return found
            elif isinstance(data, dict):
                # Check preferred keys first
                for key in ["predictions", "output", "detections", "predictions_list"]:
                    if key in data:
                        val = data[key]
                        if isinstance(val, list):
                            found = find_predictions_list(val)
                            if found is not None:
                                return found
                        elif isinstance(val, dict):
                            found = find_predictions_list(val)
                            if found is not None:
                                return found
                # Recurse other keys
                for val in data.values():
                    found = find_predictions_list(val)
                    if found is not None:
                        return found
            return None

        if isinstance(result, list):
            if not result:
                return []
            result = result[0]

        predictions = []
        if isinstance(result, dict):
            predictions = find_predictions_list(result) or []
            if not predictions and result:
                raise ProviderError(
                    "Unexpected format: could not extract predictions list from workflow result dictionary.",
                    payload={"result": result}
                )
        else:
            raise ProviderError(
                f"Unexpected workflow result type: expected dict or list, got {type(result)}",
                payload={"result": result}
            )

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
            self.parser.parse_tile(det, idx, self.color_aliases)
            for idx, det in enumerate(detections)
        ]
