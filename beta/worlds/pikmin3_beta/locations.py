from __future__ import annotations

import math
from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Location

from .data import check_names, fruits, memory_map
from .data.game_info import GAME_NAME

if TYPE_CHECKING:
    from .world import Pikmin3World

# Plages d'identifiants (uniques pour ce jeu uniquement, comme le permet Archipelago).
FRUIT_BASE = 1000            # « Fruit N » -> 1000 + N
ONION_BASE = 2000            # « Discover X Onion » : voir ONION_LOCATION_ID
KEY_ITEM_BASE = 3000         # 3000 + numéro du bit dans STATE_KEY_ITEM_BITS
NOTES_B_BASE = 4000          # « Notes B #N » -> 4000 + N (ensemble B)
OLIMAR_NOTE_BASE = 4100      # « Olimar Note N » -> 4100 + N (ensemble D)
NOTES_A_BASE = 4200          # « Notes A #N » -> 4200 + N (ensemble A)
NOTES_C_BASE = 4300          # « Notes C #N » -> 4300 + N (ensemble C)
POPULATION_BASE = 5000       # « Population P » -> 5000 + P (P multiple de 10)
DAY_BASE = 6000              # « Reach Day N » -> 6000 + N
FRUIT_KIND_BASE = 7000       # « Fruit Kind N » -> 7000 + N
STORY_EVENT_BASE = 8000      # « Story Event N » -> 8000 + N

MAX_NOTES_PER_KIND = 40
POPULATION_MILESTONE_MAX = 1000
MAX_DAY_CHECK = 60
FRUIT_KINDS = len(fruits.FRUIT_JUICE)
MAX_STORY_EVENTS = 10

# Ensemble de notes -> (base des identifiants, préfixe du nom). Noms : data/check_names.py.
NOTE_SET_LOCATIONS = {
    key: (base, check_names.NOTE_SET_PREFIXES[key])
    for key, base in (("A", NOTES_A_BASE), ("B", NOTES_B_BASE), ("C", NOTES_C_BASE), ("D", OLIMAR_NOTE_BASE))
}


class Pikmin3Location(Location):
    game = GAME_NAME


class LocationData(NamedTuple):
    name: str
    code: int
    # Limite de Pikmin sur le terrain jugée nécessaire pour ce check (logique V1, approximative).
    required_limit: int


# --------------------------------------------------------------------------
# Logique V1 : besoin en Pikmin
# --------------------------------------------------------------------------
# Sans la liste complète « fruit ↔ emplacement », la V1 suppose une progression régulière :
# les premiers fruits se ramassent avec peu de Pikmin, les derniers demandent la limite maximale.

def fruit_required_limit(count: int) -> int:
    """Limite de Pikmin nécessaire pour presser `count` fruits (1 -> 22, 33 -> 60, 66 -> 100)."""
    return min(memory_map.FIELD_LIMIT_VANILLA, 20 + math.ceil(80 * count / fruits.TOTAL_FRUITS))


def fruit_kind_required_limit(kinds: int) -> int:
    """Limite nécessaire pour la N-ième sorte de fruit (30 sortes réparties sur les 66 fruits)."""
    return fruit_required_limit(math.ceil(fruits.TOTAL_FRUITS * kinds / FRUIT_KINDS))


def story_event_required_limit(event: int) -> int:
    """Étapes d'histoire : la 1re (Data Glutton) demande déjà une petite armée."""
    return min(memory_map.FIELD_LIMIT_VANILLA, 20 + 20 * event)


