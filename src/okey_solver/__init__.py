# okey_solver/__init__.py
import logging

logging.getLogger("okey_solver").addHandler(logging.NullHandler())
from okey_solver.types import TileColor, Tile, MeldType, Meld, OkeyMeta, Arrangement
from okey_solver.rules import OkeyRuleValidator, RuleValidator
from okey_solver.solver import SolverEngine, create_standard_okey_solver, create_okey_101_solver
from okey_solver.meld_generator import MeldGenerator
from okey_solver.backtracking_solver import BacktrackingSolver
from okey_solver.pair_finder import PairFinder
from okey_solver.errors import (
    OkeySolverError,
    InvalidTileError,
    InvalidArrangementError,
)

__all__ = [
    "TileColor",
    "Tile",
    "MeldType",
    "Meld",
    "OkeyMeta",
    "Arrangement",
    "OkeyRuleValidator",
    "RuleValidator",
    "SolverEngine",
    "MeldGenerator",
    "BacktrackingSolver",
    "PairFinder",
    "OkeySolverError",
    "InvalidTileError",
    "InvalidArrangementError",
    "create_standard_okey_solver",
    "create_okey_101_solver",
]
