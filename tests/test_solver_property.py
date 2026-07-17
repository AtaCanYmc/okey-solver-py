# tests/test_solver_property.py
from hypothesis import strategies as st
from hypothesis import given, settings
from okey_core.types import Tile, TileColor, OkeyMeta
from okey_solver import create_standard_okey_solver

# Define a strategy to generate a single Tile
tile_strategy = st.builds(
    Tile,
    id=st.text(
        min_size=2,
        max_size=8,
        alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
    ),
    color=st.sampled_from(TileColor),
    value=st.integers(
        min_value=0, max_value=13
    ),  # 0 represents Joker, 1-13 standard values
)

# Define a strategy for OkeyMeta
okey_meta_strategy = st.one_of(
    st.none(),
    st.builds(
        OkeyMeta,
        color=st.sampled_from(TileColor),
        value=st.integers(min_value=1, max_value=13),
    ),
)


@given(
    tiles=st.lists(tile_strategy, min_size=0, max_size=22, unique_by=lambda t: t.id),
    okey_meta=okey_meta_strategy,
)
@settings(max_examples=250)
def test_solver_invariants(tiles, okey_meta):
    """
    Property-based test verifying that:
    1. The solver never raises uncaught exceptions for arbitrary tile inputs.
    2. The solver preserves all input tiles (remaining + melded == total).
    3. The total score remains non-negative.
    """
    solver = create_standard_okey_solver(strategy="backtracking")

    # Run solver
    arrangement = solver.find_best_arrangement(tiles, okey_meta)

    # Invariant 1: arrangement should always be returned
    assert arrangement is not None

    # Invariant 2: Total count of output tiles must match input tiles count
    output_tiles_count = len(arrangement.remainingTiles) + sum(
        len(m.tiles) for m in arrangement.melds
    )
    assert output_tiles_count == len(tiles), (
        f"Tile count mismatch: Input {len(tiles)} vs Output {output_tiles_count}"
    )

    # Invariant 3: Score is non-negative
    assert arrangement.totalScore >= 0
