# tests/test_strategic_solvers.py
from okey_core.types import Tile, TileColor
from okey_solver import create_standard_okey_solver


def _get_test_hand():
    return [
        Tile(id="t1", color=TileColor.RED, value=5),
        Tile(id="t2", color=TileColor.RED, value=6),
        Tile(id="t3", color=TileColor.RED, value=7),
        Tile(id="t4", color=TileColor.BLUE, value=10),
        Tile(id="t5", color=TileColor.BLACK, value=10),
        Tile(id="t6", color=TileColor.YELLOW, value=10),
        Tile(id="t7", color=TileColor.RED, value=12),
    ]


def test_beam_solver():
    hand = _get_test_hand()
    solver = create_standard_okey_solver(strategy="beam")
    arr = solver.find_best_arrangement(hand)

    assert arr.totalScore == 48
    assert len(arr.melds) == 2
    assert len(arr.remainingTiles) == 1
    assert arr.remainingTiles[0].id == "t7"


def test_genetic_solver():
    hand = _get_test_hand()
    solver = create_standard_okey_solver(strategy="genetic")
    arr = solver.find_best_arrangement(hand)

    # Genetic algorithm might be probabilistic, but for a tiny hand size it should easily find optimal
    assert arr.totalScore == 48
    assert len(arr.melds) == 2
    assert len(arr.remainingTiles) == 1


def test_simulated_annealing_solver():
    hand = _get_test_hand()
    solver = create_standard_okey_solver(strategy="annealing")
    arr = solver.find_best_arrangement(hand)

    # Simulated annealing should easily find optimal for small hand
    assert arr.totalScore == 48
    assert len(arr.melds) == 2
    assert len(arr.remainingTiles) == 1


def test_mcts_solver():
    hand = _get_test_hand()
    solver = create_standard_okey_solver(strategy="mcts")
    arr = solver.find_best_arrangement(hand)

    assert arr.totalScore == 48
    assert len(arr.melds) == 2
    assert len(arr.remainingTiles) == 1
