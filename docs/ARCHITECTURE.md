# Architecture & Flow

The python codebase is structured into two main submodules:
1. `okey_solver`: Handles mathematical board state resolution.
2. `okey_vision`: Coordinates image preprocessing, model detection, and class labeling.

## Workflow

```mermaid
graph TD
    Input[Camera/File Image] --> Adapters[Frame Adapters]
    Adapters --> Pipeline[Vision Pipeline]
    
    subgraph okey_vision
        Pipeline --> Pre[Preprocess Stage]
        Pre --> Det[Detect Stage]
        Det --> Cls[Classify Stage]
    end
    
    Cls --> Tiles[Parsed Tile Objects]
    Tiles --> Solver[Solver Engine]
    
    subgraph okey_solver
        Solver --> Backtrack[Backtracking Solver]
        Solver --> Pairs[Pair Finder]
    end
    
    Backtrack --> Output[Game Solution/Score]
    Pairs --> Output
```

