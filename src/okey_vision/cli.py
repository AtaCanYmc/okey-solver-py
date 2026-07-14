# src/okey_vision/cli.py
import argparse
import sys
import os
from okey_orchestrator import VisionSolverEngine
from okey_vision.providers import LocalYoloProvider


def main():
    parser = argparse.ArgumentParser(
        description="Okey Vision CLI - Detect tiles in an image and solve the hand arrangement."
    )
    parser.add_argument(
        "--image",
        required=True,
        help="Path to the image file containing the okey board / tiles.",
    )
    parser.add_argument(
        "--model", required=True, help="Path to the local YOLO model (.pt) file."
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.25,
        help="Confidence threshold for YOLO model detections (default: 0.25).",
    )

    args = parser.parse_args()

    if not os.path.exists(args.image):
        print(f"Error: Image path '{args.image}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(args.model):
        print(f"Error: Model path '{args.model}' does not exist.", file=sys.stderr)
        sys.exit(1)

    print("=== Okey Vision CLI ===")
    print(f"Loading YOLO model from: {args.model}")

    # Initialize LocalYoloProvider as the detection/classification pipeline
    try:
        provider = LocalYoloProvider(
            model_path=args.model, confidence_threshold=args.confidence
        )
    except Exception as e:
        print(f"Error initializing local YOLO provider: {e}", file=sys.stderr)
        sys.exit(1)

    # Initialize orchestrator engine
    engine = VisionSolverEngine(pipeline=provider)

    print(f"Processing image frame: {args.image}...")

    # Analyze image path
    try:
        result = engine.analyze_frame(args.image)
    except Exception as e:
        print(f"Error during vision-solver execution: {e}", file=sys.stderr)
        sys.exit(1)

    print("\n[Vision Detections]")
    print(f"Detected Tiles ({len(result['tiles'])} total):")
    for t in result["tiles"]:
        print(f"  - Tile ID: {t.id} | {t.color.value} {t.value}")

    print("\n[Optimal Arrangement Results]")
    arrangement = result["arrangement"]
    print(f"Total Score: {arrangement.totalScore}")
    print(f"Melds Found: {len(arrangement.melds)}")
    for idx, meld in enumerate(arrangement.melds):
        tiles_str = ", ".join([f"{t.color.value}-{t.value}" for t in meld.tiles])
        print(
            f"  Meld #{idx + 1} ({meld.type.value}): [{tiles_str}] - score: {meld.score}"
        )

    if arrangement.remainingTiles:
        leftovers = ", ".join(
            [f"{t.color.value}-{t.value}" for t in arrangement.remainingTiles]
        )
        print(f"Remaining Tiles: [{leftovers}]")
    else:
        print("Remaining Tiles: [None]")


if __name__ == "__main__":
    main()
