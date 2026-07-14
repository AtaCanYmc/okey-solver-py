# okey-solver-py

An enterprise-ready Python library for solving Okey & Rummikub board states, arranging hands, and processing layouts with computer vision pipelines.

[![tests](https://github.com/AtaCanYmc/okey-solver-py/actions/workflows/ci.yml/badge.svg)](./actions)
[![Python support](https://img.shields.io/badge/Python-3.10+-blue.svg)](#-requirements)
[![License](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](./LICENSE)

---

## 🏗 Modular Package Architecture

The codebase is split into fully decoupled, high-performance packages under the `src/` directory:

1. **`okey_core`**: Holds shared domain types (`Tile`, `Meld`, `Arrangement`, `OrchestratorResult`) and exceptions. Completely independent.
2. **`okey_solver`**: Stateless mathematical engines to calculate optimal run/group melds and identical pairs. Uses slot-based DTO mapping (`LightTile`, `LightMeld`) to bypass Pydantic model loop overhead.
3. **`okey_vision`**: Translates frames (numpy, PIL, bytes, base64) into tile predictions. Supports local YOLO or cloud Roboflow models. Decoupled from solver logic via an injectable `LabelParserStrategy`.
4. **`okey_orchestrator`**: Orchestrates pipelines by feeding vision outputs into the mathematical solver.
5. **`okey_server`**: A microservice framework delivering endpoints for vision processing and hand arrangement.

---

## 📦 Installation

To install the core mathematical solver:
```bash
pip install okey-solver-py
```

To install computer vision extras:
```bash
pip install okey-solver-py[vision]
```

To install FastAPI server extras:
```bash
pip install okey-solver-py[server]
```

To install everything for development:
```bash
pip install okey-solver-py[vision,server]
```

---

## 💻 CLI Commands

The package exposes the following CLI commands:

- **`okey-solve`**: Solves hand arrangements from lists of tile arguments.
- **`okey-vision`**: Runs object detection predictions on an image layout.
- **`okey-serve`**: Launches the FastAPI REST microservice API.
- **`okey-demo`**: Launches the local terminal solver demo application.

---

## 🚀 Quick Start

### 1. Basic Solver Arrangement
```python
from okey_solver import create_standard_okey_solver, Tile, TileColor

# Instantiates a stateless, independent engine
solver = create_standard_okey_solver(strategy="backtracking")

tiles = [
    Tile(id="r5", color=TileColor.RED, value=5),
    Tile(id="r6", color=TileColor.RED, value=6),
    Tile(id="r7", color=TileColor.RED, value=7),
]
result = solver.find_best_arrangement(tiles)
print(f"Total Score: {result.totalScore}")
```

### 2. End-to-End Orchestration (Vision + Solver)
```python
from okey_vision import LocalYoloProvider
from okey_orchestrator import VisionSolverEngine

# 1. Initialize vision model provider
provider = LocalYoloProvider(model_path="./models/yolov8_best.pt")

# 2. Bind pipeline inside the orchestrator
engine = VisionSolverEngine(pipeline=provider)

# 3. Analyze layout image and solve
result = engine.analyze_frame("board_layout.jpg")
print("Detected Tiles:", result.tiles)
print("Optimal Score:", result.arrangement.totalScore)
```

---

## 🌐 FastAPI Microservice (API Server)

Deploy this package directly to cloud infrastructure to process requests via HTTP:

### Start the Microservice
```bash
# Set environment variables for YOLO or Roboflow
export YOLO_MODEL_PATH="./models/yolov8_best.pt"

# Start the uvicorn instance on port 8000
okey-serve --port 8000
```

### Endpoints
- **`POST /solver/arrange`**: Accepts a JSON list of tile parameters and returns arranged melds.
- **`POST /vision/solve`**: Accepts an uploaded board image, detects the layout, and returns solved arrangements.
- **Interactive Swagger Docs**: Visit [http://localhost:8000/docs](http://localhost:8000/docs) to test requests in the browser.

---

## 📖 Extended Documentation

- 🏗 **[Architecture & Flow Reference](docs/ARCHITECTURE.md)** - Visual flow pipelines, observers, and providers.
- 📜 **[Game Rules Reference](docs/ALGORITHM_RULES.md)** - Explanations of run configurations, circular sequences, and Joker/False Okey rules.
- 💻 **[CLI Usage Guide](docs/CLI_USAGE.md)** - Terminal parameters for running predictions and solvers.
- 🤝 **[Contributing Guide](CONTRIBUTING.md)** - Guidelines for configuring local poetry environments and running Ruff/Mypy checks.
