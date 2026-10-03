from __future__ import annotations

import math
from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Location

from .data import fruits, memory_map

if TYPE_CHECKING:
    from .world import Pikmin3World

# Plages d'identifiants (uniques pour ce jeu uniquement, comme le permet Archipelago).
FRUIT_BASE = 1000            # « Fruit N » -> 1000 + N
ONION_BASE = 2000            # « Discover X Onion » : voir ONION_LOCATION_ID
KEY_ITEM_BASE = 3000         # 3000 + numéro du bit dans STATE_KEY_ITEM_BITS
TUTORIAL_NOTE_BASE = 4000    # « Tutorial Note N » -> 4000 + N
OLIMAR_NOTE_BASE = 4100      # « Olimar Note N » -> 4100 + N
SECRET_MEMO_BASE = 4200      # « Secret Memo N » -> 4200 + N
POPULATION_BASE = 5000       # « Population P » -> 5000 + P (P multiple de 10)

# Nombres relevés sur une partie terminée (sauvegarde du jour 28) ; Secret Memos : 10 d'après les guides.
MAX_TUTORIAL_NOTES = 63
MAX_OLIMAR_NOTES = 15
MAX_SECRET_MEMOS = 10
POPULATION_MILESTONE_MAX = 1000


class Pikmin3Location(Location):
    game = "Pikmin 3"


class LocationData(NamedTuple):
    name: str
    code: int
    # Limite de Pikmin sur le terrain jugée nécessaire pour ce check (logique V1, approximative).
    required_limit: int
    # Items « Progressive Zone » nécessaires (option « Progressive Zones »), voir plus bas.
    required_zones: int = 0


# --------------------------------------------------------------------------
# Logique V1 : besoin en Pikmin
# --------------------------------------------------------------------------
# Sans la liste complète « fruit ↔ emplacement », la V1 suppose une progression régulière :
# les premiers fruits se ramassent avec peu de Pikmin, les derniers demandent la limite maximale.

def fruit_required_limit(count: int) -> int:
    """Limite de Pikmin nécessaire pour presser `count` fruits (1 -> 22, 33 -> 60, 66 -> 100)."""
    return min(memory_map.FIELD_LIMIT_VANILLA, 20 + math.ceil(80 * count / fruits.TOTAL_FRUITS))


