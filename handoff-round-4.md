# Handoff: end of round 4

Read first: `CLAUDE.md` (standing rules), `problem.md` (requirements), `spec.md` (design), `docs/decisions/` (0001, 0002, 0003), and this file. `handoff-round-2.md` and `handoff-round-3.md` are older background.

## Current state
Cozy Cat Cafe is a browser game for a cat barista, in Python (standard library only). All logic is in `cafe.py`; tests are in `test_cafe.py`. R1-R11 are implemented (R5 and R9 were changed this round) and all 30 tests pass.

- R5 (changed): a correct drink earns 5 coins; a wrong drink loses 1 coin (`PENALTY`), never below 0.
- R9 (changed): ingredients are shown as pictures (original inline SVG, `ICONS` in `cafe.py`). The cup is an SVG takeaway cup with a lid and a brown sleeve (decoration only). The player drags the lid onto the cup, then presses Serve.
- R1-R4, R6-R8, R10, R11: unchanged, see `spec.md`.
- Round 4 commits (oldest first): `cab41ac` spec, `98fc555` tests, `54b92fe` implementation + README, `11c8f16` decision 0003.

## How to run and test
```
python cafe.py            # http://127.0.0.1:8000/ (next free port up to 8009), opens browser, Ctrl+C stops
python -m unittest -v     # all tests (TestRequirements R1-R6, TestRound2 R7/R8, TestRound3 R9-R11, TestRound4 R5/R9)
```

## Code map (changes this round)
- `PENALTY = 1`. `serve(state, customer, drink)` now returns the actual coin change: `+REWARD`, `-1`, or `0` (wrong drink at 0 coins).
- `ICONS`: dict of ingredient name to SVG string (built with `_svg()`); one per `INGREDIENTS` entry. A test checks the keys match.
- `Game.lid` (bool), `Game.put_lid_on()`, route `POST /api/cup/lid`. `snapshot()` now includes `lid` and `icons`.
- `add_to_cup` raises ValueError (400) when the lid is on. `put_lid_on` raises ValueError (400) on an empty cup. `clear_cup` and `serve_drink` set `lid = False`.
- `POST /api/serve`: with no `ingredients` in the body and a non-empty cup without the lid, returns 400 "Put the lid on the cup first." An explicit `ingredients` list ignores the lid rule (kept for API users and old tests). Response gained `coins_change`; `earned` is `max(change, 0)`; `correct` is true only when the change is `+REWARD`.
- `PAGE`: cup is `#cup` (drop zone) holding `#cupsvg` (with `#sleeve` and the hidden `#lidshape`) and `#cupitems`. The lid is a draggable `#lid` tile in `#lidtray` with `data-ing="__lid__"`. The drop handler sends `__lid__` to `/api/cup/lid`, anything else to `/api/cup/add`.

## Decisions this round, and why
Requested by the user (answers to my questions): icons are hand-drawn inline SVG; the lid is a draggable picture dropped on the cup; the API keeps `earned` and adds `coins_change`, and the message shows "-1 coin"; the sleeve is decoration only.

Made by me, not requested (only icon source has a record, `0003`):
- Lid on an empty cup, adding after the lid, and serving the cup without the lid are all 400 errors; Start over and Serve remove the lid.
- Explicit `ingredients` in `/api/serve` skips the lid rule.
- `serve()` returns the signed coin change instead of only the reward.
- Page wording: "Purrfect! +5 coins.", "Hiss... that was not a X. -1 coin.", "No coins lost (you had none)." The "-1 coin" text is hard-coded, not read from `PENALTY`.
- Cup contents appear as small icons inside the cup; the lid tile hides while the lid is on.
- `CLAUDE.md` was not changed this round; nothing seemed to be a new standing rule.

## Unresolved / open
- The page's JavaScript and the SVG artwork have never been run or seen in a browser, by me in any round. `node` is not installed. Layout of the cup (contents overlay position, lid shape, sleeve) is guessed from coordinates. Needs a manual check: drag ingredient, drag lid, Serve, Start over, wrong-drink message. 
    ^^ Checked by hand in Round 4 ALL works
- The SVG icons are basic. SVG markup was only checked for well-formed XML.
- Page tests are string checks (ids, `<svg`, `/api/cup/lid`, "-1 coin"), not behaviour tests.
- Drag-and-drop works with a mouse only (no touch or keyboard).
- Earlier open items remain: `savegame.jsonl` grows forever; a corrupt last line makes the next game start fresh; no way to reset a save except deleting the file; the cup and lid are not saved and are shared by all connections.
- No requirements exist beyond this round's. The next round's will be in `problem.md` under a new heading. Check them for ambiguity and ask the user before coding.

## Warnings
- `savegame.jsonl` exists in the working directory (git-ignored). Running `python cafe.py` modifies it. Never commit it, `.venv/` or `__pycache__/`.
- Git prints LF/CRLF warnings (`core.autocrlf=true`). They are harmless; do not change git settings.
- A large bash heredoc containing Python with many quotes failed this round (nothing was applied). Write patch scripts with the Write tool into the scratchpad and run them, or use Edit.
- Commit message trailer: end commits with the `Co-Authored-By` line given by the session's system reminder.
- This file is uncommitted, pending the user's review. Do not commit it unless asked. Never undo or amend a commit.
