from __future__ import annotations

import math
from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Item, ItemClassification

from .data import fruits, memory_map

if TYPE_CHECKING:
    from .world import Pikmin3World


class Pikmin3Item(Item):
    game = "Pikmin 3"


class ItemData(NamedTuple):
    code: int
    classification: ItemClassification


PROGRESSIVE_PIKMIN_LIMIT = "Progressive Pikmin Limit"
PROGRESSIVE_ZONE = "Progressive Zone"     # ouvre la zone suivante (memory_map.PROGRESSIVE_ZONE_BITS)
PROGRESSIVE_PIKMIN = "Progressive Pikmin"  # débloque le type suivant (memory_map.PROGRESSIVE_PIKMIN_TYPES)
JUICE_DROP = "Juice Drop"                 # +0.5 bouteille
EXTRA_RED_PIKMIN = "Extra Red Pikmin"     # +5 Pikmin Rouges dans l'Oignon
ULTRA_SPICY_SPRAY = "Ultra-Spicy Spray"   # +1 spray
JUICE_LEAK_TRAP = "Juice Leak Trap"       # -0.5 bouteille (jamais sous 1 bouteille)

JUICE_DROP_AMOUNT = 0.5
EXTRA_PIKMIN_AMOUNT = 5
JUICE_LEAK_AMOUNT = 0.5

ITEM_TABLE: dict[str, ItemData] = {
    PROGRESSIVE_PIKMIN_LIMIT: ItemData(1, ItemClassification.progression),
    PROGRESSIVE_ZONE: ItemData(2, ItemClassification.progression),
    # Utile seulement : l'histoire donne aussi les types de Pikmin (pas encore bloquée), ils ne sont donc pas en logique.
    PROGRESSIVE_PIKMIN: ItemData(3, ItemClassification.useful),
    JUICE_DROP: ItemData(10, ItemClassification.filler),
    EXTRA_RED_PIKMIN: ItemData(11, ItemClassification.filler),
    ULTRA_SPICY_SPRAY: ItemData(12, ItemClassification.filler),
    JUICE_LEAK_TRAP: ItemData(20, ItemClassification.trap),
}

# Un item par type de fruit : le recevoir ajoute le jus de ce fruit (identifiants 101+).
FRUIT_ITEM_NAMES = sorted(fruits.FRUIT_JUICE)
for _index, _name in enumerate(FRUIT_ITEM_NAMES, start=101):
    ITEM_TABLE[_name] = ItemData(_index, ItemClassification.useful)

ITEM_NAME_TO_ID = {name: data.code for name, data in ITEM_TABLE.items()}
ITEM_NAME_GROUPS = {"Fruits": set(FRUIT_ITEM_NAMES)}
FILLER_ITEM_NAMES = [JUICE_DROP, EXTRA_RED_PIKMIN, ULTRA_SPICY_SPRAY]


def pikmin_limit_item_count(start: int, step: int) -> int:
    """Nombre d'items nécessaires pour passer de `start` à la limite normale (100)."""
    return math.ceil(max(0, memory_map.FIELD_LIMIT_VANILLA - start) / step)


ZONE_ITEM_COUNT = len(memory_map.PROGRESSIVE_ZONE_BITS)  # 3 : les zones qui suivent les 2 du départ
PIKMIN_TYPE_ITEM_COUNT = len(memory_map.PROGRESSIVE_PIKMIN_TYPES)  # 4 : roc, jaune, ailé, bleu


def create_item(world: Pikmin3World, name: str) -> Pikmin3Item:
    data = ITEM_TABLE[name]
    return Pikmin3Item(name, data.classification, data.code, world.player)


def get_random_filler_item_name(world: Pikmin3World) -> str:
    if world.random.randint(0, 99) < world.options.trap_percentage.value:
        return JUICE_LEAK_TRAP
    weights = [world.options.filler_weights.value.get(name, 0) for name in FILLER_ITEM_NAMES]
    if sum(weights) <= 0:
        return JUICE_DROP
    return world.random.choices(FILLER_ITEM_NAMES, weights=weights)[0]


def create_all_items(world: Pikmin3World) -> None:
    itempool: list[Item] = []
    options = world.options

    if options.progressive_pikmin_limit:
        count = pikmin_limit_item_count(options.pikmin_limit_start.value, options.pikmin_limit_step.value)
        itempool += [world.create_item(PROGRESSIVE_PIKMIN_LIMIT) for _ in range(count)]

    if options.progressive_zones:
        itempool += [world.create_item(PROGRESSIVE_ZONE) for _ in range(ZONE_ITEM_COUNT)]

    if options.progressive_pikmin:
        itempool += [world.create_item(PROGRESSIVE_PIKMIN) for _ in range(PIKMIN_TYPE_ITEM_COUNT)]

    # Les fruits ne donnent plus de jus quand on les presse : le jus arrive par ces items.
    # On distribue les 30 types de façon équilibrée (au moins deux fois chacun pour 66 fruits).
    open_slots = len(world.multiworld.get_unfilled_locations(world.player)) - len(itempool)
    fruit_item_count = max(0, min(fruits.TOTAL_FRUITS, open_slots))
    fruit_cycle: list[str] = []
    while len(fruit_cycle) < fruit_item_count:
        batch = list(FRUIT_ITEM_NAMES)
        world.random.shuffle(batch)
        fruit_cycle += batch
    itempool += [world.create_item(name) for name in fruit_cycle[:fruit_item_count]]

    filler_count = len(world.multiworld.get_unfilled_locations(world.player)) - len(itempool)
    itempool += [world.create_filler() for _ in range(filler_count)]

    world.multiworld.itempool += itempool
