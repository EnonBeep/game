# Handoff: end of round 3

Read first: `CLAUDE.md` (standing rules), `problem.md` (requirements), `spec.md` (design), `docs/decisions/` (0001, 0002), and this file. `handoff-round-2.md` is older background.

## Current state
Cozy Cat Cafe is a browser game for a cat barista, in Python (standard library only). All logic is in `cafe.py`; tests are in `test_cafe.py`. R1-R11 are implemented and all 20 tests pass.

- R1-R8: see `handoff-round-2.md` and `spec.md`.
- R9: ingredients are draggable tiles (HTML5 drag-and-drop); drop them on the cup. Drag only; no click-to-add; checkboxes removed.
- R10: the cup shows its ingredients (ordered, no repeats). "Start over" empties it.
- R11: Serve serves the cup's contents. The cup empties after serving.
- Round 3 commits (oldest first): `993b9c2` spec + problem.md, `7f70d63` tests, `9be0add` implementation + README, `438ab17` decision 0002.

## How to run and test
```
python cafe.py            # http://127.0.0.1:8000/ (next free port up to 8009), opens browser, Ctrl+C stops
python -m unittest -v     # all tests (R1-R6 TestRequirements, R7/R8 TestRound2, R9-R11 TestRound3)
```

## Code map (changes this round)
- `Game.cup` (list), `Game.add_to_cup(ingredient)`, `Game.clear_cup()`. `snapshot()` now includes `cup`.
- New routes in `Game._handle`: `POST /api/cup/add` `{"ingredient": name}`, `POST /api/cup/clear`. Both return the full snapshot.
- `POST /api/serve`: if the body has no `ingredients`, it serves `Game.cup`; an explicit list still works (kept so round 2 tests and API users are unchanged). `serve_drink` empties the cup once the selection is valid.
- `PAGE` (HTML string in `cafe.py`): `.tile` elements with `draggable="true"`, `#cup` drop zone with `dragover`/`drop` listeners, `#serve`, `#clear` ("Start over").

## Decisions this round, and why
Requested by the user (answers to my questions): R11 means serve the cup's contents; remove the checkboxes; repeats of an ingredient are ignored; drag only, no click-to-add.

Made by me, not requested:
- Cup is held on the server, not saved to `savegame.jsonl`, shared by all connections (record `0002`; only decision with a record).
- Add/clear routes as above; unknown or empty ingredient is a 400 and leaves the cup unchanged.
- Serve keeps accepting an explicit `ingredients` list.
- A wrong drink also empties the cup and brings the next customer; serving an empty cup is a 400 that keeps the customer and cup.
- Ingredients are lower-cased and trimmed on add. The page styling (pill tiles, dashed cup, wording) is my choice.
- Page tests are string checks (`id="cup"`, `draggable`, `addEventListener("drop"`, no `checkbox`, `id="serve"`, "Start over").
- `problem.md` was committed with the spec because it held the user's uncommitted Round 3 text.

## Unresolved / open
- Icons are still text and basic looking
- Lack of creativity in the visuals
- The page's JavaScript has never been run in a browser, by me in any round. `node` is not installed, so it was not even syntax-checked. Drag-and-drop, the drop highlight, Start over and Serve need a manual check.
- Drag-and-drop with a mouse only
- R11's wording was ambiguous ("serve the drink from the ingredients"); I asked and the user chose "serve the cup's contents". A drink-name preview in the cup was offered and not chosen.
- Earlier open items remain: `savegame.jsonl` grows forever; a corrupt last line makes the next game start fresh; no way to reset a save except deleting the file.
- No requirements exist beyond R11. The next round's will be in `problem.md` under a new heading. Check them for ambiguity and ask the user before coding.

## Warnings
- `savegame.jsonl` exists in the working directory (git-ignored). Running `python cafe.py` modifies it. Never commit it, `.venv/` or `__pycache__/`.
- Git prints LF/CRLF warnings (`core.autocrlf=true`). They are harmless; do not change git settings.
- Writing large Python files through a bash heredoc failed once in an earlier round; use the Write tool for big files. Small Python patch scripts via heredoc worked this round.
- Commit message trailer: end commits with the `Co-Authored-By` line given by the session's system reminder.
- This file and the two new `CLAUDE.md` lines are uncommitted, pending the user's review. Do not commit them unless asked. Never undo or amend a commit.
