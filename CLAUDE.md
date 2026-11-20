# Standing rules

- Requirements live in `problem.md`; keep `spec.md` in sync with any requirement or design change.

- Python, standard library only. Do not add dependencies without asking.

-DO not use any paid services. 

- Game logic stays in `cafe.py`; keep it testable (no logic that needs a real terminal).

- Every requirement needs a test in `test_cafe.py` named `test_R<n>_...` matching its requiremnt ID.

- Run `python -m unittest -v` and make sure all tests pass before finishing any change to the code.

- Never commit save files (`*.jsonl`), `.venv/` or `__pycache__/`.

- Keep `README.md` accurate when run/test commands change.

- Ask the user about unclear requirements before writing code.

- Commit in small steps with messages saying what changed and why. Never undo or amend a commit.

- Record decisions that had real alternatives in `docs/decisions/` as Y-statements, numbered `0001`, `0002`, ... (next free number).

- Game logic must stay testable without a browser or network: `Game.handle()` is the HTTP API, and `cafe.py` must keep working with the standard library only.

- Handoff files (`handoff-round-N.md`) are written only when the user asks, and neither they nor CLAUDE.md changes are committed until the user has reviewed them.
- Do not write the next requirements ahead of time: the user adds each round's requirements to `problem.md`; read them there.
