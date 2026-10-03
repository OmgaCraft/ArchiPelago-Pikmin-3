"""
Noms des checks (locations Archipelago) et libellés en français pour la console des checks.

Module sans dépendance à Archipelago : utilisé par locations.py (génération) et par client/events.py
(console des checks, qui doit aussi marcher sans Archipelago installé).
"""

from . import memory_map as mm

# Ensemble de notes -> préfixe du nom de check. L'ensemble D garde le nom « Olimar Note ».
NOTE_SET_PREFIXES = {
    "A": "Notes A #",
    "B": "Notes B #",
    "C": "Notes C #",
    "D": "Olimar Note ",
}

# Libellés affichés dans la console (sens 🔶 sauf pour D).
NOTE_SET_LABELS = {
    "A": "Pikmin-ology",
    "B": "Tutoriel",
    "C": "Document / scène",
    "D": "Olimar",
}

ONION_LABELS = {"Red": "rouge", "Blue": "bleu", "Yellow": "jaune", "Winged": "ailé", "Rock": "roc"}


def fruit(n: int) -> str:
    return f"Fruit {n}"


def onion(slot: int) -> str:
    return f"Discover {mm.ONION_SLOTS[slot][0]} Onion"


def key_item(bit: int) -> str:
    return f"Obtain {mm.KEY_ITEM_BITS[bit]}"


def note(key: str, n: int) -> str:
    return f"{NOTE_SET_PREFIXES[key]}{n}"


def population(value: int) -> str:
    return f"Population {value}"


def day(n: int) -> str:
    return f"Reach Day {n}"


def fruit_kind(n: int) -> str:
    return f"Fruit Kind {n}"


def story_event(n: int) -> str:
    return f"Story Event {n}"
