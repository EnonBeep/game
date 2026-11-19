# Cozy Cat Cafe

A short-session cozy game for the terminal. You are a cat barista. Cat customers visit and order drinks, and you make each drink by choosing ingredients. A correct drink earns 5 coins and a wrong one earns nothing. Your progress is saved to `savegame.jsonl` and restored when you reopen the game.

## Run

```
python cafe.py
```

Type ingredients separated by commas (for example `espresso, steamed milk`) to make a drink. Type `quit` to leave.

## Test

```
python -m unittest -v
```

Requires Python 3.8+ and no other packages.
