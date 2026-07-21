# okey_solver/__init__.py
from okey_solver.types import TileColor, Tile, MeldType, Meld, OkeyMeta, Arrangement
from okey_solver.rules import OkeyRuleValidator, RuleValidator
from okey_solver.solver import (
    SolverEngine,
    create_standard_okey_solver,
    create_okey_101_solver,
)
from okey_solver.meld_generator import MeldGenerator
from okey_solver.backtracking_solver import BacktrackingSolver
from okey_solver.pair_finder import PairFinder
from okey_solver.ilp_solver import IlpSolver
from okey_solver.hybrid_solver import HybridSolver
from okey_solver.beam_search_solver import BeamSearchSolver
from okey_solver.genetic_solver import GeneticSolver
from okey_solver.simulated_annealing_solver import SimulatedAnnealingSolver
from okey_solver.mcts_solver import MctsSolver
from okey_solver.evaluator import DiscardEvaluator
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
    "IlpSolver",
    "HybridSolver",
    "BeamSearchSolver",
    "GeneticSolver",
    "SimulatedAnnealingSolver",
    "MctsSolver",
    "DiscardEvaluator",
    "OkeySolverError",
    "InvalidTileError",
    "InvalidArrangementError",
    "create_standard_okey_solver",
    "create_okey_101_solver",
]

import logging

logging.getLogger("okey_solver").addHandler(logging.NullHandler())
