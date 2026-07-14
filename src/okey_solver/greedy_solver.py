# okey_solver/greedy_solver.py
from typing import List
from okey_core.types import Tile, Meld, Arrangement
from okey_solver.dto import LightTile, LightMeld


class GreedySolver:
    """
    Açgözlü (Greedy) arama kullanarak hızlıca çakışmasız bir dizilim bulur.
    En yüksek puanlı perlerden başlayarak havuzdaki taşları tüketir.
    Büyük taş grupları (kombinatorik patlama riski olan durumlar) için idealdir.
    """

    def solve(
        self, resolved_tiles: List[Tile], all_possible_melds: List[Meld]
    ) -> Arrangement:
        pydantic_tile_map = {t.id: t for t in resolved_tiles}

        # DTO Mapping
        light_melds = []
        for m in all_possible_melds:
            m_tiles = [LightTile(t.id, t.color, t.value) for t in m.tiles]
            light_melds.append(LightMeld(m.type, m_tiles, m.score))

        # Sort melds by score (highest score first)
        # In case of tie, prefer melds with fewer tiles (higher efficiency)
        sorted_melds = sorted(
            light_melds,
            key=lambda m: (m.score, -len(m.tiles)),
            reverse=True,
        )

        chosen_melds: List[LightMeld] = []
        available_ids = {t.id for t in resolved_tiles}
        total_score = 0

        for meld in sorted_melds:
            # Check if all tiles in the meld are still available
            if all(t.id in available_ids for t in meld.tiles):
                chosen_melds.append(meld)
                total_score += meld.score
                # Remove chosen tiles from availability
                for t in meld.tiles:
                    available_ids.remove(t.id)

        # Collect remaining unused tiles
        remaining_tiles = [pydantic_tile_map[tid] for tid in available_ids]

        best_melds = []
        for lm in chosen_melds:
            tiles_mapped = [pydantic_tile_map[lt.id] for lt in lm.tiles]
            best_melds.append(Meld(type=lm.type, tiles=tiles_mapped, score=lm.score))

        # Sort remaining tiles to match the original ordering
        original_id_order = {t.id: idx for idx, t in enumerate(resolved_tiles)}
        remaining_tiles.sort(key=lambda t: original_id_order[t.id])

        return Arrangement(
            melds=best_melds,
            remainingTiles=remaining_tiles,
            totalScore=total_score,
        )
