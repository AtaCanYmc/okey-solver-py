# Algorithm and Okey Game Rules

This document outlines the rules and algorithmic considerations ported from `okey-solver-ts`.

## Melds (Seri and Per)
- **Per**: 3 or 4 tiles of the same value but different colors (e.g. Red 5, Blue 5, Yellow 5).
- **Seri**: 3 or more consecutive tiles of the same color (e.g. Red 4, Red 5, Red 6).

## Circular Runs (12-13-1)
- Wrap-around sequences like `12 -> 13 -> 1` are supported.
- `1` can only follow `13` (e.g. `11-12-13-1` is valid; `13-1-2` is invalid).

## Joker (Okey Tile)
- Evaluated as a wildcard which replaces any missing tile in a Seri or Per.

## Sahte Okey
- Resolves automatically to the actual Okey's representation.
