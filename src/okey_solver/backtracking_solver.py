# okey_solver/backtracking_solver.py
from typing import List, Dict
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

        # State: a dictionary of available tile counts
        tile_counts = {}
        for t in resolved_tiles:
            tile_counts[t.id] = tile_counts.get(t.id, 0) + 1

        # Memoization cache
        # key: (current_index, sorted_tuple_of_remaining_tile_ids) -> max_score_achievable
        memo = {}

        def get_remaining_key() -> tuple:
            # Only include tiles that have count > 0, sorted by id
            return tuple(sorted(tid for tid, cnt in tile_counts.items() for _ in range(cnt)))

        def search(
            current_arrangement: List[Meld],
            current_index: int,
            current_score: int,
        ):
            nonlocal max_score, best_arrangement

            if current_score > max_score:
                max_score = current_score
                best_arrangement = list(current_arrangement)

            # Check cache
            state_key = (current_index, get_remaining_key())
            if state_key in memo and memo[state_key] >= current_score:
                return
            memo[state_key] = current_score

            for i in range(current_index, len(all_possible_melds)):
                candidate_meld = all_possible_melds[i]

                # Check if we can form candidate_meld using the current tile_counts
                can_form = True
                temp_dec = []
                for t in candidate_meld.tiles:
                    if tile_counts.get(t.id, 0) > 0:
                        tile_counts[t.id] -= 1
                        temp_dec.append(t.id)
                    else:
                        can_form = False
                        break

                if can_form:
                    meld_score = sum(t.value for t in candidate_meld.tiles)
                    current_arrangement.append(candidate_meld)

                    search(current_arrangement, i + 1, current_score + meld_score)

                    current_arrangement.pop()

                # Revert decrementing
                for tid in temp_dec:
                    tile_counts[tid] += 1

        search([], 0, 0)

        used_ids = set()
        for m in best_arrangement:
            for t in m.tiles:
                used_ids.add(t.id)

        remaining_tiles = [t for t in resolved_tiles if t.id not in used_ids]

        return Arrangement(
            melds=best_arrangement, remainingTiles=remaining_tiles, totalScore=max_score
        )