def population_required_limit(population: int) -> int:
    """Limite de Pikmin nécessaire pour atteindre une population donnée."""
    return min(memory_map.FIELD_LIMIT_VANILLA, max(0, population // 3))


# --------------------------------------------------------------------------
# Logique des zones (option « Progressive Zones »)
# --------------------------------------------------------------------------
# La liste « check ↔ zone » n'est pas encore connue. En attendant, chaque check demande un nombre d'items
# « Progressive Zone » déduit de la partie de l'utilisateur (sauvegardes de chaque jour) : obtenu les jours 2–7,
# avec les 2 zones du départ seules → 0 ; jours 8–12, la 3ᵉ zone ouverte au jour 8 → 1 ; plus tard ou jamais
# vu → toutes les zones à fruits. Prudent : un check déjà fait avec moins de zones ne demande jamais plus.
FRUIT_ZONE_ITEMS = 2         # zones à fruits après le départ (la zone du boss final n'a pas de fruit)
FRUITS_WITH_START_ZONES = 5  # fruits pressés au début du jour 8 (single8.sav)
FRUITS_WITH_ONE_ZONE = 15    # fruits pressés au début du jour 13 (single13.sav), avant toute zone forcée


def fruit_required_zones(count: int) -> int:
    """Items « Progressive Zone » nécessaires pour presser `count` fruits."""
    if count <= FRUITS_WITH_START_ZONES:
        return 0
    if count <= FRUITS_WITH_ONE_ZONE:
        return 1
    return FRUIT_ZONE_ITEMS


def population_required_zones(population: int) -> int:
    """Items « Progressive Zone » nécessaires pour atteindre une population (54 au jour 2, 248 au jour 11)."""
    if population <= 50:
        return 0
    if population <= 240:
        return 1
    return FRUIT_ZONE_ITEMS


# Oignons (sauf le rouge, présent dès le départ) : type de Pikmin (memory_map.ONION_SLOTS) -> besoin en Pikmin.
ONION_REQUIRED_LIMIT = {2: 60, 5: 40, 6: 60, 7: 0}
# Identifiants inchangés depuis la V1 : 2001 bleu, 2002 jaune, 2003 ailé, 2004 roc.
ONION_LOCATION_ID = {2: ONION_BASE + 1, 5: ONION_BASE + 2, 6: ONION_BASE + 3, 7: ONION_BASE + 4}
# Zones : roc trouvé au jour 2, jaune au jour 8 ; bleu et ailé jamais trouvés naturellement.
ONION_REQUIRED_ZONES = {2: FRUIT_ZONE_ITEMS, 5: 1, 6: FRUIT_ZONE_ITEMS, 7: 0}

# Objets importants connus : bit -> besoin en Pikmin (estimé d'après le moment où on les obtient :
# Data Glutton / Anti-Electrifier vers les jours 7–9, Dodge Whistle jour 10, Metal Suit Z jour 13, Louie jour 23).
KEY_ITEM_REQUIRED_LIMIT = {0x01: 60, 0x02: 40, 0x10: 40, 0x40: 60, 0x80: 50}
# Zones : Data Glutton entre les jours 3 et 7, Anti-Electrifier jour 9, Dodge Whistle jour 10,
# Metal Suit Z jour 13 et Louie jour 23 (après l'ouverture forcée des zones → toutes les zones à fruits).
KEY_ITEM_REQUIRED_ZONES = {0x01: FRUIT_ZONE_ITEMS, 0x02: 0, 0x10: 1, 0x40: FRUIT_ZONE_ITEMS, 0x80: 1}
# Noms de checks particuliers (sinon « Obtain <objet> »).
KEY_ITEM_LOCATION_NAMES = {0x01: "Rescue Louie"}
# Notes : nombres relevés dans les sauvegardes de chaque jour (zones ouvertes connues) → (limite, zones).
# Début du jour 8 (zones du départ) : 29 conseils, 1 Olimar ; jour 13 (+ Distant Tundra) : 47 / 5 ;
# jour 19 (+ Twilight River, avant toute visite de Formidable Oak) : 51 / 6 ; au-delà → toutes les zones.
ALL_ZONE_ITEMS = len(memory_map.PROGRESSIVE_ZONE_BITS)
TUTORIAL_NOTE_STEPS = ((29, 0, 0), (47, 40, 1), (51, 60, FRUIT_ZONE_ITEMS))
OLIMAR_NOTE_STEPS = ((1, 40, 0), (5, 40, 1), (6, 60, FRUIT_ZONE_ITEMS))


def note_requirements(count: int, steps: tuple[tuple[int, int, int], ...]) -> tuple[int, int]:
    """(limite de Pikmin, items de zone) nécessaires pour avoir `count` notes d'une famille."""
    for maximum, limit, zones in steps:
        if count <= maximum:
            return limit, zones
    return 60, ALL_ZONE_ITEMS


def onion_location_name(slot: int) -> str:
    return f"Discover {memory_map.ONION_SLOTS[slot][0]} Onion"


def key_item_location_name(bit: int) -> str:
    return KEY_ITEM_LOCATION_NAMES.get(bit, f"Obtain {memory_map.KEY_ITEM_BITS[bit]}")


def population_location_name(population: int) -> str:
    return f"Population {population}"


FRUIT_LOCATIONS = [
    LocationData(f"Fruit {n}", FRUIT_BASE + n, fruit_required_limit(n), fruit_required_zones(n))
    for n in range(1, fruits.TOTAL_FRUITS + 1)
]
ONION_LOCATIONS = [
    LocationData(onion_location_name(slot), ONION_LOCATION_ID[slot], ONION_REQUIRED_LIMIT[slot],
                 ONION_REQUIRED_ZONES[slot])
    for slot in sorted(ONION_REQUIRED_LIMIT)
]
KEY_ITEM_LOCATIONS = [
    LocationData(key_item_location_name(bit), KEY_ITEM_BASE + bit.bit_length() - 1, KEY_ITEM_REQUIRED_LIMIT[bit],
                 KEY_ITEM_REQUIRED_ZONES[bit])
    for bit in sorted(KEY_ITEM_REQUIRED_LIMIT)
]
TUTORIAL_NOTE_LOCATIONS = [
    LocationData(f"Tutorial Note {n}", TUTORIAL_NOTE_BASE + n, *note_requirements(n, TUTORIAL_NOTE_STEPS))
    for n in range(1, MAX_TUTORIAL_NOTES + 1)
]
OLIMAR_NOTE_LOCATIONS = [
    LocationData(f"Olimar Note {n}", OLIMAR_NOTE_BASE + n, *note_requirements(n, OLIMAR_NOTE_STEPS))
    for n in range(1, MAX_OLIMAR_NOTES + 1)
]
# Emplacements des Secret Memos inconnus : toutes les zones.
SECRET_MEMO_LOCATIONS = [
    LocationData(f"Secret Memo {n}", SECRET_MEMO_BASE + n, 60, ALL_ZONE_ITEMS) for n in range(1, MAX_SECRET_MEMOS + 1)
]
POPULATION_LOCATIONS = [
    LocationData(population_location_name(p), POPULATION_BASE + p, population_required_limit(p),
                 population_required_zones(p))
    for p in range(10, POPULATION_MILESTONE_MAX + 1, 10)
]

ALL_LOCATIONS = (
    FRUIT_LOCATIONS + ONION_LOCATIONS + KEY_ITEM_LOCATIONS
    + TUTORIAL_NOTE_LOCATIONS + OLIMAR_NOTE_LOCATIONS + SECRET_MEMO_LOCATIONS + POPULATION_LOCATIONS
)
LOCATION_NAME_TO_ID = {data.name: data.code for data in ALL_LOCATIONS}
LOCATION_DATA_BY_NAME = {data.name: data for data in ALL_LOCATIONS}

LOCATION_NAME_GROUPS = {
    "Fruits": {data.name for data in FRUIT_LOCATIONS},
    "Onions": {data.name for data in ONION_LOCATIONS},
    "Key Items": {data.name for data in KEY_ITEM_LOCATIONS},
    "Notes": {data.name for data in TUTORIAL_NOTE_LOCATIONS + OLIMAR_NOTE_LOCATIONS},
    "Secret Memos": {data.name for data in SECRET_MEMO_LOCATIONS},
    "Population": {data.name for data in POPULATION_LOCATIONS},
}


def population_milestones(step: int, maximum: int) -> list[int]:
    """Paliers actifs : multiples de `step` (arrondi à la dizaine) jusqu'à `maximum`."""
    step = max(10, round(step / 10) * 10)
    return list(range(step, min(maximum, POPULATION_MILESTONE_MAX) + 1, step))


def enabled_locations(world: Pikmin3World) -> list[LocationData]:
    """Liste des checks actifs selon les options du joueur."""
    options = world.options
    active = list(FRUIT_LOCATIONS)
    # Avec « Progressive Pikmin », les items allument eux-mêmes le bit des Oignons : pas de check de découverte.
    if options.onion_checks and not options.progressive_pikmin:
        active += ONION_LOCATIONS
    if options.key_item_checks:
        active += KEY_ITEM_LOCATIONS
    if options.note_checks:
        active += TUTORIAL_NOTE_LOCATIONS[: options.tutorial_note_count.value]
        active += OLIMAR_NOTE_LOCATIONS[: options.olimar_note_count.value]
    active += SECRET_MEMO_LOCATIONS[: options.secret_memo_count.value]
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
