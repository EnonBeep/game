# Cozy Cat Cafe

A short-session cozy game that runs in your web browser. You are a cat barista. Cat customers visit and order drinks, and you make each drink by choosing ingredients. A correct drink earns 5 coins and a wrong one earns nothing. Your progress is saved to `savegame.jsonl` and restored when you reopen the game.

## Run

```
python cafe.py
```

This starts a local server (http://127.0.0.1:8000/, or the next free port up to 8009) and opens your browser. Name your barista, tick the ingredients for the customer's order and press Serve. The Menu panel on the right shows the recipe for every drink. Press Ctrl+C in the terminal to close the cafe; progress is saved after every drink.

## Test

```
python -m unittest -v
```

Requires Python 3.8+ and no other packages.
