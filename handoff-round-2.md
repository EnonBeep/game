# Handoff: end of round 2

Read first: `CLAUDE.md` (standing rules), `problem.md` (requirements), `spec.md` (design), `docs/decisions/`.

## Current state
Cozy Cat Cafe is a browser game for a cat barista, written in Python (standard library only). All logic is in `cafe.py`; tests are in `test_cafe.py`.

- R1-R6 (round 1): barista cat, cat customers with orders, ingredient selection, drink comparison, 5 coins for a correct drink, save/load.
- R7 (round 2): `python cafe.py` starts an `http.server` on 127.0.0.1 and opens the browser.
- R8 (round 2): a Menu panel, always visible, lists every recipe.
- The terminal interface (`play()`) was removed in round 2.
- All 11 tests pass. Round 2 commits (oldest first): `79c23a3` spec, `d774ff6` tests, `7a05e4e` implementation, `38d63c2` README + decision 0001.
- `CLAUDE.md` has three new rules and this file is new. Both were uncommitted when written, pending the user's review.

## How to run and test
```
python cafe.py            # serves http://127.0.0.1:8000/ (or next free port up to 8009), opens browser, Ctrl+C to stop
python -m unittest -v     # all tests
```

## Code map (`cafe.py`)
- Data: `INGREDIENTS`, `RECIPES` (drink -> frozenset), `CAT_NAMES`, `REWARD = 5`.
- Pure functions: `generate_customer`, `prepare_drink`, `drink_matches`, `serve`, `save_game`, `load_game`, `menu`.
- `Game(rng, path)`: holds state and the current customer. `Game.handle(method, path, body)` returns `(status, content_type, payload)` and is the entire API: `GET /`, `GET /api/state`, `POST /api/name`, `POST /api/serve`. A lock serializes calls.
- `make_handler` / `make_server(game, port)` / `main()`: thin socket layer. The page (`PAGE`) is an HTML string in `cafe.py`.
- Tests: R1-R6 in `TestRequirements`; R7/R8 in `TestRound2`. `make_server(..., port=0)` gives a free port for tests.

## Decisions this round, and why
Requested by the user: replace the terminal game; `python cafe.py` also opens the browser; menu is an always-visible panel; keep `savegame.jsonl` and its format (old saves still load).

Made by me, not requested:
- Stdlib `http.server` rather than Flask or a JS-only game (see `docs/decisions/0001-...`). This is the only decision with a record.
- One shared `Game` per server (single player); bind to 127.0.0.1 only; port 8000 with fallback to 8009.
- Ingredients are chosen with checkboxes. Serving before naming the barista returns 400.
- Names are trimmed to 30 chars, default "Barista"; an existing save skips the naming step.
- An invalid selection (nothing ticked) returns an error and keeps the same customer; a wrong but valid drink counts as served and brings the next customer. (The old terminal game made the customer wander off on invalid input.)
- Saves happen on naming and after every serve, but not on exit (there is no quit command).
- Request logging is off. The page escapes text it inserts as HTML.

## Unresolved / open
- The page's JavaScript was never run in a real browser by me; only the API and a real HTTP server are tested. Check the UI by hand (naming, serving, menu, resume after restart).
- Round 1's `play()` tests and terminal behaviour are gone; the user confirmed replacing the terminal, but there is no way to reset a save other than deleting `savegame.jsonl`.
- `savegame.jsonl` is append-only and grows forever (existing design; `load_game` reads the last valid line).
- A corrupt last line makes `load_game` return None, so the player would start a new game and the next save appends after the bad line.
- Only requirement IDs R1-R8 exist; the next round's requirements will be in `problem.md` under a new heading. Check them for ambiguity and ask the user before coding.

## Warnings
- `savegame.jsonl` exists in the working directory (ignored by git). Tests use temp files, but running `python cafe.py` modifies it. Never commit it.
- `__pycache__/` exists; it is ignored.
- Git prints LF/CRLF warnings on this Windows machine (`core.autocrlf=true`). They are harmless; do not change git settings without asking.
- Writing large Python files through a bash heredoc failed once in this environment; use the Write tool for big files.
- The user wants the handoff file and `CLAUDE.md` changes reviewed before they are committed; do not commit either unless asked.
- Never undo or amend a commit.
