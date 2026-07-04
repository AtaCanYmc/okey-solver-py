# Command Line Interface (CLI) Usage Guide

This package provides two main CLI tools for running hand evaluation and camera image object detection.

---

## 1. Okey Solver CLI (`okey-solve`)

Solves a hand of tiles and prints the optimal layout configuration.

### Usage
```bash
okey-solve --tiles COLOR:VALUE [COLOR:VALUE ...]
```

### Argument Parameters
- `--tiles`: List of tiles in hand in the format `COLOR:VALUE`. Supported colors: `RED`, `BLACK`, `BLUE`, `YELLOW`, `JOKER`.

### Example
```bash
okey-solve --tiles RED:5 RED:6 RED:7 BLUE:10 BLUE:11 BLUE:12 JOKER:0
```

---

## 2. Okey Vision CLI (`okey-vision`)

Processes an input camera frame or image file using a local YOLO model to find tiles and runs the solver on the output board state.

### Usage
```bash
okey-vision --image <image_path> --model <yolo_model_path> [--confidence <threshold>]
```

### Argument Parameters
- `--image`: Path to the image file containing the okey board/tiles.
- `--model`: Path to the local YOLO model (`.pt`) file.
- `--confidence`: Detection confidence threshold (default: `0.25`).

### Example
```bash
okey-vision --image ./board_layout.jpg --model ./models/best.pt --confidence 0.35
```
