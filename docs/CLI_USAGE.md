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

Processes an input camera frame or image file using the Roboflow Workflow API to detect tiles and runs the solver on the output board state.

### Usage
```bash
okey-vision --image <image_path> --api-key <roboflow_api_key> [--workspace <workspace_name>] [--workflow-id <workflow_id>] [--api-url <endpoint>]
```

### Argument Parameters
- `--image`: Path to the image file containing the okey board/tiles.
- `--api-key`: Roboflow API Key (falls back to `ROBOFLOW_API_KEY` env var if omitted).
- `--workspace`: Workspace name on Roboflow (default: `ata-dc7ry`).
- `--workflow-id`: Custom workflow ID configured in Roboflow.
- `--api-url`: Custom endpoint if running a local inference server (default: `https://serverless.roboflow.com`).

### Example
```bash
okey-vision --image ./board_layout.jpg --api-key YOUR_API_KEY
```
