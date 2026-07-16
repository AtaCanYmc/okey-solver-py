# okey_server/registry.py
from typing import Dict, Any, Optional


class VisionProviderRegistry:
    def __init__(self) -> None:
        self._cache: Dict[str, Any] = {}

    def get_local_yolo_provider(self, model_path: str) -> Any:
        key = f"local_yolo:{model_path}"
        if key not in self._cache:
            from okey_vision.providers import LocalYoloProvider

            self._cache[key] = LocalYoloProvider(model_path=model_path)
        return self._cache[key]

    def get_roboflow_provider(
        self,
        api_key: str,
        workspace_name: str,
        model_id: str,
        model_version: int,
    ) -> Any:
        key = f"roboflow:{api_key}:{workspace_name}:{model_id}:{model_version}"
        if key not in self._cache:
            from okey_vision.providers import RoboflowProvider

            self._cache[key] = RoboflowProvider(
                api_key=api_key,
                workspace_name=workspace_name,
                model_id=model_id,
                model_version=model_version,
            )
        return self._cache[key]

    def get_roboflow_workflow_provider(
        self,
        api_key: str,
        workspace_name: str,
        workflow_id: str,
        api_url: Optional[str] = None,
    ) -> Any:
        key = f"roboflow_wf:{api_key}:{workspace_name}:{workflow_id}:{api_url}"
        if key not in self._cache:
            from okey_vision.providers import RoboflowWorkflowProvider

            kwargs = {}
            if api_url:
                kwargs["api_url"] = api_url
            self._cache[key] = RoboflowWorkflowProvider(
                api_key=api_key,
                workspace_name=workspace_name,
                workflow_id=workflow_id,
                **kwargs,
            )
        return self._cache[key]
