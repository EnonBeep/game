# 0004: Round 4 changes R5 (wrong drinks cost a coin) and R9 (pictures in a takeaway cup)

- Status: accepted (round 4, R5 and R9)

In the context of the round 4 changes to the cafe game, where R5 let a wrong drink earn nothing and R9 listed ingredients by name,
facing the choice of keeping both requirements as they were or changing them,
we decided that R5 now takes 1 coin for a wrong drink (never below 0), and that R9 now shows ingredients as pictures that are dragged into a takeaway-style cup with a lid and sleeve,
and neglected keeping R5 as it was (a wrong drink had no consequence, so there was no reason to be careful), losing more than 1 coin per wrong drink (too harsh, and a small player could be stuck at 0 coins), and keeping text names for ingredients (names did not feel like making a real drink),
to achieve a game where careless serving has a cost and the drink looks and feels like a real one,
accepting that a wrong drink can now cost a player coins they earned, and that the pictures are simple and have to be drawn and kept up by hand (see 0003),
because the user asked for these changes in round 4 of `problem.md`.

## Tests changed because of this

R5:
- `test_R5_coins_only_when_correct` keeps its assertions, with a comment that a wrong drink with 0 coins stays at 0.
- New `test_R5_wrong_drink_loses_one_coin_but_never_below_zero`.
- New `test_R5_api_reports_coins_change`.

R9:
- `TestRound3` serve tests now put the lid on before serving, because serving from the cup needs the lid.
- New `test_R9_every_ingredient_has_an_svg_picture`.
- New `test_R9_page_draws_takeaway_cup_with_lid_and_sleeve`.
- New `test_R9_lid_closes_cup_with_ingredients`.
- New `test_R9_lid_on_empty_cup_is_rejected`.
- New `test_R9_cannot_add_ingredient_once_lid_is_on`.
- New `test_R9_start_over_removes_lid`.
- New `test_R9_cannot_serve_cup_without_lid`.
- New `test_R9_serving_removes_lid_and_empties_cup`.
