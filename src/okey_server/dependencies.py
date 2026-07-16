# okey_server/dependencies.py
from typing import Optional, Any
from fastapi import Request, UploadFile, File, Form, HTTPException, Depends
from okey_solver import create_standard_okey_solver, SolverEngine


def get_solver_engine() -> SolverEngine:
    return create_standard_okey_solver()


async def validate_image_file(
    request: Request,
    file: UploadFile = File(...),
) -> bytes:
    """
    Validates that the uploaded file is an image, doesn't exceed the configured size limit,
    and returns its content as bytes.
    """
    settings = request.app.state.settings

    # Validate MIME type
    if file.content_type not in settings.allowed_mime_types:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid file type: {file.content_type}. "
                f"Supported types: {', '.join(settings.allowed_mime_types)}"
            ),
        )

    # Read in chunks to prevent OOM
    content = bytearray()
    chunk_size = 1024 * 1024  # 1MB
    bytes_read = 0

    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        bytes_read += len(chunk)
        if bytes_read > settings.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size allowed is {settings.max_file_size // (1024 * 1024)}MB.",
            )
        content.extend(chunk)

    return bytes(content)


def get_local_yolo_provider(
    request: Request,
    model_path: Optional[str] = Form(None),
) -> Any:
    """
    Dependency to get a LocalYoloProvider instance, using either the request-specific
    model path or the default configured model path.
    """
    settings = request.app.state.settings
    registry = request.app.state.provider_registry

    active_path = model_path or settings.model_path

    if not active_path:
        raise HTTPException(
            status_code=400,
            detail="Local YOLO vision provider not configured. Please supply model_path or set OKEY_MODEL_PATH.",
        )

    try:
        return registry.get_local_yolo_provider(active_path)
    except Exception as e:
        prefix = (
            "Failed to initialize request-scoped LocalYoloProvider: "
            if model_path
            else "Failed to initialize LocalYoloProvider: "
        )
        raise HTTPException(
            status_code=400,
            detail=f"{prefix}{str(e)}",
        )


def get_roboflow_provider(
    request: Request,
    api_key: Optional[str] = Form(None),
    workspace: Optional[str] = Form(None),
    model_id: Optional[str] = Form(None),
    model_version: Optional[int] = Form(None),
) -> Any:
    """
    Dependency to get a RoboflowProvider instance, using either request-specific
    parameters or fallback to configured defaults.
    """
    settings = request.app.state.settings
    registry = request.app.state.provider_registry

    active_api_key = api_key or settings.rf_key
    active_workspace = workspace or settings.rf_workspace
    active_model_id = model_id or settings.rf_model_id
    active_version = (
        model_version if model_version is not None else settings.rf_model_version
    )

    if not active_api_key:
        raise HTTPException(
            status_code=400,
            detail="Roboflow standard provider not configured. Please supply api_key or set OKEY_RF_KEY.",
        )

    try:
        return registry.get_roboflow_provider(
            api_key=active_api_key,
            workspace_name=active_workspace,
            model_id=active_model_id,
            model_version=active_version,
        )
    except Exception as e:
        prefix = (
            "Failed to initialize request-scoped RoboflowProvider: "
            if api_key
            else "Failed to initialize RoboflowProvider: "
        )
        raise HTTPException(
            status_code=400,
            detail=f"{prefix}{str(e)}",
        )


def get_roboflow_workflow_provider(
    request: Request,
    api_key: Optional[str] = Form(None),
    workspace: Optional[str] = Form(None),
    workflow_id: Optional[str] = Form(None),
    api_url: Optional[str] = Form(None),
) -> Any:
    """
    Dependency to get a RoboflowWorkflowProvider instance, using either request-specific
    parameters or fallback to configured defaults.
    """
    settings = request.app.state.settings
    registry = request.app.state.provider_registry

    active_api_key = api_key or settings.rf_key
    active_workspace = workspace or settings.rf_workspace
    active_workflow = (
        workflow_id or "okey-and-rummikub-vrummikub-p8akb-vr0ef-3-yolov8n-t1-logic"
    )
    active_api_url = api_url or settings.rf_api_url

    if not active_api_key:
        raise HTTPException(
            status_code=400,
            detail="Roboflow workflow provider not configured. Please supply api_key or set OKEY_RF_KEY.",
        )

    try:
        return registry.get_roboflow_workflow_provider(
            api_key=active_api_key,
            workspace_name=active_workspace,
            workflow_id=active_workflow,
            api_url=active_api_url,
        )
    except Exception as e:
        prefix = (
            "Failed to initialize request-scoped RoboflowWorkflowProvider: "
            if api_key
            else "Failed to initialize RoboflowWorkflowProvider: "
        )
        raise HTTPException(
            status_code=400,
            detail=f"{prefix}{str(e)}",
        )
