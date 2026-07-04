# okey_solver/rules.py
from typing import List, Optional
from okey_solver.types import Tile, MeldType, OkeyMeta

class OkeyRuleValidator:
    """
    Grubun geçerli bir "Per" (Aynı sayı, farklı renk) olup olmadığını kontrol eder.
    """
    def is_per(self, tiles: List[Tile], okey_meta: Optional[OkeyMeta] = None) -> bool:
        if len(tiles) < 3 or len(tiles) > 4:
            return False

        effective_tiles = self.get_effective_tiles(tiles, okey_meta)
        first_value = effective_tiles[0].value
        colors = set()

        for tile in effective_tiles:
            if tile.value != first_value:
                return False
            if tile.color in colors:
                return False
            colors.add(tile.color)

        return True

    """
    Grubun geçerli bir "Seri" (Aynı renk, ardışık sayı) olup olmadığını kontrol eder.
    """
    def is_seri(self, tiles: List[Tile], allow_one_after: bool = True, okey_meta: Optional[OkeyMeta] = None) -> bool:
        if len(tiles) < 3:
            return False

        effective_tiles = self.get_effective_tiles(tiles, okey_meta)
        sorted_tiles = sorted(effective_tiles, key=lambda t: t.value)
        first_color = sorted_tiles[0].color

        is_normal = True
        is_circular = True

        for i in range(len(sorted_tiles)):
            if sorted_tiles[i].color != first_color:
                return False

            if i > 0:
                if sorted_tiles[i].value != sorted_tiles[i - 1].value + 1:
                    is_normal = False
                if i > 1 and sorted_tiles[i].value != sorted_tiles[i - 1].value + 1:
                    is_circular = False

        if is_normal:
            return True

        if (
            allow_one_after
            and is_circular
            and sorted_tiles[0].value == 1
            and sorted_tiles[-1].value == 13
        ):
            return True

        return False

    """
    Taş grubunu analiz edip tipini döndürür.
    """
    def evaluate_group(self, tiles: List[Tile], okey_meta: Optional[OkeyMeta] = None) -> MeldType:
        if self.is_per(tiles, okey_meta):
            return MeldType.PER
        if self.is_seri(tiles, True, okey_meta):
            return MeldType.SERI
        if len(tiles) == 2 and self.is_tiles_same(tiles[0], tiles[1], okey_meta):
            return MeldType.CIFT
        return MeldType.INVALID

    """
    Taşlar aynı renk ve aynı değerde mi?
    """
    def is_tiles_same(self, tile_a: Tile, tile_b: Tile, okey_meta: Optional[OkeyMeta] = None) -> bool:
        eff_a = self.get_effective_tile(tile_a, okey_meta)
        eff_b = self.get_effective_tile(tile_b, okey_meta)
        return eff_a.value == eff_b.value and eff_a.color == eff_b.color

    """
    JOKER (Sahte Okey) taşını gerçek okey değerine dönüştürür.
    """
    def get_effective_tile(self, tile: Tile, okey_meta: Optional[OkeyMeta] = None) -> Tile:
        if not okey_meta:
            return tile

        if tile.color == 'JOKER':
            return Tile(id=tile.id, color=okey_meta.color, value=okey_meta.value)

        return tile

    def get_effective_tiles(self, tiles: List[Tile], okey_meta: Optional[OkeyMeta] = None) -> List[Tile]:
        return [self.get_effective_tile(t, okey_meta) for t in tiles]

class RuleValidator:
    _validator = OkeyRuleValidator()

    @classmethod
    def is_per(cls, tiles: List[Tile], okey_meta: Optional[OkeyMeta] = None) -> bool:
        return cls._validator.is_per(tiles, okey_meta)

    @classmethod
    def is_seri(cls, tiles: List[Tile], allow_one_after: bool = True, okey_meta: Optional[OkeyMeta] = None) -> bool:
        return cls._validator.is_seri(tiles, allow_one_after, okey_meta)

    @classmethod
    def evaluate_group(cls, tiles: List[Tile], okey_meta: Optional[OkeyMeta] = None) -> MeldType:
        return cls._validator.evaluate_group(tiles, okey_meta)

    @classmethod
    def is_tiles_same(cls, tile_a: Tile, tile_b: Tile, okey_meta: Optional[OkeyMeta] = None) -> bool:
        return cls._validator.is_tiles_same(tile_a, tile_b, okey_meta)

    @classmethod
    def get_effective_tile(cls, tile: Tile, okey_meta: Optional[OkeyMeta] = None) -> Tile:
        return cls._validator.get_effective_tile(tile, okey_meta)

    @classmethod
    def get_effective_tiles(cls, tiles: List[Tile], okey_meta: Optional[OkeyMeta] = None) -> List[Tile]:
        return cls._validator.get_effective_tiles(tiles, okey_meta)
