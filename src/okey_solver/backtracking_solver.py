# okey_solver/backtracking_solver.py
from typing import List, Dict, Tuple
from okey_solver.types import Tile, Meld, Arrangement


class BacktrackingSolver:
    """
    Backtracking ile aday havuzundaki per/seri kombinasyonlarından en yüksek puanlı çakışmasız dizilimi bulur.
    """

    def solve(
        self, resolved_tiles: List[Tile], all_possible_melds: List[Meld]
    ) -> Arrangement:
        best_arrangement: List[Meld] = []
        max_score = 0

        # Map each unique tile ID to a specific bit index (0 to N-1)
        tile_to_bit = {t.id: idx for idx, t in enumerate(resolved_tiles)}
        num_tiles = len(resolved_tiles)

        # Initial mask: all bits set to 1 (all tiles available)
        initial_mask = (1 << num_tiles) - 1

        # Memoization cache
        # key: (current_index, mask) -> max_score_achievable
        memo: Dict[Tuple[int, int], int] = {}

        def search(
            current_arrangement: List[Meld],
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

            for i in range(current_index, len(all_possible_melds)):
                candidate_meld = all_possible_melds[i]

                # Check if all tiles in candidate_meld are available in the current mask
                can_form = True
                meld_mask = 0
                for t in candidate_meld.tiles:
                    bit = tile_to_bit[t.id]
                    if (mask & (1 << bit)) != 0:
                        # Mark this bit to be cleared
                        meld_mask |= (1 << bit)
                    else:
                        can_form = False
                        break

                if can_form:
                    meld_score = sum(t.value for t in candidate_meld.tiles)
                    current_arrangement.append(candidate_meld)

                    # recurse with mask bits cleared
                    search(
                        current_arrangement,
                        i + 1,
                        current_score + meld_score,
                        mask ^ meld_mask,
                    )

                    current_arrangement.pop()

        search([], 0, 0, initial_mask)

        used_ids = set()
        for m in best_arrangement:
            for t in m.tiles:
                used_ids.add(t.id)

        remaining_tiles = [t for t in resolved_tiles if t.id not in used_ids]

        return Arrangement(
            melds=best_arrangement, remainingTiles=remaining_tiles, totalScore=max_score
        )
