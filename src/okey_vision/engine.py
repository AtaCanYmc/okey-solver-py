# okey_vision/engine.py
import time
import logging
import asyncio
from typing import Any, List, Optional, Protocol, Callable, Dict
from okey_vision.types import FrameInput, Detection
from okey_vision.frame_adapter import (
    FrameAdapter,
    default_frame_adapters,
    adapt_to_frame_input,
)
from okey_core.types import Tile

logger = logging.getLogger(__name__)


class VisionObserver(Protocol):
    def on_event(self, event: Dict[str, Any]) -> None: ...


class VisionPipeline(Protocol):
    def preprocess(self, frame: FrameInput) -> FrameInput: ...

    def detect(self, frame: FrameInput) -> List[Detection]: ...

    def classify(
            self, frame: FrameInput, detections: List[Detection]
    ) -> List[Tile]: ...


class AsyncVisionPipeline(Protocol):
    async def preprocess_async(self, frame: FrameInput) -> FrameInput: ...

    async def detect_async(self, frame: FrameInput) -> List[Detection]: ...

    async def classify_async(
            self, frame: FrameInput, detections: List[Detection]
    ) -> List[Tile]: ...


async def _run_async(fn: Callable, *args: Any, **kwargs: Any) -> Any:
    """Helper to run a function asynchronously, wrapping blocking functions in a thread pool."""
    if asyncio.iscoroutinefunction(fn):
        return await fn(*args, **kwargs)
    return await asyncio.to_thread(fn, *args, **kwargs)


class DefaultVisionPipeline:
    def __init__(
            self,
            detect_fn: Callable[[FrameInput], List[Detection]],
            classify_fn: Callable[[FrameInput, List[Detection]], List[Tile]],
            preprocess_fn: Optional[Callable[[FrameInput], FrameInput]] = None,
            detect_async_fn: Optional[Callable[[FrameInput], Any]] = None,
            classify_async_fn: Optional[Callable[[FrameInput, List[Detection]], Any]] = None,
            preprocess_async_fn: Optional[Callable[[FrameInput], Any]] = None,
    ):
        self._detect = detect_fn
        self._classify = classify_fn
        self._preprocess = preprocess_fn or (lambda f: f)

        self._detect_async = detect_async_fn
        self._classify_async = classify_async_fn
        self._preprocess_async = preprocess_async_fn

    def preprocess(self, frame: FrameInput) -> FrameInput:
        return self._preprocess(frame)

    def detect(self, frame: FrameInput) -> List[Detection]:
        return self._detect(frame)

    def classify(self, frame: FrameInput, detections: List[Detection]) -> List[Tile]:
        return self._classify(frame, detections)

    async def preprocess_async(self, frame: FrameInput) -> FrameInput:
        if self._preprocess_async:
            return await _run_async(self._preprocess_async, frame)
        return await _run_async(self._preprocess, frame)

    async def detect_async(self, frame: FrameInput) -> List[Detection]:
        if self._detect_async:
            return await _run_async(self._detect_async, frame)
        return await _run_async(self._detect, frame)

    async def classify_async(
            self, frame: FrameInput, detections: List[Detection]
    ) -> List[Tile]:
        if self._classify_async:
            return await _run_async(self._classify_async, frame, detections)
        return await _run_async(self._classify, frame, detections)


