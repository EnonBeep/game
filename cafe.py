"""Cozy Cat Cafe: a short-session browser game where you are a cat barista."""
import json
import os
import random
import threading
import webbrowser
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SAVE_FILE = "savegame.jsonl"
REWARD = 5

INGREDIENTS = ["espresso", "hot water", "steamed milk", "milk foam", "chocolate", "tea leaves", "honey", "ice"]

RECIPES = {
    "espresso": frozenset({"espresso"}),
    "americano": frozenset({"espresso", "hot water"}),
    "latte": frozenset({"espresso", "steamed milk"}),
    "cappuccino": frozenset({"espresso", "steamed milk", "milk foam"}),
    "mocha": frozenset({"espresso", "steamed milk", "chocolate"}),
    "hot tea": frozenset({"tea leaves", "hot water"}),
    "honey tea": frozenset({"tea leaves", "hot water", "honey"}),
    "iced latte": frozenset({"espresso", "steamed milk", "ice"}),
}

CAT_NAMES = ["Whiskers", "Mochi", "Luna", "Biscuit", "Pumpkin", "Miso", "Shadow", "Ginger", "Pebbles", "Tofu"]


@dataclass
class Cat:
    """A cat: the player's barista or a customer."""
    name: str


@dataclass
class Customer:
    cat: Cat
    order: str  # key of RECIPES


@dataclass
class GameState:
    barista: Cat
    coins: int = 0
    served: int = 0
    correct: int = 0


def generate_customer(rng=random):
    """R2: create a cat customer who wants a random drink."""
    return Customer(Cat(rng.choice(CAT_NAMES)), rng.choice(sorted(RECIPES)))


def prepare_drink(selected):
    """R3: build a drink from the ingredients the player selected.

    Raises ValueError for unknown or empty selections.
    """
    chosen = frozenset(i.strip().lower() for i in selected)
    if not chosen:
        raise ValueError("Pick at least one ingredient.")
    unknown = chosen - set(INGREDIENTS)
    if unknown:
        raise ValueError("Unknown ingredient: " + ", ".join(sorted(unknown)))
    return chosen


def drink_matches(drink, order):
    """R4: compare the prepared drink with the customer's request."""
    return frozenset(drink) == RECIPES[order]


def serve(state, customer, drink):
    """R5: pay coins only when the drink is correct. Returns coins earned."""
    state.served += 1
    if drink_matches(drink, customer.order):
        state.correct += 1
        state.coins += REWARD
        return REWARD
    return 0


def save_game(state, path=SAVE_FILE):
    """R6: append the current progress as one JSON line."""
    record = {"barista": state.barista.name, "coins": state.coins,
              "served": state.served, "correct": state.correct}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def load_game(path=SAVE_FILE):
    """R6: return the most recent saved state, or None if there is no usable save."""
    if not os.path.exists(path):
        return None
    last = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                last = line
    if last is None:
        return None
    try:
        d = json.loads(last)
        return GameState(Cat(d["barista"]), int(d["coins"]), int(d["served"]), int(d["correct"]))
    except (ValueError, KeyError, TypeError):
        return None


def menu():
    """R8: every drink with its ingredients, sorted by drink name."""
    return [{"name": n, "ingredients": sorted(RECIPES[n])} for n in sorted(RECIPES)]


class Game:
    """One cafe session. `handle` is the whole HTTP API, free of sockets (R7)."""

    def __init__(self, rng=random, path=SAVE_FILE):
        self.rng = rng
        self.path = path
        self.state = load_game(path)  # None until the barista is named
        self.customer = generate_customer(rng)
        self.lock = threading.Lock()

    def snapshot(self):
        s = self.state
        return {
            "barista": s.barista.name if s else None,
            "coins": s.coins if s else 0,
            "served": s.served if s else 0,
            "correct": s.correct if s else 0,
            "customer": {"name": self.customer.cat.name, "order": self.customer.order},
            "ingredients": INGREDIENTS,
            "menu": menu(),
        }

    def set_barista(self, name):
        """R1: name the barista cat (keeps progress if a save exists)."""
        name = str(name or "").strip()[:30] or "Barista"
        if self.state:
            self.state.barista.name = name
        else:
            self.state = GameState(Cat(name))
        save_game(self.state, self.path)

    def serve_drink(self, ingredients):
        """R3-R6: prepare, compare, pay, save, then bring the next customer."""
        drink = prepare_drink(ingredients)
        customer = self.customer
        earned = serve(self.state, customer, drink)
        save_game(self.state, self.path)
        self.customer = generate_customer(self.rng)
        return customer, earned

    def handle(self, method, path, body):
        """Return (status, content_type, payload). `body` is a parsed JSON dict or None."""
        with self.lock:
            return self._handle(method, path, body)

    def _handle(self, method, path, body):
        body = body or {}
        if method == "GET" and path == "/":
            return 200, "text/html; charset=utf-8", PAGE
        if method == "GET" and path == "/api/state":
            return 200, "application/json", self.snapshot()
        if method == "POST" and path == "/api/name":
            self.set_barista(body.get("name"))
            return 200, "application/json", self.snapshot()
        if method == "POST" and path == "/api/serve":
            if not self.state:
                return 400, "application/json", {"error": "Name your barista first."}
            try:
                ingredients = body.get("ingredients", [])
                if not isinstance(ingredients, list):
                    raise ValueError("ingredients must be a list.")
                customer, earned = self.serve_drink([str(i) for i in ingredients])
            except ValueError as e:
                return 400, "application/json", {"error": str(e)}
            return 200, "application/json", {
                "correct": earned > 0, "earned": earned,
                "served_to": customer.cat.name, "order": customer.order,
                "state": self.snapshot()}
        return 404, "application/json", {"error": "Not found"}


