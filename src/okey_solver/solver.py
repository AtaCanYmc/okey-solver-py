# okey_solver/solver.py
from typing import List, Optional, Dict, Any, Union
from okey_core.types import Tile, Arrangement, OkeyMeta, TileColor
from okey_solver.rules import OkeyRuleValidator
from okey_solver.meld_generator import MeldGenerator
from okey_solver.backtracking_solver import BacktrackingSolver
from okey_solver.greedy_solver import GreedySolver
from okey_solver.pair_finder import PairFinder
from okey_solver.ilp_solver import IlpSolver
from okey_solver.hybrid_solver import HybridSolver


class SolverEngine:
    def __init__(
        self,
        validator: Optional[OkeyRuleValidator] = None,
        strategy: str = "backtracking",
    ):
        val = validator or OkeyRuleValidator()
        self.meld_generator = MeldGenerator(val)
        self.strategy = strategy.lower()

        if self.strategy == "greedy":
            self.solver = GreedySolver()
        elif self.strategy == "ilp":
            self.solver = IlpSolver()
        elif self.strategy == "hybrid":
            self.solver = HybridSolver()
        else:
            self.solver = BacktrackingSolver()

        self.pair_finder = PairFinder()

    def find_best_arrangement(
        self, tiles: List[Tile], okey_meta: Optional[OkeyMeta] = None
    ) -> Arrangement:
        resolved_tiles = (
            self.resolve_false_okeys(tiles, okey_meta) if okey_meta else tiles
        )

        wildcards = []
        normal_tiles = []
        if okey_meta:
            for t in resolved_tiles:
                if t.color == okey_meta.color and t.value == okey_meta.value:
                    wildcards.append(t)
                else:
                    normal_tiles.append(t)
        else:
            normal_tiles = resolved_tiles

        all_possible_melds = self.meld_generator.generate_all_possible_melds(
            normal_tiles, wildcards, okey_meta
        )

        return self.solver.solve(resolved_tiles, all_possible_melds)

    def find_best_pairs(
        self, tiles: List[Tile], okey_meta: Optional[OkeyMeta] = None
    ) -> Dict[str, Any]:
        return self.pair_finder.find_best_pairs(tiles, okey_meta)

    def resolve_false_okeys(self, tiles: List[Tile], okey_meta: OkeyMeta) -> List[Tile]:
        resolved = []
        for t in tiles:
            if t.color == TileColor.JOKER:
                resolved.append(
                    Tile(id=t.id, color=okey_meta.color, value=okey_meta.value)
                )
            else:
                resolved.append(t)
        return resolved

    # Legacy static wrappers - no longer uses singleton global state
    @classmethod
    def findBestArrangement(
        cls, tiles: List[Tile], okey_meta: Optional[OkeyMeta] = None
    ) -> Arrangement:
        return cls().find_best_arrangement(tiles, okey_meta)

    @classmethod
    def findBestPairs(
        cls, tiles: List[Tile], okey_meta: Optional[OkeyMeta] = None
    ) -> Dict[str, Any]:
        return cls().find_best_pairs(tiles, okey_meta)


def create_standard_okey_solver(strategy: str = "backtracking") -> SolverEngine:
    """
    Standard Okey (Rummikub) kurallarına uygun bir SolverEngine örneği döner.
    """
    return SolverEngine(validator=OkeyRuleValidator(), strategy=strategy)


def create_okey_101_solver(strategy: str = "backtracking") -> SolverEngine:
    """
    Okey 101 kurallarına uygun bir SolverEngine örneği döner (Gelecekteki genişletmeler için hazırdır).
    """
    # 101 validator rule engine placeholder
    return SolverEngine(validator=OkeyRuleValidator(), strategy=strategy)
