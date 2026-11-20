# 0001: Serve the browser game with Python's standard-library HTTP server

- Status: accepted (round 2, R7)

In the context of making the game run in a web browser from one command (R7) under the rule "Python, standard library only",
facing the choice between a stdlib `http.server` with a hand-written JSON API and single HTML page, a third-party framework such as Flask, or a static page with all logic in JavaScript,
we decided for the stdlib `http.server` (`ThreadingHTTPServer`) with game logic kept in `cafe.py`,
and neglected Flask (needs a dependency, forbidden without asking) and a JavaScript-only game (would move the logic out of `cafe.py` and out of reach of the Python tests, and break R6's server-side save file),
to achieve zero dependencies, a single `python cafe.py` command and fully testable logic,
accepting a more manual routing and request handling layer and a single shared game session per server,
because the standing rules require standard library only and testable logic in `cafe.py`.
