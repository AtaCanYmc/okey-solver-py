# okey-solver-py

Python package providing the core game logic engine (`okey_solver`) and camera frames processing pipeline (`okey_vision`) ported from TypeScript.

## Features
- **Backtracking Solver**: Optimal arrangement solver for Okey / Rummikub games.
- **Pairs/Double Play**: Find identical pairs.
- **Extensible Vision Engine**: Process frames natively with numpy arrays (OpenCV), PIL, base64 strings, bytes, and paths.
- **Provider Support**: Native local YOLO (`ultralytics`) and cloud Roboflow API implementations.

## Installation
```bash
pip install okey-solver-py
```

## Quick Start
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

For more documentation, look into `docs/` folder.
