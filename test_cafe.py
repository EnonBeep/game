import json
import os
import random
import tempfile
import threading
import unittest
import urllib.request

import cafe


class TestRequirements(unittest.TestCase):
    def test_R1_player_controls_barista_cat(self):
        with tempfile.TemporaryDirectory() as d:
            game = cafe.Game(random.Random(1), os.path.join(d, "s.jsonl"))
            status, _, body = game.handle("POST", "/api/name", {"name": "Kiwi"})
            self.assertEqual(status, 200)
            self.assertEqual(body["barista"], "Kiwi")
            # the player acts by serving drinks
            status, _, body = game.handle("POST", "/api/serve", {"ingredients": ["espresso"]})
            self.assertEqual(status, 200)
            self.assertEqual(body["state"]["served"], 1)

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


class TestRound2(unittest.TestCase):
    def make_game(self, d):
        return cafe.Game(random.Random(2), os.path.join(d, "s.jsonl"))

    def test_R7_http_api_without_sockets(self):
        with tempfile.TemporaryDirectory() as d:
            game = self.make_game(d)
            status, ctype, body = game.handle("GET", "/", None)
            self.assertEqual((status, ctype), (200, "text/html; charset=utf-8"))
            self.assertIn("<html", body.lower())
            status, _, st = game.handle("GET", "/api/state", None)
            self.assertEqual(status, 200)
            self.assertIn(st["customer"]["order"], cafe.RECIPES)
            self.assertEqual(game.handle("GET", "/nope", None)[0], 404)
            self.assertEqual(game.handle("POST", "/api/serve", {"ingredients": ["gravel"]})[0], 400)
            self.assertEqual(game.handle("POST", "/api/serve", {"ingredients": []})[0], 400)

    def test_R7_correct_drink_over_api_pays_and_saves(self):
        with tempfile.TemporaryDirectory() as d:
            game = self.make_game(d)
            game.handle("POST", "/api/name", {"name": "Kiwi"})
            order = game.handle("GET", "/api/state", None)[2]["customer"]["order"]
            _, _, body = game.handle("POST", "/api/serve",
                                     {"ingredients": sorted(cafe.RECIPES[order])})
            self.assertTrue(body["correct"])
            self.assertEqual(body["state"]["coins"], cafe.REWARD)
            # a new game on the same file resumes the save (R6 through the web layer)
            again = cafe.Game(random.Random(3), os.path.join(d, "s.jsonl"))
            st = again.handle("GET", "/api/state", None)[2]
            self.assertEqual((st["barista"], st["coins"]), ("Kiwi", cafe.REWARD))

    def test_R7_one_command_serves_over_http(self):
        with tempfile.TemporaryDirectory() as d:
            server = cafe.make_server(cafe.Game(random.Random(4), os.path.join(d, "s.jsonl")), port=0)
            host, port = server.server_address
            self.assertEqual(host, "127.0.0.1")
            t = threading.Thread(target=server.serve_forever, daemon=True)
            t.start()
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/state") as r:
                    self.assertEqual(r.status, 200)
                    self.assertIn("menu", json.loads(r.read()))
                req = urllib.request.Request(
                    f"http://127.0.0.1:{port}/api/name", data=json.dumps({"name": "Pip"}).encode(),
                    headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req) as r:
                    self.assertEqual(json.loads(r.read())["barista"], "Pip")
            finally:
                server.shutdown()
                server.server_close()

    def test_R8_menu_lists_every_recipe(self):
        menu = cafe.menu()
        self.assertEqual([m["name"] for m in menu], sorted(cafe.RECIPES))
        for m in menu:
            self.assertEqual(set(m["ingredients"]), set(cafe.RECIPES[m["name"]]))

    def test_R8_menu_is_in_state_and_page(self):
        with tempfile.TemporaryDirectory() as d:
            game = self.make_game(d)
            st = game.handle("GET", "/api/state", None)[2]
            self.assertEqual(st["menu"], cafe.menu())
            page = game.handle("GET", "/", None)[2]
            self.assertIn('id="menu"', page)


if __name__ == "__main__":
    unittest.main()
