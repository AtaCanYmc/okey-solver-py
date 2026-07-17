# okey_solver/hybrid_solver.py
import time
from typing import List, Dict, Tuple
from okey_core.types import Tile, Meld, Arrangement
from okey_solver.greedy_solver import GreedySolver
from okey_solver.dto import LightTile, LightMeld


class HybridSolver:
    """
    Solves okey hand arrangements using a Hybrid approach:
    1. First calculates a quick baseline using GreedySolver.
    2. Runs an optimized Branch & Bound backtracking solver pruned by the greedy baseline.
    3. Respects a strict timeout_ms (default: 50ms). If the timeout is exceeded, it terminates
       and returns the best arrangement found up to that point.
    """

    def __init__(self, timeout_ms: float = 50.0):
        self.timeout_ms = timeout_ms
        self.greedy_solver = GreedySolver()

    def solve(
        self, resolved_tiles: List[Tile], all_possible_melds: List[Meld]
    ) -> Arrangement:
        if not resolved_tiles:
            return Arrangement(melds=[], remainingTiles=[], totalScore=0)

        # 1. Run Greedy Solver to establish the baseline lower bound
        greedy_arrangement = self.greedy_solver.solve(
            resolved_tiles, all_possible_melds
        )
        max_score = greedy_arrangement.totalScore

        # If greedy already placed all tiles, return immediately
        if not greedy_arrangement.remainingTiles:
            return greedy_arrangement

        # 2. Setup DTO structures for Backtracking
        pydantic_tile_map = {t.id: t for t in resolved_tiles}
        light_tiles = [LightTile(t.id, t.color, t.value) for t in resolved_tiles]

        light_melds = []
        for m in all_possible_melds:
            m_tiles = [LightTile(t.id, t.color, t.value) for t in m.tiles]
            light_melds.append(LightMeld(m.type, m_tiles, m.score))

        tile_to_bit = {t.id: idx for idx, t in enumerate(light_tiles)}
        num_tiles = len(light_tiles)
        initial_mask = (1 << num_tiles) - 1

        best_lm_arrangement: List[LightMeld] = []
        start_time = time.time()
        timeout_seconds = self.timeout_ms / 1000.0

        # Calculate prefix sum of remaining maximum possible scores for pruning
        # Sort melds by score descending to find higher scores first
        light_melds.sort(key=lambda x: x.score, reverse=True)

        # prefix_max_scores[i] = sum of scores from index i to end
        prefix_max_scores = [0] * (len(light_melds) + 1)
        for i in range(len(light_melds) - 1, -1, -1):
            prefix_max_scores[i] = prefix_max_scores[i + 1] + light_melds[i].score

        memo: Dict[Tuple[int, int], int] = {}

        def search(
            current_arrangement: List[LightMeld],
            current_index: int,
            current_score: int,
            mask: int,
        ):
            nonlocal max_score, best_lm_arrangement

            # Timeout check
            if time.time() - start_time > timeout_seconds:
                return

            # Branch & Bound Pruning: if current score + maximum remaining score can't beat max_score, prune
            if current_score + prefix_max_scores[current_index] <= max_score:
                return

            if current_score > max_score:
                max_score = current_score
                best_lm_arrangement = list(current_arrangement)

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
                        meld_mask |= 1 << bit
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

        # 3. If backtracking found a better solution, rebuild and return it
        if best_lm_arrangement:
            used_ids = set()
            best_melds = []
            for lm in best_lm_arrangement:
                tiles_mapped = [pydantic_tile_map[lt.id] for lt in lm.tiles]
                for t in tiles_mapped:
                    used_ids.add(t.id)
                best_melds.append(
                    Meld(type=lm.type, tiles=tiles_mapped, score=lm.score)
                )

            remaining_tiles = [t for t in resolved_tiles if t.id not in used_ids]
            return Arrangement(
                melds=best_melds, remainingTiles=remaining_tiles, totalScore=max_score
            )

        return greedy_arrangement
