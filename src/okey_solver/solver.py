# okey_solver/solver.py
from typing import List, Optional, Dict, Any
from okey_solver.types import Tile, Arrangement, OkeyMeta, TileColor
from okey_solver.rules import OkeyRuleValidator
from okey_solver.meld_generator import MeldGenerator
from okey_solver.backtracking_solver import BacktrackingSolver
from okey_solver.pair_finder import PairFinder


class SolverEngine:
    def __init__(self, validator: Optional[OkeyRuleValidator] = None):
        val = validator or OkeyRuleValidator()
        self.meld_generator = MeldGenerator(val)
        self.backtracking_solver = BacktrackingSolver()
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

        return self.backtracking_solver.solve(resolved_tiles, all_possible_melds)

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

    # Static wrappers
    _default_engine = None

    @classmethod
    def get_default_engine(cls):
        if cls._default_engine is None:
            cls._default_engine = SolverEngine()
        return cls._default_engine

    @classmethod
    def findBestArrangement(
        cls, tiles: List[Tile], okey_meta: Optional[OkeyMeta] = None
    ) -> Arrangement:
        return cls.get_default_engine().find_best_arrangement(tiles, okey_meta)

    @classmethod
    def findBestPairs(
        cls, tiles: List[Tile], okey_meta: Optional[OkeyMeta] = None
    ) -> Dict[str, Any]:
        return cls.get_default_engine().find_best_pairs(tiles, okey_meta)
