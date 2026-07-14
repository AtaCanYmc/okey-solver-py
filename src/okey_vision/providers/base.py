import re
import difflib
from typing import Dict, Protocol
from okey_vision.types import Detection
from okey_core.types import Tile, TileColor
from okey_core.errors import InvalidTileError

DEFAULT_COLOR_ALIASES = {
    "RED": TileColor.RED,
    "R": TileColor.RED,
    "KIRMIZI": TileColor.RED,
    "BLACK": TileColor.BLACK,
    "B": TileColor.BLACK,
    "SIYAH": TileColor.BLACK,
    "BLUE": TileColor.BLUE,
    "MAVI": TileColor.BLUE,
    "YELLOW": TileColor.YELLOW,
    "ORANGE": TileColor.YELLOW,
    "Y": TileColor.YELLOW,
    "SARI": TileColor.YELLOW,
}


class LabelParserStrategy(Protocol):
    def parse_tile(
        self, detection: Detection, index: int, color_aliases: Dict[str, TileColor]
    ) -> Tile:
        """
        Parses a Detection label into a Tile object.
        """
        ...


class FuzzyLabelParser:
    """
    Default parser implementing fuzzy label matching and OCR confusion translation.
    """

    def parse_tile(
        self, detection: Detection, index: int, color_aliases: Dict[str, TileColor]
    ) -> Tile:
        raw_label = detection.label
        if not raw_label:
            raise InvalidTileError(
                f"Detection {detection.id or index} does not contain a class label.",
                payload={"detection_id": detection.id or str(index)}
            )

        normalized = raw_label.strip().upper()
        if "JOKER" in normalized:
            return Tile(id=detection.id, color=TileColor.JOKER, value=0)

        # 1. Match color key by finding exact matches of aliases in the string
        matched_color_key = None
        parts = [p for p in re.split(r'[\s\-_]+', normalized) if p]
        for key in sorted(color_aliases.keys(), key=len, reverse=True):
            if len(key) <= 2:
                if key in parts:
                    matched_color_key = key
                    break
            else:
                if key in normalized:
                    matched_color_key = key
                    break

        # 2. Extract value part
        if matched_color_key:
            value_part = normalized.replace(matched_color_key, "")
        else:
            # Try to find a part that fuzzy matches a color alias
            matched_part = None
            for part in parts:
                letters_only = "".join(c for c in part if c.isalpha() or c in "ÇĞİÖŞÜ")
                matches = difflib.get_close_matches(letters_only, list(color_aliases.keys()), n=1, cutoff=0.5)
                if matches:
                    matched_color_key = matches[0]
                    matched_part = part
                    break

            if matched_color_key and matched_part:
                # Reconstruct value part by removing the matched part
                value_part = "".join(p for p in parts if p != matched_part)
            else:
                # Fallback if no separators: split letters and digits
                letters = "".join(c for c in normalized if c.isalpha() or c in "ÇĞİÖŞÜ")
                matches = difflib.get_close_matches(letters, list(color_aliases.keys()), n=1, cutoff=0.5)
                if matches:
                    matched_color_key = matches[0]
                    value_part = "".join(c for c in normalized if c.isdigit())
                else:
                    raise InvalidTileError(
                        f'Unsupported or unrecognized tile color/label "{raw_label}" on detection {detection.id or index}.',
                        payload={"detection_id": detection.id or str(index), "label": raw_label}
                    )

        color = color_aliases[matched_color_key]

        # Clean the value part
        value_part = "".join(c for c in value_part if c.isalnum())

        # OCR Digit Confusions translation
        confusion_map = {
            'S': '5',
            'O': '0',
            'I': '1',
            'L': '1',
            'Z': '2',
            'G': '6',
            'B': '8'
        }
        digits_cleaned = "".join(confusion_map.get(c, c) for c in value_part if c.isdigit() or c in confusion_map)

        if not digits_cleaned.isdigit():
            raise InvalidTileError(
                f'No valid numeric value found in label "{raw_label}" on detection {detection.id or index}.',
                payload={"detection_id": detection.id or str(index), "label": raw_label}
            )

        value = int(digits_cleaned)
        if value < 1 or value > 13:
            raise InvalidTileError(
                f'Unsupported tile value "{value}" on detection {detection.id or index}.',
                payload={"detection_id": detection.id or str(index), "label": raw_label, "parsed_value": value}
            )

        return Tile(id=detection.id, color=color, value=value)


# Legacy function wrapper for backwards compatibility
def parse_default_tile(
    detection: Detection, index: int, color_aliases: Dict[str, TileColor]
) -> Tile:
    return FuzzyLabelParser().parse_tile(detection, index, color_aliases)
