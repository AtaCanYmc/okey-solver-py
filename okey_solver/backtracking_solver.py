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

        def can_form_meld(needed_tiles: List[Tile], pool: List[Tile]) -> bool:
            pool_counts: Dict[str, int] = {}
            for t in pool:
                pool_counts[t.id] = pool_counts.get(t.id, 0) + 1

            needed_counts: Dict[str, int] = {}
            for t in needed_tiles:
                needed_counts[t.id] = needed_counts.get(t.id, 0) + 1

            for tile_id, count in needed_counts.items():
                if pool_counts.get(tile_id, 0) < count:
                    return False
            return True

        def remove_tiles_from_pool(
            used_tiles: List[Tile], pool: List[Tile]
        ) -> List[Tile]:
            remaining = list(pool)
            for used in used_tiles:
                for idx, t in enumerate(remaining):
                    if t.id == used.id:
                        remaining.pop(idx)
                        break
            return remaining

        def calculate_arrangement_score(melds: List[Meld]) -> int:
            score = 0
            for meld in melds:
                score += sum(t.value for t in meld.tiles)
            return score

        def search(
            current_arrangement: List[Meld],
            remaining_pool: List[Tile],
            current_index: int,
        ):
            nonlocal max_score, best_arrangement
            current_score = calculate_arrangement_score(current_arrangement)

            if current_score > max_score:
                max_score = current_score
                best_arrangement = list(current_arrangement)

            for i in range(current_index, len(all_possible_melds)):
                candidate_meld = all_possible_melds[i]

                if can_form_meld(candidate_meld.tiles, remaining_pool):
                    next_remaining_pool = remove_tiles_from_pool(
                        candidate_meld.tiles, remaining_pool
                    )
                    current_arrangement.append(candidate_meld)

                    search(current_arrangement, next_remaining_pool, i + 1)

                    current_arrangement.pop()

        search([], resolved_tiles, 0)

        used_ids = set()
        for m in best_arrangement:
            for t in m.tiles:
                used_ids.add(t.id)

        remaining_tiles = [t for t in resolved_tiles if t.id not in used_ids]

        return Arrangement(
            melds=best_arrangement, remainingTiles=remaining_tiles, totalScore=max_score
        )
