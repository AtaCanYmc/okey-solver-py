# tests/test_advanced_solvers.py
from okey_core.types import Tile, TileColor
from okey_solver import create_standard_okey_solver, DiscardEvaluator


def test_ilp_solver_runs():
    """
    Tests that the ILP solver yields identical/correct scores as the backtracking solver.
    """
    # Define a clean hand
    tiles = [
        Tile(id="t1", color=TileColor.RED, value=5),
        Tile(id="t2", color=TileColor.RED, value=6),
        Tile(id="t3", color=TileColor.RED, value=7),
        Tile(id="t4", color=TileColor.BLUE, value=10),
        Tile(id="t5", color=TileColor.BLACK, value=10),
        Tile(id="t6", color=TileColor.YELLOW, value=10),
        Tile(id="t7", color=TileColor.RED, value=12),
    ]

    solver_ilp = create_standard_okey_solver(strategy="ilp")
    solver_bt = create_standard_okey_solver(strategy="backtracking")

    arr_ilp = solver_ilp.find_best_arrangement(tiles)
    arr_bt = solver_bt.find_best_arrangement(tiles)

    # Both should identify the same score
    assert arr_ilp.totalScore == arr_bt.totalScore
    assert len(arr_ilp.melds) == 2  # 5-6-7 RED and 10-10-10 Group
    assert len(arr_ilp.remainingTiles) == 1  # 12 RED remains


def test_hybrid_solver_runs():
    """
    Tests that the Hybrid solver resolves hands correctly and respects its boundaries.
    """
    tiles = [
        Tile(id="t1", color=TileColor.YELLOW, value=1),
        Tile(id="t2", color=TileColor.YELLOW, value=2),
        Tile(id="t3", color=TileColor.YELLOW, value=3),
    ]

    solver_hybrid = create_standard_okey_solver(strategy="hybrid")
    arr = solver_hybrid.find_best_arrangement(tiles)

    assert arr.totalScore == 6
    assert len(arr.melds) == 1
    assert len(arr.remainingTiles) == 0


def test_discard_evaluator():
    """
    Tests that DiscardEvaluator computes meld probabilities correctly and recommends
    the least useful tile for discarding.
    """
    # 5 and 6 RED are connected (needs 4 or 7 to complete a run)
    # 12 BLACK is completely disconnected
    hand = [
        Tile(id="t1", color=TileColor.RED, value=5),
        Tile(id="t2", color=TileColor.RED, value=6),
        Tile(id="t3", color=TileColor.BLACK, value=12),
    ]

    # Assume they are remaining tiles in the arrangement
    solver = create_standard_okey_solver()
    arr = solver.find_best_arrangement(hand)

    evaluator = DiscardEvaluator()
    recommendations = evaluator.evaluate_discards(hand, arr)

    assert len(recommendations) == 3
    # The first recommendation should be the lowest score (best to discard)
    # 12 BLACK should be recommended first since 5-6 RED has run connections
    best_discard = recommendations[0]
    assert best_discard["tile"].color == TileColor.BLACK
    assert best_discard["tile"].value == 12
