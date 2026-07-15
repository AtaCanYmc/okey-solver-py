# okey_server/state.py
from typing import Optional, Any

# Globally shared default vision pipeline, populated during application lifespan
vision_pipeline: Optional[Any] = None
