# okey_solver/backtracking_solver.py
from typing import List, Dict, Tuple
from okey_core.types import Tile, Meld, Arrangement
from okey_solver.dto import LightTile, LightMeld


class BacktrackingSolver:
    """
    Backtracking ile aday havuzundaki per/seri kombinasyonlarından en yüksek puanlı çakışmasız dizilimi bulur.
    """

    def solve(
        self, resolved_tiles: List[Tile], all_possible_melds: List[Meld]
    ) -> Arrangement:
        # Create map of original Pydantic tiles
        pydantic_tile_map = {t.id: t for t in resolved_tiles}

        # DTO Mapping: Map Pydantic models to lightweight DTOs
        light_tiles = [LightTile(t.id, t.color, t.value) for t in resolved_tiles]
        
        # Map melds and their constituent tiles
        light_melds = []
        for m in all_possible_melds:
            m_tiles = [LightTile(t.id, t.color, t.value) for t in m.tiles]
            light_melds.append(LightMeld(m.type, m_tiles, m.score))

        best_arrangement: List[LightMeld] = []
        max_score = 0

        # Map each unique tile ID to a specific bit index (0 to N-1)
        tile_to_bit = {t.id: idx for idx, t in enumerate(light_tiles)}
        num_tiles = len(light_tiles)

        # Initial mask: all bits set to 1 (all tiles available)
        initial_mask = (1 << num_tiles) - 1

        # Memoization cache
        memo: Dict[Tuple[int, int], int] = {}

        def search(
            current_arrangement: List[LightMeld],
            current_index: int,
            current_score: int,
            mask: int,
        ):
            nonlocal max_score, best_arrangement

            if current_score > max_score:
                max_score = current_score
                best_arrangement = list(current_arrangement)

            # Check cache
            state_key = (current_index, mask)
            if state_key in memo and memo[state_key] >= current_score:
                return
            memo[state_key] = current_score

            for i in range(current_index, len(light_melds)):
                candidate_meld = light_melds[i]

                can_form = True
                meld_mask = 0
                for t in candidate_meld.tiles:
                    bit = tile_to_bit[t.id]
                    if (mask & (1 << bit)) != 0:
                        meld_mask |= (1 << bit)
                    else:
                        can_form = False
                        break

                if can_form:
                    current_arrangement.append(candidate_meld)

                    search(
                        current_arrangement,
                        i + 1,
                        current_score + candidate_meld.score,
                        mask ^ meld_mask,
                    )

                    current_arrangement.pop()

        search([], 0, 0, initial_mask)

        # Map DTOs back to original Pydantic objects
        used_ids = set()
        best_melds = []
        for lm in best_arrangement:
            tiles_mapped = [pydantic_tile_map[lt.id] for lt in lm.tiles]
            for t in tiles_mapped:
                used_ids.add(t.id)
            best_melds.append(Meld(type=lm.type, tiles=tiles_mapped, score=lm.score))

        remaining_tiles = [t for t in resolved_tiles if t.id not in used_ids]

        return Arrangement(
            melds=best_melds, remainingTiles=remaining_tiles, totalScore=max_score
        )
