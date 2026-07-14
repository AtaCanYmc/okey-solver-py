# okey_solver/dto.py
from typing import Any, List


class LightTile:
    __slots__ = ("id", "color", "value")

    def __init__(self, id: str, color: Any, value: int):
        self.id = id
        self.color = color
        self.value = value


class LightMeld:
    __slots__ = ("type", "tiles", "score")

    def __init__(self, type: Any, tiles: List[LightTile], score: int):
        self.type = type
        self.tiles = tiles
        self.score = score
