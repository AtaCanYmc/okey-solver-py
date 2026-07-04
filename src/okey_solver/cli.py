# src/okey_solver/cli.py
import argparse
import sys
from okey_solver.types import Tile, TileColor
from okey_solver.solver import SolverEngine

def parse_tile_arg(tile_str: str) -> Tile:
    """Parses a tile in format 'COLOR:VALUE' e.g. 'RED:5' or 'JOKER:0'"""
    try:
        parts = tile_str.strip().split(":")
        if len(parts) != 2:
            raise ValueError()
        
        color_str, value_str = parts[0].upper(), parts[1]
        color = TileColor(color_str)
        value = int(value_str)
        
        tile_id = f"{color_str.lower()}_{value_str}"
        return Tile(id=tile_id, color=color, value=value)
    except Exception:
        raise argparse.ArgumentTypeError(
            f"Tile '{tile_str}' must be in the format COLOR:VALUE (e.g., RED:12 or JOKER:0)"
        )

def main():
    parser = argparse.ArgumentParser(
        description="Okey Solver CLI - Find the best arrangement of tiles."
    )
    parser.add_argument(
        "--tiles",
        nargs="+",
        required=True,
        type=parse_tile_arg,
        help="List of tiles in the hand in 'COLOR:VALUE' format. E.g., RED:5 BLUE:6 YELLOW:7"
    )
    
    args = parser.parse_args()
    
    print("=== Okey Solver CLI ===")
    print(f"Solving hand with {len(args.tiles)} tiles...\n")
    
    arrangement = SolverEngine.findBestArrangement(args.tiles)
    
    print(f"Total Arrangement Score: {arrangement.totalScore}")
    print(f"Melds Found: {len(arrangement.melds)}")
    for idx, meld in enumerate(arrangement.melds):
        tiles_str = ", ".join([f"{t.color.value}-{t.value}" for t in meld.tiles])
        print(f"  Meld #{idx+1} ({meld.type.value}): [{tiles_str}] - score: {meld.score}")
        
    if arrangement.remainingTiles:
        leftovers = ", ".join([f"{t.color.value}-{t.value}" for t in arrangement.remainingTiles])
        print(f"Remaining Tiles: [{leftovers}]")
    else:
        print("Remaining Tiles: [None]")

if __name__ == "__main__":
    main()
