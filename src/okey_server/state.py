# okey_server/state.py
from typing import Optional, Any

# Globally shared default vision pipeline, populated during application lifespan
vision_pipeline: Optional[Any] = None

# Configuration parameters passed from outside (CLI, function calls, tests, etc.)
model_path: Optional[str] = None
rf_key: Optional[str] = None
rf_workspace: str = "ata-dc7ry"
rf_model_id: str = "okey-rummikub"
rf_model_version: int = 1
rf_api_url: Optional[str] = None
