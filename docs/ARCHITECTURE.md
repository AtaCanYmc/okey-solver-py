# Architecture & Flow

The python codebase is structured into two main submodules:
1. `okey_solver`: Handles mathematical board state resolution.
2. `okey_vision`: Coordinates image preprocessing, model detection, and class labeling.

## Workflow

```mermaid
graph TD
    Client[Client / CLI] -->|HTTP / Frame| Server[okey_server: FastAPI app]
    Server -->|Content| Orchestrator[okey_orchestrator: VisionSolverEngine]
    
    subgraph Decoupled Layers
        Orchestrator -->|Image Frame| Vision[okey_vision: Roboflow Workflow]
        Vision -->|Label Parsing Strategy| Parser[FuzzyLabelParser / CustomParser]
        Vision -->|Parsed Tiles| Core[okey_core: Shared Types]
        Orchestrator -->|Resolved Tiles| Solver[okey_solver: SolverEngine]
        Solver -->|DTO Mapping| DTO[dto: LightTile/LightMeld]
        DTO -->|Search Strategies| Strategy[Backtracking / Greedy Strategy]
    end
    
    Strategy -->|Meld Solution| Orchestrator
    Orchestrator -->|OrchestratorResult| Server
    Server -->|JSON Response| Client
```

## Model Provider

The `okey_vision` submodule uses the modern Roboflow Inference SDK Workflow API to query custom detection workflows on serverless infrastructure.

### `RoboflowWorkflowProvider`
Queries multi-stage visual logic workflows from Roboflow and parses the predictions into core tile models.
- **Dependencies**: `inference-sdk`.
- **Use Case**: Advanced visual logic workflows, hosting/scaling models in the cloud.



