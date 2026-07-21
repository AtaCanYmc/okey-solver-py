# okey_solver/genetic_solver.py
import random
from typing import List, Tuple
from okey_core.types import Tile, Meld, Arrangement
from okey_solver.dto import LightTile, LightMeld


class GeneticSolver:
    """
    Finds the optimal meld arrangement using a Genetic Algorithm (Evolutionary Search).
    Designed to quickly find near-global optimums in very large search spaces.
    """

    def __init__(
        self,
        pop_size: int = 40,
        generations: int = 50,
        crossover_rate: float = 0.8,
        mutation_rate: float = 0.15,
        elitism_count: int = 2,
    ):
        self.pop_size = pop_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elitism_count = elitism_count

    def solve(
        self, resolved_tiles: List[Tile], all_possible_melds: List[Meld]
    ) -> Arrangement:
        if not resolved_tiles or not all_possible_melds:
            return Arrangement(melds=[], remainingTiles=resolved_tiles, totalScore=0)

        pydantic_tile_map = {t.id: t for t in resolved_tiles}

        # DTO Mapping
        light_tiles = [LightTile(t.id, t.color, t.value) for t in resolved_tiles]
        light_melds: List[LightMeld] = []
        for m in all_possible_melds:
            m_tiles = [LightTile(t.id, t.color, t.value) for t in m.tiles]
            light_melds.append(LightMeld(m.type, m_tiles, m.score))

        tile_to_bit = {t.id: idx for idx, t in enumerate(light_tiles)}
        num_tiles = len(light_tiles)
        initial_mask = (1 << num_tiles) - 1
        num_melds = len(light_melds)

        # Precalculate masks for all light melds
        meld_masks = []
        for lm in light_melds:
            mask = 0
            for tile in lm.tiles:
                if tile.id in tile_to_bit:
                    mask |= 1 << tile_to_bit[tile.id]
            meld_masks.append(mask)

        # Helper to repair chromosome and calculate fitness
        def evaluate(chromosome: Tuple[int, ...]) -> Tuple[int, List[LightMeld]]:
            # Extract selected melds
            selected_indices = [i for i, gene in enumerate(chromosome) if gene == 1]
            # To repair, we can sort them by score descending
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

        # Initialize population
        # Chromosome is a tuple of 0 or 1
        population: List[Tuple[int, ...]] = []
        for _ in range(self.pop_size):
            chromosome = tuple(random.choice([0, 1]) for _ in range(num_melds))
            population.append(chromosome)

        best_score = -1
        best_chosen_melds: List[LightMeld] = []

        # Run generations
        for _ in range(self.generations):
            # Evaluate fitness
            evaluated_pop = []
            for chrom in population:
                score, chosen = evaluate(chrom)
                evaluated_pop.append((score, chrom, chosen))
                if score > best_score:
                    best_score = score
                    best_chosen_melds = chosen

            # Sort population by fitness descending
            evaluated_pop.sort(key=lambda x: x[0], reverse=True)

            # Elitism: carry over the best
            next_pop = [evaluated_pop[i][1] for i in range(self.elitism_count)]

            # Selection & Reproduction
            while len(next_pop) < self.pop_size:
                # Tournament selection
                # Parent 1
                t1 = random.sample(evaluated_pop, 2)
                t1.sort(key=lambda x: x[0], reverse=True)
                p1 = t1[0][1]

                # Parent 2
                t2 = random.sample(evaluated_pop, 2)
                t2.sort(key=lambda x: x[0], reverse=True)
                p2 = t2[0][1]

                # Crossover
                if random.random() < self.crossover_rate:
                    # Single-point crossover
                    pt = random.randint(1, num_melds - 1) if num_melds > 1 else 0
                    c1 = p1[:pt] + p2[pt:]
                    c2 = p2[:pt] + p1[pt:]
                else:
                    c1, c2 = p1, p2

                # Mutation
                c1_list = list(c1)
                c2_list = list(c2)
                mutation_prob = self.mutation_rate / num_melds if num_melds > 0 else 0.1
                for i in range(num_melds):
                    if random.random() < mutation_prob:
                        c1_list[i] = 1 - c1_list[i]
                    if random.random() < mutation_prob:
                        c2_list[i] = 1 - c2_list[i]

                next_pop.append(tuple(c1_list))
                if len(next_pop) < self.pop_size:
                    next_pop.append(tuple(c2_list))

            population = next_pop

        # Build final Arrangement
        used_ids = set()
        best_melds = []
        for lm in best_chosen_melds:
            tiles_mapped = [pydantic_tile_map[lt.id] for lt in lm.tiles]
            for t in tiles_mapped:
                used_ids.add(t.id)
            best_melds.append(Meld(type=lm.type, tiles=tiles_mapped, score=lm.score))

        remaining_tiles = [t for t in resolved_tiles if t.id not in used_ids]

        # Sort remaining tiles to match the original ordering
        original_id_order = {t.id: idx for idx, t in enumerate(resolved_tiles)}
        remaining_tiles.sort(key=lambda t: original_id_order[t.id])

        return Arrangement(
            melds=best_melds,
            remainingTiles=remaining_tiles,
            totalScore=max(0, best_score),
        )
