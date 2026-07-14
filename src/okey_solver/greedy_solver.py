# okey_solver/greedy_solver.py
from typing import List
from okey_solver.types import Tile, Meld, Arrangement


class GreedySolver:
    """
    Açgözlü (Greedy) arama kullanarak hızlıca çakışmasız bir dizilim bulur.
    En yüksek puanlı perlerden başlayarak havuzdaki taşları tüketir.
    Büyük taş grupları (kombinatorik patlama riski olan durumlar) için idealdir.
    """

    def solve(
        self, resolved_tiles: List[Tile], all_possible_melds: List[Meld]
    ) -> Arrangement:
        # Sort melds by score (highest score first)
        # In case of tie, prefer melds with fewer tiles (higher efficiency)
        sorted_melds = sorted(
            all_possible_melds,
            key=lambda m: (m.score, -len(m.tiles)),
            reverse=True,
        )

        chosen_melds: List[Meld] = []
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
        remaining_tiles = [t for t in resolved_tiles if t.id in available_ids]

        return Arrangement(
            melds=chosen_melds,
            remainingTiles=remaining_tiles,
            totalScore=total_score,
        )
