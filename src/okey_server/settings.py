# okey_server/settings.py
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict


class OkeyServerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="OKEY_",
        case_sensitive=False,
        extra="ignore"
    )

    model_path: Optional[str] = None
    rf_key: Optional[str] = None
    rf_workspace: str = "ata-dc7ry"
    rf_model_id: str = "okey-rummikub"
    rf_model_version: int = 1
    rf_api_url: Optional[str] = None

    # Security controls
    max_file_size: int = 10 * 1024 * 1024  # 10 MB limit
    allowed_mime_types: List[str] = ["image/jpeg", "image/png", "image/webp"]
