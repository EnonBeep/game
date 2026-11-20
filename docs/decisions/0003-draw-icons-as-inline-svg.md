# 0003: Draw ingredient icons as original inline SVG in cafe.py

- Status: accepted (round 4, R9)

In the context of showing ingredients as pictures using free icons only (R9) in a standard-library, no-network game,
facing the choice between hand-drawn inline SVG kept in `cafe.py`, emoji characters, and copying an open-licensed icon set (e.g. Twemoji or Font Awesome Free) into the repository,
we decided for original inline SVG icons stored in `ICONS` and sent to the page in `GET /api/state`,
and neglected emoji (look differs per operating system and several ingredients, such as espresso, milk foam and tea leaves, have no good emoji) and a third-party icon set (needs license and attribution files and a way to serve static files),
to achieve consistent pictures with no downloads, no license obligations and no new files to serve,
accepting simple, basic-looking artwork that has to be drawn and maintained by hand,
because the user chose this option and the standing rules forbid dependencies and paid services.
