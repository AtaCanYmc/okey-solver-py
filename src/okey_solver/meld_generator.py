# okey_solver/meld_generator.py
from typing import List, Optional, Dict
import itertools
from okey_solver.types import Tile, Meld, TileColor, MeldType, OkeyMeta
from okey_solver.rules import OkeyRuleValidator

ALL_COLORS = [TileColor.RED, TileColor.BLACK, TileColor.BLUE, TileColor.YELLOW]


class MeldGenerator:
    def __init__(self, validator: OkeyRuleValidator):
        self.validator = validator

    def generate_all_possible_melds(
        self,
        normal_tiles: List[Tile],
        wildcards: List[Tile],
        okey_meta: Optional[OkeyMeta] = None,
    ) -> List[Meld]:
        valid_melds: List[Meld] = []
        valid_melds.extend(self.generate_all_pers(normal_tiles, wildcards, okey_meta))
        valid_melds.extend(self.generate_all_seris(normal_tiles, wildcards, okey_meta))
        return valid_melds

    def generate_all_pers(
        self,
        normal_tiles: List[Tile],
        wildcards: List[Tile],
        okey_meta: Optional[OkeyMeta] = None,
    ) -> List[Meld]:
        melds: List[Meld] = []
        num_wildcards = len(wildcards)

        grouped_by_value: Dict[int, List[Tile]] = {}
        for tile in normal_tiles:
            grouped_by_value.setdefault(tile.value, []).append(tile)

        for value, group_tiles in grouped_by_value.items():
            colors: Dict[str, List[Tile]] = {}
            for t in group_tiles:
                colors.setdefault(t.color.value, []).append(t)

            available_colors = list(colors.keys())
            missing_colors = [
                c.value for c in ALL_COLORS if c.value not in available_colors
            ]

            if len(available_colors) >= 3:
                combinations3 = list(itertools.combinations(available_colors, 3))
                for combo in combinations3:
                    tile_options = [colors[color] for color in combo]
                    cartesian_tiles = list(itertools.product(*tile_options))

                    for tile_set in cartesian_tiles:
                        tile_set_list = list(tile_set)
                        meld_type = self.validator.evaluate_group(
                            tile_set_list, okey_meta
                        )
                        if meld_type == MeldType.PER:
                            score = sum(t.value for t in tile_set_list)
                            melds.append(
                                Meld(
                                    type=MeldType.PER, tiles=tile_set_list, score=score
                                )
                            )

                if len(available_colors) == 4:
                    tile_options = [colors[color] for color in available_colors]
                    cartesian_tiles = list(itertools.product(*tile_options))

                    for tile_set in cartesian_tiles:
                        tile_set_list = list(tile_set)
                        meld_type = self.validator.evaluate_group(
                            tile_set_list, okey_meta
                        )
                        if meld_type == MeldType.PER:
                            score = sum(t.value for t in tile_set_list)
                            melds.append(
                                Meld(
                                    type=MeldType.PER, tiles=tile_set_list, score=score
                                )
                            )

            if num_wildcards > 0:
                if len(available_colors) >= 2 and num_wildcards >= 1:
                    combinations2 = list(itertools.combinations(available_colors, 2))
                    for combo in combinations2:
                        used_colors = set(combo)
                        candidate_third_colors = [
                            c.value for c in ALL_COLORS if c.value not in used_colors
                        ]
                        if not candidate_third_colors:
                            continue

                        tile_options = [colors[c] for c in combo]
                        cartesian_tiles = list(itertools.product(*tile_options))

                        for tile_set in cartesian_tiles:
                            for wc_color in candidate_third_colors:
                                wc_tile = Tile(
                                    id=wildcards[0].id,
                                    color=TileColor(wc_color),
                                    value=value,
                                )
                                full_set = list(tile_set) + [wc_tile]
                                meld_type = self.validator.evaluate_group(
                                    full_set, okey_meta
                                )
                                if meld_type == MeldType.PER:
                                    score = sum(t.value for t in full_set)
                                    melds.append(
                                        Meld(
                                            type=MeldType.PER,
                                            tiles=full_set,
                                            score=score,
                                        )
                                    )

                if len(available_colors) >= 1 and num_wildcards >= 2:
                    for base_color in available_colors:
                        base_tiles = colors[base_color]
                        other_colors = [
                            c.value for c in ALL_COLORS if c.value != base_color
                        ]
                        color_pairs = list(itertools.combinations(other_colors, 2))

                        for color_pair in color_pairs:
                            for base_tile in base_tiles:
                                wc1 = Tile(
                                    id=wildcards[0].id,
                                    color=TileColor(color_pair[0]),
                                    value=value,
                                )
                                wc2 = Tile(
                                    id=wildcards[1].id,
                                    color=TileColor(color_pair[1]),
                                    value=value,
                                )
                                full_set = [base_tile, wc1, wc2]
                                meld_type = self.validator.evaluate_group(
                                    full_set, okey_meta
                                )
                                if meld_type == MeldType.PER:
                                    score = sum(t.value for t in full_set)
                                    melds.append(
                                        Meld(
                                            type=MeldType.PER,
                                            tiles=full_set,
                                            score=score,
                                        )
                                    )

                if len(available_colors) == 3 and num_wildcards >= 1:
                    missing_color = missing_colors[0]
                    tile_options = [colors[c] for c in available_colors]
                    cartesian_tiles = list(itertools.product(*tile_options))

                    for tile_set in cartesian_tiles:
                        wc_tile = Tile(
                            id=wildcards[0].id,
                            color=TileColor(missing_color),
                            value=value,
                        )
                        full_set = list(tile_set) + [wc_tile]
                        meld_type = self.validator.evaluate_group(full_set, okey_meta)
                        if meld_type == MeldType.PER:
                            score = sum(t.value for t in full_set)
                            melds.append(
                                Meld(type=MeldType.PER, tiles=full_set, score=score)
                            )

        return melds

    def generate_all_seris(
        self,
        normal_tiles: List[Tile],
        wildcards: List[Tile],
        okey_meta: Optional[OkeyMeta] = None,
    ) -> List[Meld]:
        melds: List[Meld] = []
        num_wildcards = len(wildcards)

        grouped_by_color: Dict[str, List[Tile]] = {}
        for tile in normal_tiles:
            grouped_by_color.setdefault(tile.color.value, []).append(tile)

        for color, group_tiles in grouped_by_color.items():
            value_map: Dict[int, List[Tile]] = {}
            for t in group_tiles:
                value_map.setdefault(t.value, []).append(t)

            circular_map = dict(value_map)
            if 1 in value_map:
                circular_map[14] = value_map[1]

            all_unique_values = sorted(list(circular_map.keys()))

            for i in range(len(all_unique_values)):
                start_val = all_unique_values[i]
                if start_val == 14:
                    continue

                self.generate_windowed_seris(
                    start_val,
                    color,
                    circular_map,
                    num_wildcards,
                    wildcards,
                    melds,
                    okey_meta,
                )

        return melds

    def generate_windowed_seris(
        self,
        start_val: int,
        color: str,
        circular_map: Dict[int, List[Tile]],
        max_wildcards: int,
        wildcards: List[Tile],
        melds: List[Meld],
        okey_meta: Optional[OkeyMeta] = None,
    ) -> None:
        def build_run(current_val: int, current_tiles: List[Tile], wildcards_used: int):
            if len(current_tiles) >= 3:
                normalized_set = []
                for t in current_tiles:
                    val = 1 if t.value == 14 else t.value
                    normalized_set.append(Tile(id=t.id, color=t.color, value=val))

                if (
                    self.validator.evaluate_group(normalized_set, okey_meta)
                    == MeldType.SERI
                ):
                    score = sum(t.value for t in normalized_set)
                    melds.append(
                        Meld(type=MeldType.SERI, tiles=normalized_set, score=score)
                    )

            if current_val > 14:
                return

            effective_val = 1 if current_val == 14 else current_val

            if current_val in circular_map:
                tiles = circular_map[current_val]
                for tile in tiles:
                    build_run(current_val + 1, current_tiles + [tile], wildcards_used)

            if wildcards_used < max_wildcards and wildcards_used < len(wildcards):
                wildcard_tile = Tile(
                    id=wildcards[wildcards_used].id,
                    color=TileColor(color),
                    value=effective_val,
                )
                build_run(
                    current_val + 1, current_tiles + [wildcard_tile], wildcards_used + 1
                )

        build_run(start_val, [], 0)
