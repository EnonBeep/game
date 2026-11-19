# Standing rules

- Requirements live in `problem.md`; keep `spec.md` in sync with any requirement or design change.
- Python, standard library only. Do not add dependencies without asking.
- Game logic stays in `cafe.py`; keep it testable (no logic that needs a real terminal).
- Every requirement needs a test in `test_cafe.py` named `test_R<n>_...` matching its ID.
- Run `python -m unittest -v` and make sure all tests pass before finishing any change.
- Never commit save files (`*.jsonl`), `.venv/` or `__pycache__/`.
- Keep `README.md` accurate when run/test commands change.
- Ask the user about unclear requirements before writing code.
