"""Cozy Cat Cafe: a short-session terminal game where you are a cat barista."""
import json
import os
import random
from dataclasses import dataclass, field

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


def play(input_fn=input, print_fn=print, rng=random, path=SAVE_FILE):
    """R1: the player controls the barista cat through text commands."""
    state = load_game(path)
    if state:
        print_fn(f"Welcome back, {state.barista.name}! You have {state.coins} coins.")
    else:
        name = input_fn("Name your barista cat: ").strip() or "Barista"
        state = GameState(Cat(name))
        print_fn(f"Meow! {name} opens the cafe.")
    print_fn("Ingredients: " + ", ".join(INGREDIENTS))
    print_fn("Type ingredients separated by commas to make a drink, or 'quit' to leave.")
    while True:
        customer = generate_customer(rng)
        print_fn(f"\n{customer.cat.name} the cat orders a {customer.order}.")
        answer = input_fn("Your drink> ").strip()
        if answer.lower() in ("quit", "q"):
            break
        try:
            drink = prepare_drink(answer.split(","))
        except ValueError as e:
            print_fn(str(e) + " The customer wanders off.")
            continue
        earned = serve(state, customer, drink)
        if earned:
            print_fn(f"Purrfect! +{earned} coins. Total: {state.coins}")
        else:
            print_fn("Hiss... that's not what they ordered. No coins.")
        save_game(state, path)
    save_game(state, path)
    print_fn(f"See you soon! Coins: {state.coins}")
    return state


if __name__ == "__main__":
    play()
