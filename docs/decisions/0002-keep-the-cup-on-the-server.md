# 0002: Keep the cup's contents on the server, not only in the page

- Status: accepted (round 3, R9-R11)

In the context of letting the player drag ingredients into a cup, show them, start over and serve (R9-R11),
facing the choice between holding the cup only in browser JavaScript and sending the final list on Serve, or holding it in `Game.cup` on the server with `POST /api/cup/add` and `POST /api/cup/clear`,
we decided for the server-side cup,
and neglected the browser-only cup (its add, no-repeat and start-over rules could not be tested by `python -m unittest`, which has no browser, and CLAUDE.md requires logic to stay in `cafe.py`),
to achieve testable cup rules and a cup that survives a page reload,
accepting an extra request per drag and a cup that is shared by all connections (and not saved to `savegame.jsonl`),
because the standing rules say game logic must stay testable without a browser.
