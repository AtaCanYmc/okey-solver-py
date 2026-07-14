import logging
from typing import Dict, List, Optional
import numpy as np
from okey_vision.types import FrameInput, Detection, BoundingBox
from okey_solver.types import Tile, TileColor
from okey_vision.errors import ProviderError
from okey_vision.providers.base import DEFAULT_COLOR_ALIASES, parse_default_tile

logger = logging.getLogger(__name__)


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
            raise ProviderError(
                f"Error querying Roboflow Workflow API: {e}",
                payload={"workspace_name": self.workspace_name, "workflow_id": self.workflow_id}
            ) from e

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
            parse_default_tile(det, idx, self.color_aliases)
            for idx, det in enumerate(detections)
        ]
