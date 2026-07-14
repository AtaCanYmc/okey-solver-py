# okey_core/types.py
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class TileColor(str, Enum):
    RED = "RED"
    BLACK = "BLACK"
    BLUE = "BLUE"
    YELLOW = "YELLOW"
    JOKER = "JOKER"


class Tile(BaseModel):
    id: str  # e.g., "r_12_1"
    color: TileColor
    value: int  # 1-13. 0 for false okey/joker.


class MeldType(str, Enum):
    SERI = "SERI"
    PER = "PER"
    CIFT = "CIFT"
    INVALID = "INVALID"


class Meld(BaseModel):
    type: MeldType
    tiles: List[Tile]
    score: int


class OkeyMeta(BaseModel):
    color: TileColor
    value: int


class Arrangement(BaseModel):
    melds: List[Meld] = Field(default_factory=list)
    remainingTiles: List[Tile] = Field(default_factory=list)
    totalScore: int = 0


class OrchestratorResult(BaseModel):
    tiles: List[Tile]
    arrangement: Optional[Arrangement] = None