def population_required_limit(population: int) -> int:
    """Limite de Pikmin nécessaire pour atteindre une population donnée."""
    return min(memory_map.FIELD_LIMIT_VANILLA, max(0, population // 3))


# Oignons (sauf le rouge, présent dès le départ) : type de Pikmin (memory_map.ONION_SLOTS) -> besoin en Pikmin.
ONION_REQUIRED_LIMIT = {2: 60, 5: 40, 6: 60, 7: 0}
# Identifiants inchangés depuis l'ancien modèle par emplacement (2001 bleu, 2002 jaune, 2003 ailé, 2004 roc),
# les mêmes que dans worlds/pikmin3.
ONION_LOCATION_ID = {2: ONION_BASE + 1, 5: ONION_BASE + 2, 6: ONION_BASE + 3, 7: ONION_BASE + 4}

# Objets importants connus : bit -> besoin en Pikmin.
KEY_ITEM_REQUIRED_LIMIT = {0x02: 40, 0x10: 40, 0x40: 60, 0x80: 50}


# Noms des checks : un seul endroit (data/check_names.py), partagé avec la console des checks.
onion_location_name = check_names.onion
key_item_location_name = check_names.key_item
population_location_name = check_names.population


FRUIT_LOCATIONS = [
    LocationData(check_names.fruit(n), FRUIT_BASE + n, fruit_required_limit(n))
    for n in range(1, fruits.TOTAL_FRUITS + 1)
]
ONION_LOCATIONS = [
    LocationData(onion_location_name(slot), ONION_LOCATION_ID[slot], ONION_REQUIRED_LIMIT[slot])
    for slot in sorted(ONION_REQUIRED_LIMIT)
]
KEY_ITEM_LOCATIONS = [
    LocationData(key_item_location_name(bit), KEY_ITEM_BASE + bit.bit_length() - 1, KEY_ITEM_REQUIRED_LIMIT[bit])
    for bit in sorted(KEY_ITEM_REQUIRED_LIMIT)
]
# Notes : les ensembles A/B/C ne demandent rien (tutoriels), les notes d'Olimar demandent une armée.
NOTE_LOCATIONS = {
    key: [LocationData(check_names.note(key, n), base + n, 40 if key == "D" else 0)
          for n in range(1, MAX_NOTES_PER_KIND + 1)]
    for key, (base, _) in NOTE_SET_LOCATIONS.items()
}
DAY_LOCATIONS = [LocationData(check_names.day(n), DAY_BASE + n, 0) for n in range(2, MAX_DAY_CHECK + 1)]
FRUIT_KIND_LOCATIONS = [
    LocationData(check_names.fruit_kind(n), FRUIT_KIND_BASE + n, fruit_kind_required_limit(n))
    for n in range(1, FRUIT_KINDS + 1)
]
STORY_EVENT_LOCATIONS = [
    LocationData(check_names.story_event(n), STORY_EVENT_BASE + n, story_event_required_limit(n))
    for n in range(1, MAX_STORY_EVENTS + 1)
]
POPULATION_LOCATIONS = [
    LocationData(population_location_name(p), POPULATION_BASE + p, population_required_limit(p))
    for p in range(10, POPULATION_MILESTONE_MAX + 1, 10)
]

ALL_LOCATIONS = (
    FRUIT_LOCATIONS + ONION_LOCATIONS + KEY_ITEM_LOCATIONS
    + [data for group in NOTE_LOCATIONS.values() for data in group] + POPULATION_LOCATIONS
    + DAY_LOCATIONS + FRUIT_KIND_LOCATIONS + STORY_EVENT_LOCATIONS
)
LOCATION_NAME_TO_ID = {data.name: data.code for data in ALL_LOCATIONS}
LOCATION_DATA_BY_NAME = {data.name: data for data in ALL_LOCATIONS}

LOCATION_NAME_GROUPS = {
    "Fruits": {data.name for data in FRUIT_LOCATIONS},
    "Onions": {data.name for data in ONION_LOCATIONS},
    "Key Items": {data.name for data in KEY_ITEM_LOCATIONS},
    "Notes": {data.name for group in NOTE_LOCATIONS.values() for data in group},
    "Population": {data.name for data in POPULATION_LOCATIONS},
    "Days": {data.name for data in DAY_LOCATIONS},
    "Fruit Kinds": {data.name for data in FRUIT_KIND_LOCATIONS},
    "Story Events": {data.name for data in STORY_EVENT_LOCATIONS},
}


def population_milestones(step: int, maximum: int) -> list[int]:
    """Paliers actifs : multiples de `step` (arrondi à la dizaine) jusqu'à `maximum`."""
    step = max(10, round(step / 10) * 10)
    return list(range(step, min(maximum, POPULATION_MILESTONE_MAX) + 1, step))


def note_counts(world: Pikmin3World) -> dict[str, int]:
    """Nombre de checks par ensemble de notes, d'après les options."""
    options = world.options
    return {
        "A": options.notes_a_count.value,
        "B": options.notes_b_count.value,
        "C": options.notes_c_count.value,
        "D": options.olimar_note_count.value,
    }


def enabled_locations(world: Pikmin3World) -> list[LocationData]:
    """Liste des checks actifs selon les options du joueur."""
    options = world.options
    active = list(FRUIT_LOCATIONS)
    if options.onion_checks:
        active += ONION_LOCATIONS
    if options.key_item_checks:
        active += KEY_ITEM_LOCATIONS
    if options.note_checks:
        for key, count in note_counts(world).items():
            active += NOTE_LOCATIONS[key][:count]
    if options.day_checks:
        active += DAY_LOCATIONS[: options.day_check_max.value - 1]
    if options.fruit_kind_checks:
        active += FRUIT_KIND_LOCATIONS[: options.fruit_kind_max.value]
    if options.story_event_checks:
        active += STORY_EVENT_LOCATIONS[: options.story_event_count.value]
    for population in population_milestones(options.population_milestone_step.value,
                                            options.population_milestone_max.value):
        active.append(LOCATION_DATA_BY_NAME[population_location_name(population)])
    return active


def create_all_locations(world: Pikmin3World) -> None:
    planet = world.get_region("Planet")
    planet.add_locations({data.name: data.code for data in enabled_locations(world)}, Pikmin3Location)

    # Événement de victoire (sans identifiant) : la règle est posée dans rules.py.
    from .items import Pikmin3Item
    planet.add_event("Goal Reached", "Victory", location_type=Pikmin3Location, item_type=Pikmin3Item)
