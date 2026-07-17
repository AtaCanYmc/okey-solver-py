# okey_server/app.py
from contextlib import asynccontextmanager
import structlog

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from okey_server.settings import OkeyServerSettings
from okey_server.registry import VisionProviderRegistry
from okey_server.routers import router
from okey_server.logging_config import setup_logging
from okey_server.otel_config import setup_opentelemetry

# Set up structured logging
setup_logging()
logger = structlog.get_logger("okey_server")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Retrieve configurations from state settings
    settings: OkeyServerSettings = app.state.settings
    registry: VisionProviderRegistry = app.state.provider_registry

    # Warm up default provider
    if settings.rf_key:
        try:
            registry.get_roboflow_workflow_provider(
                api_key=settings.rf_key,
                workspace_name=settings.rf_workspace,
                workflow_id=settings.rf_workflow_id,
                api_url=settings.rf_api_url,
            )
            logger.info(
                "Pre-warmed default RoboflowWorkflowProvider",
                workspace=settings.rf_workspace,
                workflow_id=settings.rf_workflow_id,
            )
        except Exception as e:
            logger.exception(
                "Failed to pre-warm default Roboflow workflow provider", error=str(e)
            )

    yield


app = FastAPI(
    title="Okey Solver API",
    description="Microservice for solving Okey hand arrangements and detecting tiles from images.",
    version="0.3.0",
    lifespan=lifespan,
)

# Initialize OpenTelemetry instrumentation
setup_opentelemetry(app)

# Attach state structures
app.state.settings = OkeyServerSettings()
app.state.provider_registry = VisionProviderRegistry()


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler to capture all unhandled exceptions, log them structured,
    and return a clean generic 500 error to prevent internal info leakage.
    """
    from fastapi import HTTPException as FastAPIHTTPException
    from starlette.exceptions import HTTPException as StarletteHTTPException
    from okey_vision.errors import OkeyVisionError

    if isinstance(exc, (FastAPIHTTPException, StarletteHTTPException)):
        # Let FastAPI handle HTTPExceptions normally
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers,
        )

    if isinstance(exc, OkeyVisionError):
        # Known vision exceptions should return their detailed message under 500
        logger.exception("A known vision provider error occurred.", error=str(exc))
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)},
        )

    logger.exception("An unhandled exception occurred in the server.", error=str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )


@app.get("/health")
def health_check():
    """
    Service health check endpoint.
    """
    return {"status": "ok", "version": "0.3.0"}


# Register endpoints with /api/v1 prefix
app.include_router(router, prefix="/api/v1")
