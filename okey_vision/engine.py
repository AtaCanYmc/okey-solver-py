# okey_vision/engine.py
import time
from typing import Any, List, Optional, Protocol, Callable, Dict
from okey_vision.types import FrameInput, Detection
from okey_vision.frame_adapter import FrameAdapter, default_frame_adapters, adapt_to_frame_input
from okey_solver.types import Tile

class VisionObserver(Protocol):
    def on_event(self, event: Dict[str, Any]) -> None:
        ...

class VisionPipeline(Protocol):
    def preprocess(self, frame: FrameInput) -> FrameInput:
        ...
    def detect(self, frame: FrameInput) -> List[Detection]:
        ...
    def classify(self, frame: FrameInput, detections: List[Detection]) -> List[Tile]:
        ...

class DefaultVisionPipeline:
    def __init__(
        self,
        detect_fn: Callable[[FrameInput], List[Detection]],
        classify_fn: Callable[[FrameInput, List[Detection]], List[Tile]],
        preprocess_fn: Optional[Callable[[FrameInput], FrameInput]] = None
    ):
        self._detect = detect_fn
        self._classify = classify_fn
        self._preprocess = preprocess_fn or (lambda f: f)

    def preprocess(self, frame: FrameInput) -> FrameInput:
        return self._preprocess(frame)

    def detect(self, frame: FrameInput) -> List[Detection]:
        return self._detect(frame)

    def classify(self, frame: FrameInput, detections: List[Detection]) -> List[Tile]:
        return self._classify(frame, detections)

class VisionEngine:
    def __init__(
        self,
        pipeline: VisionPipeline,
        frame_adapters: Optional[List[FrameAdapter]] = None,
        observers: Optional[List[VisionObserver]] = None
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
                # Log observer error but don't crash pipeline
                print(f"Observer error: {e}")

    def process_frame(self, frame_input: Any) -> List[Tile]:
        frame = adapt_to_frame_input(frame_input, self.frame_adapters)
        if frame.data is None:
            raise ValueError("Frame data is required.")

        # Preprocess
        start_time = time.time()
        self.emit({"stage": "preprocess", "status": "start", "timestamp": start_time})
        try:
            prepared_frame = self.pipeline.preprocess(frame)
            self.emit({"stage": "preprocess", "status": "end", "timestamp": time.time(), "frame": prepared_frame})
        except Exception as e:
            self.emit({"stage": "preprocess", "status": "error", "timestamp": time.time(), "error": e})
            raise e

        # Detect
        start_time = time.time()
        self.emit({"stage": "detect", "status": "start", "timestamp": start_time})
        try:
            detections = self.pipeline.detect(prepared_frame)
            self.emit({"stage": "detect", "status": "end", "timestamp": time.time(), "detections": detections})
        except Exception as e:
            self.emit({"stage": "detect", "status": "error", "timestamp": time.time(), "error": e})
            raise e

        # Classify
        start_time = time.time()
        self.emit({"stage": "classify", "status": "start", "timestamp": start_time})
        try:
            tiles = self.pipeline.classify(prepared_frame, detections)
            self.emit({"stage": "classify", "status": "end", "timestamp": time.time(), "tiles": tiles})
        except Exception as e:
            self.emit({"stage": "classify", "status": "error", "timestamp": time.time(), "error": e})
            raise e

        return tiles
