import os
import random
import tempfile
import unittest

import cafe


class TestRequirements(unittest.TestCase):
    def test_R1_player_controls_barista_cat(self):
        inputs = iter(["Kiwi", "quit"])
        with tempfile.TemporaryDirectory() as d:
            state = cafe.play(lambda _: next(inputs), lambda *_: None,
                              random.Random(1), os.path.join(d, "s.jsonl"))
        self.assertEqual(state.barista.name, "Kiwi")

    def test_R2_generates_cat_customers_with_orders(self):
        rng = random.Random(0)
        for _ in range(20):
            c = cafe.generate_customer(rng)
            self.assertIn(c.cat.name, cafe.CAT_NAMES)
            self.assertIn(c.order, cafe.RECIPES)

    def test_R3_prepare_drink_from_ingredients(self):
        self.assertEqual(cafe.prepare_drink(["Espresso", " hot water "]),
                         frozenset({"espresso", "hot water"}))
        with self.assertRaises(ValueError):
            cafe.prepare_drink(["gravel"])
        with self.assertRaises(ValueError):
            cafe.prepare_drink([])

    def test_R4_compare_drink_to_request(self):
        self.assertTrue(cafe.drink_matches(frozenset({"espresso", "steamed milk"}), "latte"))
        self.assertFalse(cafe.drink_matches(frozenset({"espresso"}), "latte"))
        self.assertFalse(cafe.drink_matches(
            frozenset({"espresso", "steamed milk", "ice"}), "latte"))

    def test_R5_coins_only_when_correct(self):
        state = cafe.GameState(cafe.Cat("A"))
        cust = cafe.Customer(cafe.Cat("B"), "latte")
        self.assertEqual(cafe.serve(state, cust, frozenset({"espresso"})), 0)
        self.assertEqual(state.coins, 0)
        self.assertEqual(cafe.serve(state, cust, cafe.RECIPES["latte"]), cafe.REWARD)
        self.assertEqual(state.coins, cafe.REWARD)

    def test_R6_progress_saved_and_loaded(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "s.jsonl")
            self.assertIsNone(cafe.load_game(path))
            state = cafe.GameState(cafe.Cat("Kiwi"), coins=10, served=3, correct=2)
            cafe.save_game(state, path)
            state.coins = 15
            cafe.save_game(state, path)
            loaded = cafe.load_game(path)
            self.assertEqual((loaded.barista.name, loaded.coins, loaded.served, loaded.correct),
                             ("Kiwi", 15, 3, 2))
            with open(path, "a") as f:
                f.write("not json\n")
            self.assertIsNone(cafe.load_game(path))


if __name__ == "__main__":
    unittest.main()
