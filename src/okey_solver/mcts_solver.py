# okey_solver/mcts_solver.py
import math
import random
from typing import List, Dict, Tuple, Optional
from okey_core.types import Tile, Meld, Arrangement
from okey_solver.dto import LightTile, LightMeld


class MctsNode:
    def __init__(
        self,
        mask: int,
        chosen_indices: Tuple[int, ...],
        parent: Optional["MctsNode"] = None,
    ):
        self.mask = mask
        self.chosen_indices = chosen_indices  # Tuple of indexes in light_melds
        self.parent = parent
        self.visits = 0
        self.total_value = 0.0
        self.children: Dict[int, "MctsNode"] = {}  # action (meld index) -> child node
        self.untried_actions: Optional[List[int]] = None


class MctsSolver:
    """
    Optimizes meld arrangements using Monte Carlo Tree Search (MCTS).
    Simulates candidate meld selections (rollouts) at each step to find the arrangement with the highest expected value.
    """

    def __init__(self, iterations: int = 150, exploration_constant: float = 2.0):
        self.iterations = iterations
        self.exploration_constant = exploration_constant

    def solve(
        self, resolved_tiles: List[Tile], all_possible_melds: List[Meld]
    ) -> Arrangement:
        if not resolved_tiles:
            return Arrangement(melds=[], remainingTiles=[], totalScore=0)

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

        # Helper to get all valid actions (candidate meld indices that do not overlap with current mask)
        def get_valid_actions(mask: int, last_idx: int = -1) -> List[int]:
            actions = []
            # To avoid permutations (permutations of same selection), only consider indices > last_idx
            for idx in range(last_idx + 1, num_melds):
                m_mask = meld_masks[idx]
                if (mask & m_mask) == m_mask:
                    actions.append(idx)
            return actions

        root = MctsNode(initial_mask, ())
        root.untried_actions = get_valid_actions(root.mask)

        best_score = 0
        best_chosen_indices: Tuple[int, ...] = ()

        for _ in range(self.iterations):
            node = root

            # 1. Selection
            while (
                node.untried_actions is not None
                and len(node.untried_actions) == 0
                and len(node.children) > 0
            ):
                # Select best child using UCT
                best_uct = -1.0
                best_child = None
                log_parent_visits = math.log(node.visits) if node.visits > 0 else 0
                for action, child in node.children.items():
                    if child.visits == 0:
                        uct = float("inf")
                    else:
                        uct = (
                            child.total_value / child.visits
                        ) + self.exploration_constant * math.sqrt(
                            log_parent_visits / child.visits
                        )
                    if uct > best_uct:
                        best_uct = uct
                        best_child = child
                if best_child is not None:
                    node = best_child
                else:
                    break

            # 2. Expansion
            if node.untried_actions is not None and len(node.untried_actions) > 0:
                action = node.untried_actions.pop()
                m_mask = meld_masks[action]
                new_mask = node.mask ^ m_mask
                new_chosen = node.chosen_indices + (action,)
                child = MctsNode(new_mask, new_chosen, parent=node)

                # Get the last chosen index to enforce order
                last_idx = action
                child.untried_actions = get_valid_actions(child.mask, last_idx)
                node.children[action] = child
                node = child

            # 3. Simulation (Rollout)
            # Fast random simulation
            sim_mask = node.mask
            sim_chosen = list(node.chosen_indices)
            last_idx = sim_chosen[-1] if sim_chosen else -1
            valid_actions = get_valid_actions(sim_mask, last_idx)

            while valid_actions:
                action = random.choice(valid_actions)
                sim_mask ^= meld_masks[action]
                sim_chosen.append(action)
                valid_actions = get_valid_actions(sim_mask, action)

            # Evaluate simulation score
            score = sum(light_melds[idx].score for idx in sim_chosen)
            if score > best_score:
                best_score = score
                best_chosen_indices = tuple(sim_chosen)

            # 4. Backpropagation
            temp_node = node
            while temp_node is not None:
                temp_node.visits += 1
                temp_node.total_value += score
                temp_node = temp_node.parent

        # Map back to original Pydantic structures
        used_ids = set()
        best_melds = []
        for idx in best_chosen_indices:
            lm = light_melds[idx]
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
            totalScore=best_score,
        )
