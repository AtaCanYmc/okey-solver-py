# okey_solver/ilp_solver.py
import pulp
from typing import List, Dict
from okey_core.types import Tile, Meld, Arrangement


class IlpSolver:
    """
    Solves the Okey hand arrangement problem as an Integer Linear Programming (ILP) Set Cover problem.
    """

    def solve(
        self, resolved_tiles: List[Tile], all_possible_melds: List[Meld]
    ) -> Arrangement:
        if not resolved_tiles:
            return Arrangement(melds=[], remainingTiles=[], totalScore=0)

        # Create map of original Pydantic tiles
        {t.id: t for t in resolved_tiles}

        # Initialize the maximization problem
        prob = pulp.LpProblem("Okey_Hand_Arrangement", pulp.LpMaximize)

        # Define binary variables: x[j] = 1 if meld j is selected, 0 otherwise
        x = [
            pulp.LpVariable(f"meld_{j}", cat=pulp.LpBinary)
            for j in range(len(all_possible_melds))
        ]

        # Objective Function: Maximize total meld score
        prob += pulp.lpSum(
            x[j] * all_possible_melds[j].score for j in range(len(all_possible_melds))
        )

        # Map each unique tile ID to its index in the resolved_tiles list
        tile_to_idx = {t.id: idx for idx, t in enumerate(resolved_tiles)}

        # Constraints: Each tile can be part of at most one selected meld
        tile_usages: Dict[int, List[int]] = {
            idx: [] for idx in range(len(resolved_tiles))
        }
        for j, meld in enumerate(all_possible_melds):
            for t in meld.tiles:
                if t.id in tile_to_idx:
                    tile_usages[tile_to_idx[t.id]].append(j)

        for idx in range(len(resolved_tiles)):
            prob += pulp.lpSum(x[j] for j in tile_usages[idx]) <= 1

        # Solve the ILP problem
        prob.solve(pulp.PULP_CBC_CMD(msg=False))

        # Retrieve selected melds
        selected_melds = []
        used_ids = set()
        for j in range(len(all_possible_melds)):
            if pulp.value(x[j]) is not None and pulp.value(x[j]) > 0.5:
                meld = all_possible_melds[j]
                selected_melds.append(meld)
                for t in meld.tiles:
                    used_ids.add(t.id)

        # Compute remaining tiles
        remaining_tiles = [t for t in resolved_tiles if t.id not in used_ids]
        total_score = sum(m.score for m in selected_melds)

        return Arrangement(
            melds=selected_melds,
            remainingTiles=remaining_tiles,
            totalScore=total_score,
        )
