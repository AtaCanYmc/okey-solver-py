<div align="center">
  <img src=".github/screenshots/okey-solver-logo.png" alt="Okey Solver Py Logo" width="200" />
  <h1>okey-solver-py</h1>
  <p>Python library for solving Okey & Rummikub tile arrangements and processing board layouts.</p>

  [![PyPI version](https://img.shields.io/pypi/v/okey-solver-py.svg)](https://pypi.org/project/okey-solver-py/)
  [![tests](https://img.shields.io/badge/tests-11%2F11%20passing-brightgreen)](./tests)
  [![Python support](https://img.shields.io/badge/Python-3.10+-blue.svg)](#-requirements)
  [![License](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](./LICENSE)
</div>

---

## Features
- **Backtracking Solver**: Optimal arrangement solver for Okey / Rummikub games.
- **Pairs/Double Play**: Find identical pairs.
- **Extensible Vision Engine**: Process frames natively with numpy arrays (OpenCV), PIL, base64 strings, bytes, and paths.
- **Provider Support**: Native local YOLO (`ultralytics`), cloud Roboflow API (`RoboflowProvider`), and Roboflow Inference SDK Workflows (`RoboflowWorkflowProvider`).

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

### With Roboflow Workflow Provider
```python
from okey_vision import RoboflowWorkflowProvider, VisionSolverEngine

provider = RoboflowWorkflowProvider(
    api_key="your_api_key",
    workspace_name="ata-dc7ry",
    workflow_id="rummikub-vrummikub-p8akb-vr0ef-3-yolov8n-t1-logic"
)

engine = VisionSolverEngine(provider)
result = engine.analyze_frame("image_path.jpg")
print(result.tiles)
print(result.arrangement)
```

### With Roboflow Object Detection Provider
```python
from okey_vision import RoboflowProvider
from okey_orchestrator import VisionSolverEngine

provider = RoboflowProvider(
    api_key="your_api_key",
    model_id="rummikub-5bldr",
    model_version=1
)

engine = VisionSolverEngine(provider)
result = engine.analyze_frame("image_path.jpg")
print(result.tiles)
print(result.arrangement)
```

### With Local YOLO Model
```python
from okey_vision import LocalYoloProvider
from okey_orchestrator import VisionSolverEngine

provider = LocalYoloProvider(
    model_path="./models/yolov8_best.pt"
)

engine = VisionSolverEngine(provider)
result = engine.analyze_frame("board_layout.jpg")
print(result.arrangement)
```

---

## FastAPI Microservice (API Server)

For developers deploying this package to cloud environments, `okey-solver-py` ships with an embedded FastAPI microservice.

### 1. Install dependencies
```bash
pip install okey-solver-py[server]
```

### 2. Start the Server
```bash
# Start on port 8000
okey-serve --port 8000
```

### 3. Interactive API Docs (Swagger UI)
Once running, navigate to [http://localhost:8000/docs](http://localhost:8000/docs) in your browser. This interactive interface allows you to view detailed API schemas and test endpoints (such as `POST /solver/arrange` and `POST /vision/solve`) directly.

---

## Extended Documentation

For details on architecture, rules, and APIs:
- 🏗 **[Architecture & Flow](docs/ARCHITECTURE.md)** - Details on pipeline stages, frame adapters, and observers.
- 📜 **[Game Rules Reference](docs/ALGORITHM_RULES.md)** - Okey rules, 12-13-1 circular runs, joker and false okey logic.
- 💻 **[CLI Usage Guide](docs/CLI_USAGE.md)** - Guide to running `okey-solve` and `okey-vision` terminal applications.
- 🤖 **[Telegram Bot Demo](demo/telegram/bot.py)** - Telegram Bot server example integrating image detection and layout solving.
