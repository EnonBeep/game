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
PENALTY = 1  # R5: coins lost for a wrong drink (never below 0)

INGREDIENTS = ["espresso", "hot water", "steamed milk", "milk foam", "chocolate", "tea leaves", "honey", "ice"]

def _svg(body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48" '
            'aria-hidden="true">' + body + '</svg>')


# R9 (round 4): original hand-drawn icons, one per ingredient (no downloads, no licences).
ICONS = {
    "espresso": _svg(
        '<ellipse cx="24" cy="38" rx="17" ry="4" fill="#d9c7b0"/>'
        '<path d="M10 18h24v8a12 12 0 0 1-24 0z" fill="#fff" stroke="#6b4226" stroke-width="2"/>'
        '<path d="M34 20h3a4 4 0 0 1 0 9h-4" fill="none" stroke="#6b4226" stroke-width="2"/>'
        '<ellipse cx="22" cy="19" rx="10" ry="2.5" fill="#4a2c17"/>'),
    "hot water": _svg(
        '<path d="M24 5c6 8 11 13 11 21a11 11 0 0 1-22 0c0-8 5-13 11-21z" fill="#6ec1e4" stroke="#2a7fa6" stroke-width="2"/>'
        '<path d="M18 28a6 6 0 0 0 5 6" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"/>'
        '<path d="M38 8q-3 4 0 8M43 10q-3 4 0 8" fill="none" stroke="#c9c9c9" stroke-width="2" stroke-linecap="round"/>'),
    "steamed milk": _svg(
        '<path d="M15 12h18l3 30H12z" fill="#fff" stroke="#8a8a8a" stroke-width="2"/>'
        '<path d="M14 22h20l1.6 20H12.4z" fill="#f4efe6"/>'
        '<path d="M32 4q-3 4 0 7M26 4q-3 4 0 7" fill="none" stroke="#c9c9c9" stroke-width="2" stroke-linecap="round"/>'),
    "milk foam": _svg(
        '<circle cx="17" cy="28" r="9" fill="#fff" stroke="#b9b9b9" stroke-width="2"/>'
        '<circle cx="30" cy="25" r="11" fill="#fff" stroke="#b9b9b9" stroke-width="2"/>'
        '<circle cx="24" cy="15" r="8" fill="#fff" stroke="#b9b9b9" stroke-width="2"/>'
        '<circle cx="21" cy="12" r="2" fill="#e8e8e8"/>'),
    "chocolate": _svg(
        '<rect x="8" y="10" width="32" height="28" rx="3" fill="#6b3f26" stroke="#3d2314" stroke-width="2"/>'
        '<path d="M8 24h32M20 10v28M32 10v28" stroke="#3d2314" stroke-width="2"/>'
        '<path d="M8 10h32l-4 6H12z" fill="#8a5636" opacity=".6"/>'),
    "tea leaves": _svg(
        '<path d="M8 38C8 18 22 8 40 8c0 20-12 30-32 30z" fill="#6fae4f" stroke="#3f7a2a" stroke-width="2"/>'
        '<path d="M8 38C18 28 28 20 36 12" fill="none" stroke="#3f7a2a" stroke-width="2"/>'),
    "honey": _svg(
        '<rect x="12" y="14" width="24" height="26" rx="6" fill="#f2b705" stroke="#a87800" stroke-width="2"/>'
        '<rect x="14" y="8" width="20" height="6" rx="2" fill="#8a5a3c"/>'
        '<rect x="17" y="22" width="14" height="10" rx="2" fill="#fff6d6"/>'
        '<path d="M24 14v6" stroke="#a87800" stroke-width="2"/>'),
    "ice": _svg(
        '<rect x="9" y="14" width="22" height="22" rx="4" fill="#cdeefc" stroke="#6fb8d9" stroke-width="2"/>'
        '<rect x="22" y="22" width="18" height="18" rx="4" fill="#e3f6fe" stroke="#6fb8d9" stroke-width="2"/>'
        '<path d="M13 19l5-2" stroke="#fff" stroke-width="2" stroke-linecap="round"/>'),
}

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
    """R5: pay REWARD for a correct drink; a wrong one costs PENALTY but coins never go
    below 0. Returns the actual change in coins (+REWARD, -PENALTY, or 0)."""
    state.served += 1
    if drink_matches(drink, customer.order):
        state.correct += 1
        state.coins += REWARD
        return REWARD
    lost = min(PENALTY, state.coins)
    state.coins -= lost
    return -lost


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
        self.cup = []  # R10: ingredients dragged into the cup, in order
        self.lid = False  # R9 (round 4): lid on the cup
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
            "cup": list(self.cup),
            "lid": self.lid,
            "icons": ICONS,
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

    def add_to_cup(self, ingredient):
        """R9/R10: drop an ingredient into the cup; repeats are ignored."""
        if self.lid:
            raise ValueError("The lid is on. Press Start over to begin again.")
        name = str(ingredient or "").strip().lower()
        prepare_drink([name] if name else [])  # raises ValueError if empty or unknown
        if name not in self.cup:
            self.cup.append(name)

    def put_lid_on(self):
        """R9: close the cup; needs at least one ingredient."""
        if not self.cup:
            raise ValueError("Put something in the cup before the lid.")
        self.lid = True

    def clear_cup(self):
        """R10: start over (also takes the lid off)."""
        self.cup = []
        self.lid = False

    def serve_drink(self, ingredients):
        """R3-R6: prepare, compare, pay, save, then bring the next customer."""
        drink = prepare_drink(ingredients)
        self.cup = []  # R11: the cup is empty after serving
        self.lid = False
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
        if method == "POST" and path == "/api/cup/add":
            try:
                self.add_to_cup(body.get("ingredient"))
            except ValueError as e:
                return 400, "application/json", {"error": str(e)}
            return 200, "application/json", self.snapshot()
        if method == "POST" and path == "/api/cup/lid":
            try:
                self.put_lid_on()
            except ValueError as e:
                return 400, "application/json", {"error": str(e)}
            return 200, "application/json", self.snapshot()
        if method == "POST" and path == "/api/cup/clear":
            self.clear_cup()
            return 200, "application/json", self.snapshot()
        if method == "POST" and path == "/api/serve":
            if not self.state:
                return 400, "application/json", {"error": "Name your barista first."}
            try:
                if "ingredients" not in body and self.cup and not self.lid:
                    raise ValueError("Put the lid on the cup first.")
                ingredients = body.get("ingredients", self.cup)  # R11: default to the cup
                if not isinstance(ingredients, list):
                    raise ValueError("ingredients must be a list.")
                customer, change = self.serve_drink([str(i) for i in ingredients])
            except ValueError as e:
                return 400, "application/json", {"error": str(e)}
            return 200, "application/json", {
                "correct": change == REWARD, "earned": max(change, 0), "coins_change": change,
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
h1{margin-top:0}
.tile{display:inline-block;margin:.25rem;padding:.4rem .6rem;background:#fff;border:2px solid #d98c5f;border-radius:14px;cursor:grab;user-select:none;text-align:center;font-size:.85rem}
.tile svg{display:block;margin:0 auto .15rem;width:48px;height:48px}
#cup{position:relative;width:180px;height:230px;margin:1rem 0;border-radius:14px}
#cup.over{background:#ffe3c9}
#cupsvg{position:absolute;inset:0;width:180px;height:230px}
#cupitems{position:absolute;left:38px;top:96px;width:104px;display:flex;flex-wrap:wrap;justify-content:center}
#cupitems svg{width:34px;height:34px;margin:1px}
#cupitems.empty{font-size:.8rem;color:#8a5a3c;top:140px;text-align:center}
#lid{display:inline-block;cursor:grab}
button{padding:.5rem 1rem;font-size:1rem;border-radius:8px;border:0;background:#d98c5f;color:#fff;cursor:pointer}
#msg{min-height:1.5rem;font-weight:bold}#menu{padding-left:1.2rem}#menu li{margin-bottom:.5rem}
</style></head><body>
<main>
<h1>&#128049; Cozy Cat Cafe</h1>
<div id="namebox" hidden><p>Name your barista cat:</p><input id="name" maxlength="30"> <button id="go">Open the cafe</button></div>
<div id="game" hidden>
<p id="stats"></p>
<h2 id="order"></h2>
<p>Drag ingredients into the cup:</p>
<div id="ings"></div>
<div id="cup" aria-label="Takeaway cup">
<svg id="cupsvg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 230" aria-hidden="true">
<path d="M32 70h116l-14 150a8 8 0 0 1-8 7H54a8 8 0 0 1-8-7z" fill="#fffaf3" stroke="#8a5a3c" stroke-width="3"/>
<path id="sleeve" d="M38 122h104l-5 56H43z" fill="#b5835a" stroke="#8a5a3c" stroke-width="3"/>
<g id="lidshape" visibility="hidden">
<rect x="22" y="46" width="136" height="14" rx="6" fill="#4a3426"/>
<path d="M34 46q4-24 56-24t56 24z" fill="#5c4332"/>
<rect x="76" y="14" width="28" height="8" rx="3" fill="#4a3426"/>
<rect x="26" y="60" width="128" height="10" rx="4" fill="#3b2a1f"/>
</g>
</svg>
<div id="cupitems"></div></div>
<p>Drag the lid onto the cup when you are done:</p>
<div id="lidtray"><span id="lid" class="tile" draggable="true" data-ing="__lid__">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" aria-hidden="true"><rect x="4" y="28" width="40" height="8" rx="4" fill="#4a3426"/><path d="M9 28q2-14 15-14t15 14z" fill="#5c4332"/><rect x="19" y="9" width="10" height="5" rx="2" fill="#4a3426"/></svg>lid</span></div>
<p><button id="serve">Serve</button> <button id="clear">Start over</button></p>
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
  const icons=s.icons;
  $("ings").innerHTML=s.ingredients.map(i=>'<span class="tile" draggable="true" data-ing="'+esc(i)+'">'+(icons[i]||"")+esc(i)+"</span>").join("");
  $("cupitems").className=s.cup.length?"":"empty";
  $("cupitems").innerHTML=s.cup.length?s.cup.map(i=>'<span title="'+esc(i)+'">'+(icons[i]||esc(i))+"</span>").join(""):"The cup is empty.";
  $("lidshape").setAttribute("visibility",s.lid?"visible":"hidden");
  $("lidtray").hidden=s.lid;
}
$("go").onclick=async()=>show((await api("/api/name",{name:$("name").value}))[1]);
document.addEventListener("dragstart",e=>{
  const t=e.target.closest&&e.target.closest("[data-ing]");
  if(t)e.dataTransfer.setData("text/plain",t.dataset.ing);
});
const cup=$("cup");
cup.addEventListener("dragover",e=>{e.preventDefault();cup.classList.add("over");});
cup.addEventListener("dragleave",()=>cup.classList.remove("over"));
cup.addEventListener("drop",async e=>{
  e.preventDefault();cup.classList.remove("over");
  const what=e.dataTransfer.getData("text/plain");
  const [ok,d]=what==="__lid__"?await api("/api/cup/lid",{}):await api("/api/cup/add",{ingredient:what});
  if(ok){$("msg").textContent="";show(d);}else $("msg").textContent=d.error;
});
$("clear").onclick=async()=>show((await api("/api/cup/clear",{}))[1]);
$("serve").onclick=async()=>{
  const [ok,d]=await api("/api/serve",{});
  if(!ok){$("msg").textContent=d.error;return;}
  show(d.state);
  const c=d.coins_change;
  $("msg").textContent=d.correct?"Purrfect! +"+c+" coins.":"Hiss... that was not a "+d.order+". "+(c<0?"-1 coin.":"No coins lost (you had none).");
};
api("/api/state").then(([,s])=>show(s));
</script></body></html>
"""


if __name__ == "__main__":
    main()
