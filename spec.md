# Spec: Cozy Cat Cafe

A short-session game played in a web browser, served locally by a Python program (standard library only). All logic lives in `cafe.py`. Round 2 replaced the terminal interface with a browser interface. Round 3 replaced the ingredient checkboxes with drag-and-drop into a cup.

## How each requirement is met

| ID | Requirement | Design |
|----|-------------|--------|
| R1 | Player controls a cat barista | The page asks the player to name their barista cat (`POST /api/name`, `Game.set_barista()`). The player acts by ticking ingredients and pressing Serve. |
| R2 | Cat customers visit and order | `generate_customer(rng)` returns a `Customer` with a random cat name from `CAT_NAMES` and an order from `RECIPES`. `Game` holds the current customer and generates a new one after each served drink. |
| R3 | Prepare drink by selecting ingredients | The player ticks ingredient checkboxes (from `INGREDIENTS`); the page sends them to `POST /api/serve`. `prepare_drink()` normalizes them into a set and raises `ValueError` for empty or unknown input. |
| R4 | Compare drink to request | `drink_matches(drink, order)` is true only when the ingredient set equals the recipe in `RECIPES` exactly (no missing or extra ingredients). |
| R5 | Coins if correct, none if wrong | `serve()` adds `REWARD` (5) coins on a match and 0 otherwise. It updates `served` and `correct` counters. |
| R6 | Save progress locally | `save_game()` appends one JSON line (barista, coins, served, correct) to `savegame.jsonl` after every serve and when the barista is named. `load_game()` reads the last valid line on startup, so progress persists. A missing, empty or corrupt file starts a new game. |
| R7 | Runs in a web browser, served locally with one command | `python cafe.py` calls `main()`, which starts an `http.server.ThreadingHTTPServer` bound to `127.0.0.1` (port 8000, or the next free port) and opens the default browser. `Game.handle(method, path, body)` is the whole HTTP API and is socket-free so it is testable. Routes: `GET /` (page), `GET /api/state`, `POST /api/name`, `POST /api/serve`, plus `POST /api/cup/add` and `POST /api/cup/clear` (round 3). The terminal interface (`play()`) is removed. |
| R8 | Menu with the recipe for each drink | `menu()` returns every drink in `RECIPES` with its ingredients, sorted by name. It is included in `GET /api/state` and rendered by the page as an always-visible side panel. |
| R9 | Make the drink by dragging ingredients into a cup | The page shows each ingredient as a draggable tile (HTML5 drag-and-drop) and a cup drop zone. Dropping a tile on the cup calls `POST /api/cup/add` with `{"ingredient": name}`. Drag only: no click-to-add and no checkboxes (the checkboxes from R3 are removed). |
| R10 | Cup shows its ingredients; can start over | The cup is held server-side in `Game.cup` (an ordered list, no repeats) and is part of `GET /api/state` as `cup`. `Game.add_to_cup()` validates through `prepare_drink` rules (unknown ingredient is an error 400) and ignores an ingredient already in the cup. `POST /api/cup/clear` empties it ("Start over" button). The page renders the cup contents from state. |
| R11 | Serve the drink made from the cup's ingredients | The Serve button calls `POST /api/serve` with no body ingredients; the server serves `Game.cup` through the existing R3-R6 path (empty cup is a 400 error and keeps the customer). The cup is emptied after a successful serve. A body with an explicit `ingredients` list is still accepted, as in round 2. |

## Notes
- Sessions are short: the player quits (by closing tab or control C in terminal) whenever they like, and progress is saved.
- `Game` takes injectable `rng` and `path`, and `Game.handle()` takes plain values, so logic is tested without a browser or network.
- Saving stays server-side in `savegame.jsonl` with the same format, so earlier saves still load.
- The server is single-player and keeps one `Game` shared by all connections.
- Tests in `test_cafe.py` are named `test_R<n>_...` to match the requirement IDs.
- The cup lives on the server so drag-and-drop state is testable without a browser; it is not saved to `savegame.jsonl` (a new session starts with an empty cup).
