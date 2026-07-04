# okey_solver/pair_finder.py
from typing import List, Tuple, Dict, Any, Optional
from okey_solver.types import Tile, OkeyMeta, TileColor

class PairFinder:
    """
    Çifte Gitme: Eldeki taşlardan en fazla "özdeş çift" bulur.
    """
    def find_best_pairs(self, tiles: List[Tile], okey_meta: Optional[OkeyMeta] = None) -> Dict[str, Any]:
        resolved_tiles = self.resolve_false_okeys(tiles, okey_meta) if okey_meta else tiles
        
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

        pairs: List[Tuple[Tile, Tile]] = []
        used_ids = set()

        for i in range(len(normal_tiles)):
            if normal_tiles[i].id in used_ids:
                continue
            for j in range(i + 1, len(normal_tiles)):
                if normal_tiles[j].id in used_ids:
                    continue
                if (
                    normal_tiles[i].color == normal_tiles[j].color
                    and normal_tiles[i].value == normal_tiles[j].value
                ):
                    pairs.append((normal_tiles[i], normal_tiles[j]))
                    used_ids.add(normal_tiles[i].id)
                    used_ids.add(normal_tiles[j].id)
                    break

        wildcards_left = list(wildcards)
        for tile in normal_tiles:
            if tile.id in used_ids:
                continue
            if wildcards_left:
                wc = wildcards_left.pop(0)
                pairs.append((tile, wc))
                used_ids.add(tile.id)
                used_ids.add(wc.id)

        while len(wildcards_left) >= 2:
            wc1 = wildcards_left.pop(0)
            wc2 = wildcards_left.pop(0)
            pairs.append((wc1, wc2))
            used_ids.add(wc1.id)
            used_ids.add(wc2.id)

        remaining_tiles = [t for t in resolved_tiles if t.id not in used_ids]
        return {
            "pairs": pairs,
            "remainingTiles": remaining_tiles,
            "totalPairs": len(pairs)
        }

    def resolve_false_okeys(self, tiles: List[Tile], okey_meta: OkeyMeta) -> List[Tile]:
        resolved = []
        for t in tiles:
            if t.color == TileColor.JOKER:
                resolved.append(Tile(id=t.id, color=okey_meta.color, value=okey_meta.value))
            else:
                resolved.append(t)
        return resolved
