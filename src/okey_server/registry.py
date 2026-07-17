# okey_server/registry.py
from typing import Dict, Any, Optional


class VisionProviderRegistry:
    def __init__(self) -> None:
        self._cache: Dict[str, Any] = {}

    def get_roboflow_workflow_provider(
        self,
        api_key: str,
        workspace_name: str,
        workflow_id: str,
        api_url: Optional[str] = None,
    ) -> Any:
        key = f"roboflow_wf:{api_key}:{workspace_name}:{workflow_id}:{api_url}"
        if key not in self._cache:
            from okey_vision.providers.roboflow_workflow import RoboflowWorkflowProvider

            self._cache[key] = RoboflowWorkflowProvider(
                api_key=api_key,
                workspace_name=workspace_name,
                workflow_id=workflow_id,
                api_url=api_url if api_url is not None else "https://serverless.roboflow.com",
            )
        return self._cache[key]
