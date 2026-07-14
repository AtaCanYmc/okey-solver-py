from okey_solver import SolverEngine, Tile, TileColor, OkeyMeta, MeldType


def create_tile(tile_id: str, color: TileColor, value: int) -> Tile:
    return Tile(id=tile_id, color=color, value=value)


# Okey: RED 7
okey_meta = OkeyMeta(color=TileColor.RED, value=7)
joker1 = create_tile("okey_1", TileColor.RED, 7)
joker2 = create_tile("okey_2", TileColor.RED, 7)


def test_joker_seri_ortasi():
    tiles = [
        create_tile("r4", TileColor.RED, 4),
        joker1,
        create_tile("r6", TileColor.RED, 6),
    ]
    result = SolverEngine.findBestArrangement(tiles, okey_meta)
    assert len(result.melds) == 1
    assert result.melds[0].type == MeldType.SERI
    assert len(result.melds[0].tiles) == 3
    assert len(result.remainingTiles) == 0


def test_joker_seri_basi():
    tiles = [
        joker1,
        create_tile("r5", TileColor.RED, 5),
        create_tile("r6", TileColor.RED, 6),
    ]
    result = SolverEngine.findBestArrangement(tiles, okey_meta)
    assert len(result.melds) == 1
    assert result.melds[0].type == MeldType.SERI
    assert len(result.remainingTiles) == 0


def test_joker_seri_sonu():
    tiles = [
        create_tile("r5", TileColor.RED, 5),
        create_tile("r6", TileColor.RED, 6),
        joker1,
    ]
    result = SolverEngine.findBestArrangement(tiles, okey_meta)
    assert len(result.melds) == 1
    assert result.melds[0].type == MeldType.SERI
    assert len(result.remainingTiles) == 0


def test_iki_joker_5_tasli_seri():
    blue_okey_meta = OkeyMeta(color=TileColor.BLUE, value=10)
    bjoker1 = create_tile("bjoker1", TileColor.BLUE, 10)
    bjoker2 = create_tile("bjoker2", TileColor.BLUE, 10)

    tiles = [
        create_tile("b4", TileColor.BLUE, 4),
        create_tile("b5", TileColor.BLUE, 5),
        bjoker1,
        bjoker2,
        create_tile("b8", TileColor.BLUE, 8),
    ]
    result = SolverEngine.findBestArrangement(tiles, blue_okey_meta)
    assert len(result.melds) == 1
    assert result.melds[0].type == MeldType.SERI
    assert len(result.melds[0].tiles) == 5
    assert len(result.remainingTiles) == 0


def test_joker_per_ortasi():
    tiles = [
        create_tile("y7", TileColor.YELLOW, 7),
        create_tile("b7", TileColor.BLUE, 7),
        joker1,
    ]
    result = SolverEngine.findBestArrangement(tiles, okey_meta)
    assert len(result.melds) == 1
    assert result.melds[0].type == MeldType.PER
    assert len(result.melds[0].tiles) == 3
    assert len(result.remainingTiles) == 0


def test_iki_joker_bir_normal_tas_per():
    yellow_thirteen_meta = OkeyMeta(color=TileColor.YELLOW, value=13)
    yjok1 = create_tile("yjok1", TileColor.YELLOW, 13)
    yjok2 = create_tile("yjok2", TileColor.YELLOW, 13)

    tiles = [
        create_tile("bk13", TileColor.BLACK, 13),
        yjok1,
        yjok2,
    ]
    result = SolverEngine.findBestArrangement(tiles, yellow_thirteen_meta)
    assert len(result.melds) == 1
    assert result.melds[0].type == MeldType.PER
    assert len(result.remainingTiles) == 0


def test_circular_seri_12_13_1():
    tiles = [
        create_tile("r12", TileColor.RED, 12),
        create_tile("r13", TileColor.RED, 13),
        create_tile("r1", TileColor.RED, 1),
    ]
    result = SolverEngine.findBestArrangement(tiles)
    assert len(result.melds) == 1
    assert result.melds[0].type == MeldType.SERI
    assert len(result.remainingTiles) == 0