class VisionEngine:
    def __init__(
            self,
            pipeline: Any,  # Can be VisionPipeline or AsyncVisionPipeline
            frame_adapters: Optional[List[FrameAdapter]] = None,
            observers: Optional[List[VisionObserver]] = None,
    ):
        self.pipeline = pipeline
        self.frame_adapters = frame_adapters or default_frame_adapters()
        self.observers = observers or []

    def add_observer(self, observer: VisionObserver) -> None:
        self.observers.append(observer)

    def emit(self, event: Dict[str, Any]) -> None:
        for observer in self.observers:
            try:
                observer.on_event(event)
            except Exception as e:
                # Use logger instead of print
                logger.error(f"Observer error: {e}", exc_info=True)

    def process_frame(self, frame_input: Any) -> List[Tile]:
        frame = adapt_to_frame_input(frame_input, self.frame_adapters)
        if frame.data is None:
            raise ValueError("Frame data is required.")

        # Preprocess
        start_time = time.time()
        self.emit({"stage": "preprocess", "status": "start", "timestamp": start_time})
        try:
            prepared_frame = self.pipeline.preprocess(frame)
            self.emit(
                {
                    "stage": "preprocess",
                    "status": "end",
                    "timestamp": time.time(),
                    "frame": prepared_frame,
                }
            )
        except Exception as e:
            self.emit(
                {
                    "stage": "preprocess",
                    "status": "error",
                    "timestamp": time.time(),
                    "error": e,
                }
            )
            raise e

        # Detect
        start_time = time.time()
        self.emit({"stage": "detect", "status": "start", "timestamp": start_time})
        try:
            detections = self.pipeline.detect(prepared_frame)
            self.emit(
                {
                    "stage": "detect",
                    "status": "end",
                    "timestamp": time.time(),
                    "detections": detections,
                }
            )
        except Exception as e:
            self.emit(
                {
                    "stage": "detect",
                    "status": "error",
                    "timestamp": time.time(),
                    "error": e,
                }
            )
            raise e

        # Classify
        start_time = time.time()
        self.emit({"stage": "classify", "status": "start", "timestamp": start_time})
        try:
            tiles = self.pipeline.classify(prepared_frame, detections)
            self.emit(
                {
                    "stage": "classify",
                    "status": "end",
                    "timestamp": time.time(),
                    "tiles": tiles,
                }
            )
        except Exception as e:
            self.emit(
                {
                    "stage": "classify",
                    "status": "error",
                    "timestamp": time.time(),
                    "error": e,
                }
            )
            raise e

        return tiles

    async def process_frame_async(self, frame_input: Any) -> List[Tile]:
        frame = adapt_to_frame_input(frame_input, self.frame_adapters)
        if frame.data is None:
            raise ValueError("Frame data is required.")

        # Preprocess
        start_time = time.time()
        self.emit({"stage": "preprocess", "status": "start", "timestamp": start_time})
        try:
            if hasattr(self.pipeline, "preprocess_async"):
                prepared_frame = await self.pipeline.preprocess_async(frame)
            else:
                prepared_frame = await asyncio.to_thread(self.pipeline.preprocess, frame)
            self.emit(
                {
                    "stage": "preprocess",
                    "status": "end",
                    "timestamp": time.time(),
                    "frame": prepared_frame,
                }
            )
        except Exception as e:
            self.emit(
                {
                    "stage": "preprocess",
                    "status": "error",
                    "timestamp": time.time(),
                    "error": e,
                }
            )
            raise e

        # Detect
        start_time = time.time()
        self.emit({"stage": "detect", "status": "start", "timestamp": start_time})
        try:
            if hasattr(self.pipeline, "detect_async"):
                detections = await self.pipeline.detect_async(prepared_frame)
            else:
                detections = await asyncio.to_thread(self.pipeline.detect, prepared_frame)
            self.emit(
                {
                    "stage": "detect",
                    "status": "end",
                    "timestamp": time.time(),
                    "detections": detections,
                }
            )
        except Exception as e:
            self.emit(
                {
                    "stage": "detect",
                    "status": "error",
                    "timestamp": time.time(),
                    "error": e,
                }
            )
            raise e

        # Classify
        start_time = time.time()
        self.emit({"stage": "classify", "status": "start", "timestamp": start_time})
        try:
            if hasattr(self.pipeline, "classify_async"):
                tiles = await self.pipeline.classify_async(prepared_frame, detections)
            else:
                tiles = await asyncio.to_thread(self.pipeline.classify, prepared_frame, detections)
            self.emit(
                {
                    "stage": "classify",
                    "status": "end",
                    "timestamp": time.time(),
                    "tiles": tiles,
                }
            )
        except Exception as e:
            self.emit(
                {
                    "stage": "classify",
                    "status": "error",
                    "timestamp": time.time(),
                    "error": e,
                }
            )
            raise e

        return tiles
