# Spec: Cozy Cat Cafe

A short-session terminal game, written in Python (standard library only). All logic lives in `cafe.py`.

## How each requirement is met

| ID | Requirement | Design |
|----|-------------|--------|
| R1 | Player controls a cat barista | `play()` asks the player to name their barista `Cat`. The player acts through text commands (ingredient lists, `quit`). |
| R2 | Cat customers visit and order | `generate_customer(rng)` returns a `Customer` with a random cat name from `CAT_NAMES` and an order from `RECIPES`. `play()` generates a new one after each served drink. |
| R3 | Prepare drink by selecting ingredients | The player types comma-separated ingredients from `INGREDIENTS`. `prepare_drink()` normalizes them into a set and raises `ValueError` for empty or unknown input. |
| R4 | Compare drink to request | `drink_matches(drink, order)` is true only when the ingredient set equals the recipe in `RECIPES` exactly (no missing or extra ingredients). |
| R5 | Coins if correct, none if wrong | `serve()` adds `REWARD` (5) coins on a match and 0 otherwise. It updates `served` and `correct` counters. |
| R6 | Save progress locally | `save_game()` appends one JSON line (barista, coins, served, correct) to `savegame.jsonl` after every serve and on quit. `load_game()` reads the last valid line on startup, so progress persists. A missing, empty or corrupt file starts a new game. |

## Notes
- Sessions are short: the player quits whenever they like, and progress is saved.
- `play()` takes injectable `input_fn`, `print_fn`, `rng` and `path` so it can be tested without a terminal.
- Tests in `test_cafe.py` are named `test_R<n>_...` to match the requirement IDs.
