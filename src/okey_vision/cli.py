# src/okey_vision/cli.py
import argparse
import sys
import os
from okey_orchestrator import VisionSolverEngine
from okey_vision.providers import RoboflowWorkflowProvider


def main():
    parser = argparse.ArgumentParser(
        description="Okey Vision CLI - Detect tiles in an image using Roboflow Workflows and solve the hand arrangement."
    )
    parser.add_argument(
        "--image",
        required=True,
        help="Path to the image file containing the okey board / tiles.",
    )
    parser.add_argument(
        "--api-key",
        required=True,
        help="Roboflow API Key (falls back to ROBOFLOW_API_KEY env var if empty).",
    )
    parser.add_argument(
        "--workspace",
        default="ata-dc7ry",
        help="Roboflow Workspace name (default: ata-dc7ry).",
    )
    parser.add_argument(
        "--workflow-id",
        default="okey-and-rummikub-vrummikub-p8akb-vr0ef-3-yolov8n-t1-logic",
        help="Roboflow Workflow ID.",
    )
    parser.add_argument(
        "--api-url",
        default="https://serverless.roboflow.com",
        help="Roboflow Workflow API Endpoint URL.",
    )

    args = parser.parse_args()

    if not os.path.exists(args.image):
        print(f"Error: Image path '{args.image}' does not exist.", file=sys.stderr)
        sys.exit(1)

    api_key = args.api_key or os.getenv("ROBOFLOW_API_KEY")
    if not api_key:
        print("Error: Roboflow API key is required. Pass --api-key or set ROBOFLOW_API_KEY env var.", file=sys.stderr)
        sys.exit(1)

    print("=== Okey Vision CLI ===")
    print(f"Loading Roboflow Workflow ID: {args.workflow_id}")

    # Initialize RoboflowWorkflowProvider as the detection/classification pipeline
    try:
        provider = RoboflowWorkflowProvider(
            api_key=api_key,
            workspace_name=args.workspace,
            workflow_id=args.workflow_id,
            api_url=args.api_url,
        )
    except Exception as e:
        print(f"Error initializing Roboflow Workflow provider: {e}", file=sys.stderr)
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
    print(f"Detected Tiles ({len(result.tiles)} total):")
    for t in result.tiles:
        print(f"  - Tile ID: {t.id} | {t.color.value} {t.value}")

    print("\n[Optimal Arrangement Results]")
    arrangement = result.arrangement
    if arrangement:
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
    else:
        print("No valid arrangement was found.")


if __name__ == "__main__":
    main()
