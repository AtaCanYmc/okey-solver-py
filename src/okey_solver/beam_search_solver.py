# okey_solver/beam_search_solver.py
from typing import List, Tuple
from okey_core.types import Tile, Meld, Arrangement
from okey_solver.dto import LightTile, LightMeld


class BeamSearchSolver:
    """
    Finds a non-overlapping, high-scoring hand arrangement using Beam Search.
    Faster than DFS/Backtracking and searches for more optimal arrangements than Greedy.
    """

    def __init__(self, beam_width: int = 25):
        self.beam_width = beam_width

    def solve(
        self, resolved_tiles: List[Tile], all_possible_melds: List[Meld]
    ) -> Arrangement:
        if not resolved_tiles:
            return Arrangement(melds=[], remainingTiles=[], totalScore=0)

        pydantic_tile_map = {t.id: t for t in resolved_tiles}

        # DTO Mapping
        light_tiles = [
            LightTile(tile.id, tile.color, tile.value) for tile in resolved_tiles
        ]
        light_melds: List[LightMeld] = []
        for m in all_possible_melds:
            m_tiles = [LightTile(tile.id, tile.color, tile.value) for tile in m.tiles]
            light_melds.append(LightMeld(m.type, m_tiles, m.score))

        # Sort candidate melds by score descending to focus on highest potential first
        light_melds.sort(key=lambda m: (m.score, -len(m.tiles)), reverse=True)

        tile_to_bit = {tile.id: idx for idx, tile in enumerate(light_tiles)}
        num_tiles = len(light_tiles)
        initial_mask = (1 << num_tiles) - 1

        # State representation in the beam: (score, mask, list_of_melds)
        # We start with the empty arrangement state
        beam: List[Tuple[int, int, List[LightMeld]]] = [(0, initial_mask, [])]

        for meld in light_melds:
            next_beam = []
            seen_masks = set()

            # Precalculate meld mask and whether it is valid
            meld_mask = 0
            meld_valid = True
            for tile in meld.tiles:
                if tile.id in tile_to_bit:
                    meld_mask |= 1 << tile_to_bit[tile.id]
                else:
                    meld_valid = False
                    break

            if not meld_valid:
                continue

            for score, mask, chosen in beam:
                # Option 1: Exclude the meld (carry over existing state)
                if mask not in seen_masks:
                    seen_masks.add(mask)
                    next_beam.append((score, mask, chosen))

                # Option 2: Include the meld (if no overlap)
                if (mask & meld_mask) == meld_mask:
                    new_mask = mask ^ meld_mask
                    new_score = score + meld.score
                    next_beam.append((new_score, new_mask, chosen + [meld]))

            # Prune and keep only the top beam_width unique states
            next_beam.sort(key=lambda x: x[0], reverse=True)

            beam = []
            seen_masks_prune = set()
            for score, mask, chosen in next_beam:
                if mask not in seen_masks_prune:
                    seen_masks_prune.add(mask)
                    beam.append((score, mask, chosen))
                    if len(beam) >= self.beam_width:
                        break

        # Best arrangement is the first state in the final beam
        if beam:
            best_score, _, best_arrangement = beam[0]
        else:
            best_score, _, best_arrangement = 0, initial_mask, []

        # Map back to original Pydantic structures
        used_ids = set()
        best_melds = []
        for lm in best_arrangement:
            tiles_mapped = [pydantic_tile_map[lt.id] for lt in lm.tiles]
            for pyd_tile in tiles_mapped:
                used_ids.add(pyd_tile.id)
            best_melds.append(Meld(type=lm.type, tiles=tiles_mapped, score=lm.score))

        remaining_tiles = [
            pyd_tile for pyd_tile in resolved_tiles if pyd_tile.id not in used_ids
        ]

        # Sort remaining tiles to match the original ordering
        original_id_order = {
            pyd_tile.id: idx for idx, pyd_tile in enumerate(resolved_tiles)
        }
        remaining_tiles.sort(key=lambda pyd_tile: original_id_order[pyd_tile.id])

        return Arrangement(
            melds=best_melds,
            remainingTiles=remaining_tiles,
            totalScore=best_score,
        )
