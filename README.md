# okey-solver-py

Python library for solving Okey & Rummikub tile arrangements and processing board layouts.

---

## Features
- **Backtracking Solver**: Optimal arrangement solver for Okey / Rummikub games.
- **Pairs/Double Play**: Find identical pairs.
- **Extensible Vision Engine**: Process frames natively with numpy arrays (OpenCV), PIL, base64 strings, bytes, and paths.
- **Provider Support**: Native local YOLO (`ultralytics`) and cloud Roboflow API implementations.

---

## Installation
```bash
pip install okey-solver-py
```

---

## Quick Start

### Basic Solver Arrangement
```python
from okey_solver import SolverEngine, Tile, TileColor

tiles = [
    Tile(id="r5", color=TileColor.RED, value=5),
    Tile(id="r6", color=TileColor.RED, value=6),
    Tile(id="r7", color=TileColor.RED, value=7),
]
result = SolverEngine.findBestArrangement(tiles)
print(result.totalScore)
```

### With Roboflow Provider
```python
from okey_vision import RoboflowProvider, VisionSolverEngine

provider = RoboflowProvider(
    api_key="your_api_key",
    model_id="rummikub-5bldr",
    model_version=1
)

engine = VisionSolverEngine(provider)
result = engine.analyze_frame("image_path.jpg")
print(result["tiles"])
print(result["arrangement"])
```

### With Local YOLO Model
```python
from okey_vision import LocalYoloProvider, VisionSolverEngine

provider = LocalYoloProvider(
    model_path="./models/yolov8_best.pt"
)

engine = VisionSolverEngine(provider)
result = engine.analyze_frame("board_layout.jpg")
print(result["arrangement"])
```

---

## Extended Documentation

For details on architecture, rules, and APIs:
- 🏗 **[Architecture & Flow](docs/ARCHITECTURE.md)** - Details on pipeline stages, frame adapters, and observers.
- 📜 **[Game Rules Reference](docs/ALGORITHM_RULES.md)** - Okey rules, 12-13-1 circular runs, joker and false okey logic.
