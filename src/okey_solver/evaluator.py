# okey_solver/evaluator.py
from typing import List, Dict, Tuple, Any
from okey_core.types import Tile, TileColor, Arrangement


class DiscardEvaluator:
    """
    Evaluates the remaining tiles in an arrangement and calculates the probability
    (or connection strength) of each tile forming a meld, suggesting the best discard.
    """

    def __init__(self):
        # A standard Okey deck has 106 tiles: 2 sets of [RED, BLACK, BLUE, YELLOW] x [1..13] + 2 Jokers
        self.total_deck = self._initialize_standard_deck()

    def _initialize_standard_deck(self) -> Dict[Tuple[TileColor, int], int]:
        deck = {}
        for color in [TileColor.RED, TileColor.BLACK, TileColor.BLUE, TileColor.YELLOW]:
            for val in range(1, 14):
                deck[(color, val)] = 2
        # Jokers are special and usually not discarded, we represent them with value 0
        deck[(TileColor.JOKER, 0)] = 2
        return deck

    def evaluate_discards(
        self, hand: List[Tile], arrangement: Arrangement
    ) -> List[Dict[str, Any]]:
        """
        Calculates a 'meld_probability_score' for each tile in arrangement.remainingTiles.
        Returns a sorted list of dictionaries with discard recommendations (lowest score first).
        """
        remaining_tiles = arrangement.remainingTiles
        if not remaining_tiles:
            return []

        # Count copies of each tile color/value in the current hand
        hand_counts = {}
        for t in hand:
            key = (t.color, t.value)
            hand_counts[key] = hand_counts.get(key, 0) + 1

        # Calculate outstanding tiles (in deck/other players' hands)
        outstanding = {}
        for key, count in self.total_deck.items():
            outstanding[key] = max(0, count - hand_counts.get(key, 0))

        recommendations = []
        for t in remaining_tiles:
            if t.color == TileColor.JOKER or t.value == 0:
                # Jokers should never be discarded under normal circumstances
                recommendations.append(
                    {
                        "tile": t,
                        "score": float("inf"),
                        "explanation": "Joker wildcard tile; keep in hand.",
                    }
                )
                continue

            score = 0.0

            # --- 1. Run (Consecutive Series) Opportunities ---
            # A tile 'T' can belong to runs: (T-2, T-1, T), (T-1, T, T+1), (T, T+1, T+2)
            run_candidates = [
                ((t.color, t.value - 2), (t.color, t.value - 1)),
                ((t.color, t.value - 1), (t.color, t.value + 1)),
                ((t.color, t.value + 1), (t.color, t.value + 2)),
            ]
            for p1_key, p2_key in run_candidates:
                # Bound check values 1..13
                if not (1 <= p1_key[1] <= 13 and 1 <= p2_key[1] <= 13):
                    continue

                p1_in_hand = hand_counts.get(p1_key, 0) > 0
                p2_in_hand = hand_counts.get(p2_key, 0) > 0

                if p1_in_hand and p2_in_hand:
                    # Meld is already formed or ready
                    score += 5.0
                elif p1_in_hand:
                    # Needs p2
                    score += outstanding.get(p2_key, 0) * 1.5
                elif p2_in_hand:
                    # Needs p1
                    score += outstanding.get(p1_key, 0) * 1.5
                else:
                    # Needs both
                    score += (
                        outstanding.get(p1_key, 0) * outstanding.get(p2_key, 0) * 0.2
                    )

            # --- 2. Group (Same Value, Different Colors) Opportunities ---
            other_colors = [
                c
                for c in [
                    TileColor.RED,
                    TileColor.BLACK,
                    TileColor.BLUE,
                    TileColor.YELLOW,
                ]
                if c != t.color
            ]
            # Combination of other colors of same value
            group_pairs = [
                (other_colors[0], other_colors[1]),
                (other_colors[0], other_colors[2]),
                (other_colors[1], other_colors[2]),
            ]
            for c1, c2 in group_pairs:
                p1_key = (c1, t.value)
                p2_key = (c2, t.value)

                p1_in_hand = hand_counts.get(p1_key, 0) > 0
                p2_in_hand = hand_counts.get(p2_key, 0) > 0

                if p1_in_hand and p2_in_hand:
                    score += 4.0
                elif p1_in_hand:
                    score += outstanding.get(p2_key, 0) * 1.2
                elif p2_in_hand:
                    score += outstanding.get(p1_key, 0) * 1.2
                else:
                    score += (
                        outstanding.get(p1_key, 0) * outstanding.get(p2_key, 0) * 0.15
                    )

            recommendations.append(
                {
                    "tile": t,
                    "score": round(score, 3),
                    "explanation": f"Meld connectivity score: {round(score, 3)}",
                }
            )

        # Sort with lowest score first (least useful tile is the best candidate to discard)
        recommendations.sort(key=lambda x: x["score"])
        return recommendations
