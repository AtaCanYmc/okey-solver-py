# okey_solver/simulated_annealing_solver.py
import math
import random
from typing import List, Tuple
from okey_core.types import Tile, Meld, Arrangement
from okey_solver.dto import LightTile, LightMeld


class SimulatedAnnealingSolver:
    """
    Finds the optimal meld arrangement using Simulated Annealing.
    Utilizes a probabilistic acceptance mechanism to escape local minima.
    """

    def __init__(
        self,
        initial_temp: float = 100.0,
        cooling_rate: float = 0.95,
        min_temp: float = 0.1,
        steps_per_temp: int = 15,
    ):
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp
        self.steps_per_temp = steps_per_temp

    def solve(
        self, resolved_tiles: List[Tile], all_possible_melds: List[Meld]
    ) -> Arrangement:
        if not resolved_tiles or not all_possible_melds:
            return Arrangement(melds=[], remainingTiles=resolved_tiles, totalScore=0)

        pydantic_tile_map = {t.id: t for t in resolved_tiles}

        # DTO Mapping
        light_tiles = [LightTile(t.id, t.color, t.value) for t in resolved_tiles]
        light_melds = []
        for m in all_possible_melds:
            m_tiles = [LightTile(t.id, t.color, t.value) for t in m.tiles]
            light_melds.append(LightMeld(m.type, m_tiles, m.score))

        tile_to_bit = {t.id: idx for idx, t in enumerate(light_tiles)}
        num_tiles = len(light_tiles)
        initial_mask = (1 << num_tiles) - 1
        num_melds = len(light_melds)

        # Precalculate masks for all light melds
        meld_masks = []
        for m in light_melds:
            mask = 0
            for t in m.tiles:
                if t.id in tile_to_bit:
                    mask |= 1 << tile_to_bit[t.id]
            meld_masks.append(mask)

        # Helper to repair chromosome and calculate score/melds
        def evaluate(state: List[int]) -> Tuple[int, List[LightMeld]]:
            # state is a list of 0s and 1s representing selected melds
            selected_indices = [i for i, val in enumerate(state) if val == 1]
            # Repair logic: sort selected by score descending to greedily pack
            selected_indices.sort(
                key=lambda idx: (light_melds[idx].score, -len(light_melds[idx].tiles)),
                reverse=True,
            )

            mask = initial_mask
            score = 0
            chosen_melds = []
            for idx in selected_indices:
                m_mask = meld_masks[idx]
                if (mask & m_mask) == m_mask:
                    mask ^= m_mask
                    score += light_melds[idx].score
                    chosen_melds.append(light_melds[idx])
            return score, chosen_melds

        # Initial state: random configuration
        current_state = [random.choice([0, 1]) for _ in range(num_melds)]
        current_score, current_chosen = evaluate(current_state)

        best_state = list(current_state)
        best_score = current_score
        best_chosen = current_chosen

        temp = self.initial_temp

        while temp > self.min_temp:
            for _ in range(self.steps_per_temp):
                # Generate a neighbor by flipping one random bit
                neighbor_state = list(current_state)
                flip_idx = random.randint(0, num_melds - 1)
                neighbor_state[flip_idx] = 1 - neighbor_state[flip_idx]

                neighbor_score, neighbor_chosen = evaluate(neighbor_state)

                # Calculate delta score
                delta = neighbor_score - current_score

                # Accept or reject
                if delta > 0:
                    current_state = neighbor_state
                    current_score = neighbor_score
                    current_chosen = neighbor_chosen
                    if neighbor_score > best_score:
                        best_score = neighbor_score
                        best_state = list(neighbor_state)
                        best_chosen = neighbor_chosen
                else:
                    # Calculate acceptance probability
                    prob = math.exp(delta / temp) if temp > 0 else 0
                    if random.random() < prob:
                        current_state = neighbor_state
                        current_score = neighbor_score
                        current_chosen = neighbor_chosen

            # Cool down
            temp *= self.cooling_rate

        # Reconstruct final Arrangement
        used_ids = set()
        best_melds = []
        for lm in best_chosen:
            tiles_mapped = [pydantic_tile_map[lt.id] for lt in lm.tiles]
            for t in tiles_mapped:
                used_ids.add(t.id)
            best_melds.append(Meld(type=lm.type, tiles=tiles_mapped, score=lm.score))

        remaining_tiles = [t for t in resolved_tiles if t.id not in used_ids]

        # Sort remaining tiles to match original ordering
        original_id_order = {t.id: idx for idx, t in enumerate(resolved_tiles)}
        remaining_tiles.sort(key=lambda t: original_id_order[t.id])

        return Arrangement(
            melds=best_melds,
            remainingTiles=remaining_tiles,
            totalScore=best_score,
        )