def make_handler(game):
    class Handler(BaseHTTPRequestHandler):
        def _respond(self, status, ctype, payload):
            if isinstance(payload, str):
                data = payload.encode("utf-8")
            else:
                data = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            self._respond(*game.handle("GET", self.path.split("?")[0], None))

        def do_POST(self):
            try:
                length = int(self.headers.get("Content-Length") or 0)
                body = json.loads(self.rfile.read(length) or b"{}")
                if not isinstance(body, dict):
                    raise ValueError
            except ValueError:
                return self._respond(400, "application/json", {"error": "Bad request body."})
            self._respond(*game.handle("POST", self.path.split("?")[0], body))

        def log_message(self, *args):
            pass

    return Handler


def make_server(game, port=8000):
    """R7: an HTTP server reachable from this computer only (127.0.0.1)."""
    server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(game))
    server.daemon_threads = True
    return server


def main():
    """R7: the one command. Serves the game and opens the browser."""
    game = Game()
    server = None
    for port in range(8000, 8010):
        try:
            server = make_server(game, port)
            break
        except OSError:
            continue
    if server is None:
        raise SystemExit("Could not find a free port between 8000 and 8009.")
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    print(f"Cozy Cat Cafe is open at {url}  (press Ctrl+C to close)")
    threading.Timer(0.5, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSee you soon!")
    finally:
        server.server_close()


PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Cozy Cat Cafe</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:system-ui,sans-serif;background:#fdf3e7;color:#4a3426;margin:0;display:flex;gap:1.5rem;padding:1.5rem;flex-wrap:wrap}
main{flex:2;min-width:280px}
aside{flex:1;min-width:220px;background:#fff;border-radius:12px;padding:1rem;box-shadow:0 2px 6px #0002;align-self:flex-start}
h1{margin-top:0}label{display:block;margin:.3rem 0}
button{padding:.5rem 1rem;font-size:1rem;border-radius:8px;border:0;background:#d98c5f;color:#fff;cursor:pointer}
#msg{min-height:1.5rem;font-weight:bold}#menu{padding-left:1.2rem}#menu li{margin-bottom:.5rem}
</style></head><body>
<main>
<h1>&#128049; Cozy Cat Cafe</h1>
<div id="namebox" hidden><p>Name your barista cat:</p><input id="name" maxlength="30"> <button id="go">Open the cafe</button></div>
<div id="game" hidden>
<p id="stats"></p>
<h2 id="order"></h2>
<form id="form"><div id="ings"></div><p><button>Serve</button></p></form>
</div>
<p id="msg" aria-live="polite"></p>
</main>
<aside id="menu-panel"><h2>Menu</h2><ul id="menu"></ul></aside>
<script>
const $=id=>document.getElementById(id);
const esc=t=>String(t).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
async function api(path,body){
  const r=await fetch(path,body?{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)}:undefined);
  return [r.ok,await r.json()];
}
function show(s){
  $("menu").innerHTML=s.menu.map(m=>"<li><b>"+esc(m.name)+"</b><br>"+esc(m.ingredients.join(", "))+"</li>").join("");
  $("namebox").hidden=!!s.barista;$("game").hidden=!s.barista;
  if(!s.barista)return;
  $("stats").textContent=s.barista+" | Coins: "+s.coins+" | Served: "+s.served+" | Correct: "+s.correct;
  $("order").textContent=s.customer.name+" the cat orders a "+s.customer.order+".";
  $("ings").innerHTML=s.ingredients.map(i=>'<label><input type="checkbox" value="'+esc(i)+'"> '+esc(i)+"</label>").join("");
}
$("go").onclick=async()=>show((await api("/api/name",{name:$("name").value}))[1]);
$("form").onsubmit=async e=>{
  e.preventDefault();
  const ing=[...document.querySelectorAll("#ings input:checked")].map(c=>c.value);
  const [ok,d]=await api("/api/serve",{ingredients:ing});
  if(!ok){$("msg").textContent=d.error;return;}
  show(d.state);
  $("msg").textContent=d.correct?"Purrfect! +"+d.earned+" coins.":"Hiss... that was not a "+d.order+". No coins.";
};
api("/api/state").then(([,s])=>show(s));
</script></body></html>
"""


if __name__ == "__main__":
    main()