def test_sahte_okey_seri():
    yellow_five_meta = OkeyMeta(color=TileColor.YELLOW, value=5)
    false_okey = create_tile("sahte_okey", TileColor.JOKER, 0)

    tiles = [
        create_tile("y3", TileColor.YELLOW, 3),
        create_tile("y4", TileColor.YELLOW, 4),
        false_okey,
    ]
    result = SolverEngine.findBestArrangement(tiles, yellow_five_meta)
    assert len(result.melds) == 1
    assert result.melds[0].type == MeldType.SERI
    assert len(result.remainingTiles) == 0


def test_find_best_pairs():
    tiles = [
        create_tile("r5_1", TileColor.RED, 5),
        create_tile("r5_2", TileColor.RED, 5),
        create_tile("b9_1", TileColor.BLUE, 9),
        create_tile("b9_2", TileColor.BLUE, 9),
        create_tile("y3", TileColor.YELLOW, 3),
    ]
    result = SolverEngine.findBestPairs(tiles)
    assert result["totalPairs"] == 2
    assert len(result["remainingTiles"]) == 1
    assert result["remainingTiles"][0].id == "y3"


def test_bridge_intersection_greedy_vs_optimal():
    tiles = [
        create_tile("r7", TileColor.RED, 7),
        create_tile("r8", TileColor.RED, 8),
        create_tile("r9", TileColor.RED, 9),
        create_tile("r10", TileColor.RED, 10),
        create_tile("b10", TileColor.BLUE, 10),
        create_tile("y10", TileColor.YELLOW, 10),
    ]
    result = SolverEngine.findBestArrangement(tiles)
    assert len(result.melds) == 2
    assert result.totalScore == 54
    assert len(result.remainingTiles) == 0


def test_solver_error_payload():
    from okey_solver.errors import OkeySolverError
    
    # Verify custom context payload in OkeySolverError
    payload = {"tile_id": "r5", "reason": "invalid value"}
    err = OkeySolverError("Error message", payload=payload)
    assert err.payload == payload
    assert str(err) == "Error message"


def test_solver_backtracking_memoization():
    # Construct a large hand with multiple potential melds to ensure backtracking solver with memoization evaluates correctly
    tiles = [
        create_tile("r1", TileColor.RED, 1),
        create_tile("r2", TileColor.RED, 2),
        create_tile("r3", TileColor.RED, 3),
        create_tile("b1", TileColor.BLUE, 1),
        create_tile("b2", TileColor.BLUE, 2),
        create_tile("b3", TileColor.BLUE, 3),
        create_tile("y1", TileColor.YELLOW, 1),
        create_tile("y2", TileColor.YELLOW, 2),
        create_tile("y3", TileColor.YELLOW, 3),
        create_tile("bk1", TileColor.BLACK, 1),
        create_tile("bk2", TileColor.BLACK, 2),
        create_tile("bk3", TileColor.BLACK, 3),
    ]
    result = SolverEngine.findBestArrangement(tiles)
    # The solver should find 4 SERI melds (RED 1-2-3, BLUE 1-2-3, YELLOW 1-2-3, BLACK 1-2-3)
    # Or 3 PER melds of size 4 (1-1-1-1, 2-2-2-2, 3-3-3-3).
    # Scores: 4 * 6 = 24 vs 3 * 24 = 24.
    assert result.totalScore == 24


def test_greedy_solver_strategy():
    engine = SolverEngine(strategy="greedy")
    tiles = [
        create_tile("r7", TileColor.RED, 7),
        create_tile("r8", TileColor.RED, 8),
        create_tile("r9", TileColor.RED, 9),
        create_tile("r10", TileColor.RED, 10),
        create_tile("b10", TileColor.BLUE, 10),
        create_tile("y10", TileColor.YELLOW, 10),
    ]
    result = engine.find_best_arrangement(tiles)
    # Greedy solver picks highest score first (r7-r8-r9-r10 -> score 34)
    # leaving r10 unavailable for the second meld (r10-b10-y10 -> score 30).
    assert result.totalScore == 34
    assert len(result.melds) == 1
    assert result.melds[0].tiles[0].id == "r7"


