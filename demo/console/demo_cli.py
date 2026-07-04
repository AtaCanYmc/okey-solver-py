# demo/console/demo_cli.py
import os
import sys
import numpy as np

# Ensure correct module resolution paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from okey_solver import SolverEngine, Tile, TileColor, OkeyMeta
from okey_vision import VisionSolverEngine, DefaultVisionPipeline, Detection, BoundingBox

def run_solver_demo():
    print("=== OKEY SOLVER ENGINE DEMO ===")
    
    # Simulating a hand of tiles: RED 5-6-7 (Seri), BLUE 11-12-13 (Seri) and some leftovers
    tiles = [
        Tile(id="r5", color=TileColor.RED, value=5),
        Tile(id="r6", color=TileColor.RED, value=6),
        Tile(id="r7", color=TileColor.RED, value=7),
        Tile(id="b11", color=TileColor.BLUE, value=11),
        Tile(id="b12", color=TileColor.BLUE, value=12),
        Tile(id="b13", color=TileColor.BLUE, value=13),
        Tile(id="y10", color=TileColor.YELLOW, value=10),
    ]

    print(f"Input Hand: {[f'{t.color.value} {t.value}' for t in tiles]}")
    
    arrangement = SolverEngine.findBestArrangement(tiles)
    
    print("\n[Optimal Arrangement Results]")
    print(f"Total Arrangement Score: {arrangement.totalScore}")
    print(f"Valid Melds Found: {len(arrangement.melds)}")
    for i, meld in enumerate(arrangement.melds):
        tiles_str = ", ".join([f"{t.color.value}-{t.value}" for t in meld.tiles])
        print(f"  Meld #{i+1} ({meld.type.value}): [{tiles_str}] - score: {meld.score}")
    
    leftovers = ", ".join([f"{t.color.value}-{t.value}" for t in arrangement.remainingTiles])
    print(f"Leftover Tiles: [{leftovers}]")


def run_vision_solver_demo():
    print("\n=== OKEY VISION + SOLVER INTEGRATION DEMO ===")

    # Custom mock vision pipeline
    def mock_detect(frame):
        print(f"[Vision Pipeline] Detecting tiles in frame metadata size: {frame.width}x{frame.height}")
        # Simulated detections representing a Yellow 7, Blue 7, and Red 7 (Per candidate)
        return [
            Detection(id="d1", bounds=BoundingBox(x=5, y=5, width=15, height=20), confidence=0.99, label="YELLOW-7"),
            Detection(id="d2", bounds=BoundingBox(x=25, y=5, width=15, height=20), confidence=0.97, label="BLUE-7"),
            Detection(id="d3", bounds=BoundingBox(x=45, y=5, width=15, height=20), confidence=0.98, label="RED-7"),
        ]

    def mock_classify(frame, detections):
        print(f"[Vision Pipeline] Classifying {len(detections)} bounding boxes...")
        return [
            Tile(id="y7", color=TileColor.YELLOW, value=7),
            Tile(id="b7", color=TileColor.BLUE, value=7),
            Tile(id="r7", color=TileColor.RED, value=7),
        ]

    pipeline = DefaultVisionPipeline(
        detect_fn=mock_detect,
        classify_fn=mock_classify
    )

    # Instantiate the Orchestrator with our custom pipeline
    engine = VisionSolverEngine(pipeline)
    
    # Simulated camera frame (dummy 1280x720 RGB image)
    dummy_frame = np.zeros((720, 1280, 3), dtype=np.uint8)

    # Process
    result = engine.analyze_frame(dummy_frame)
    
    print("\n[Vision-Solver Results]")
    print(f"Detected Tiles: {[f'{t.color.value}-{t.value}' for t in result['tiles']]}")
    print(f"Total Solution Score: {result['arrangement'].totalScore}")
    for i, meld in enumerate(result["arrangement"].melds):
        tiles_str = ", ".join([f"{t.color.value}-{t.value}" for t in meld.tiles])
        print(f"  Meld #{i+1} ({meld.type.value}): [{tiles_str}]")

if __name__ == "__main__":
    run_solver_demo()
    run_vision_solver_demo()
