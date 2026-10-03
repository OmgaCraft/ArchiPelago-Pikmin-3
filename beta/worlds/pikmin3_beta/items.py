from __future__ import annotations

import math
from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Item, ItemClassification

from .data import fruits, memory_map
from .data.game_info import GAME_NAME

if TYPE_CHECKING:
    from .world import Pikmin3World


class Pikmin3Item(Item):
    game = GAME_NAME


class ItemData(NamedTuple):
    code: int
    classification: ItemClassification


PROGRESSIVE_PIKMIN_LIMIT = "Progressive Pikmin Limit"
JUICE_DROP = "Juice Drop"                 # +0.5 bouteille
EXTRA_RED_PIKMIN = "Extra Red Pikmin"     # +5 Pikmin Rouges dans l'Oignon
ULTRA_SPICY_SPRAY = "Ultra-Spicy Spray"   # +1 spray
JUICE_LEAK_TRAP = "Juice Leak Trap"       # -0.5 bouteille (jamais sous 1 bouteille)
# BÊTA : items encore à valider en jeu.
EXTRA_YELLOW_PIKMIN = "Extra Yellow Pikmin"   # +5 dans l'Oignon jaune
EXTRA_ROCK_PIKMIN = "Extra Rock Pikmin"       # +5 dans l'Oignon roc
EXTRA_BLUE_PIKMIN = "Extra Blue Pikmin"       # +5 dans l'Oignon bleu (type 2)
EXTRA_WINGED_PIKMIN = "Extra Winged Pikmin"   # +5 dans l'Oignon ailé (type 6)
ULTRA_SPICY_BERRY = "Ultra-Spicy Berry"       # +1 baie ultra-épicée

# Item « Pikmin en plus » -> type de Pikmin (voir memory_map.ONION_SLOTS).
# Si l'Oignon n'est pas encore découvert, le client donne des Pikmin rouges à la place : des Pikmin d'un type
# pas encore débloqué apparaissent dans le menu de l'Oignon, mais en sortir un fait planter le jeu.
EXTRA_PIKMIN_SLOTS = {
    "Extra Red Pikmin": memory_map.RED_SLOT,
    EXTRA_BLUE_PIKMIN: 2,
    EXTRA_YELLOW_PIKMIN: 5,
    EXTRA_WINGED_PIKMIN: 6,
    EXTRA_ROCK_PIKMIN: 7,
}

JUICE_DROP_AMOUNT = 0.5
EXTRA_PIKMIN_AMOUNT = 5
JUICE_LEAK_AMOUNT = 0.5
BERRY_AMOUNT = 1

ITEM_TABLE: dict[str, ItemData] = {
    PROGRESSIVE_PIKMIN_LIMIT: ItemData(1, ItemClassification.progression),
    JUICE_DROP: ItemData(10, ItemClassification.filler),
    EXTRA_RED_PIKMIN: ItemData(11, ItemClassification.filler),
    ULTRA_SPICY_SPRAY: ItemData(12, ItemClassification.filler),
    JUICE_LEAK_TRAP: ItemData(20, ItemClassification.trap),
    EXTRA_YELLOW_PIKMIN: ItemData(13, ItemClassification.filler),
    EXTRA_ROCK_PIKMIN: ItemData(14, ItemClassification.filler),
    EXTRA_BLUE_PIKMIN: ItemData(15, ItemClassification.filler),
    EXTRA_WINGED_PIKMIN: ItemData(16, ItemClassification.filler),
    ULTRA_SPICY_BERRY: ItemData(17, ItemClassification.filler),
}

# Un item par type de fruit : le recevoir ajoute le jus de ce fruit (identifiants 101+).
FRUIT_ITEM_NAMES = sorted(fruits.FRUIT_JUICE)
for _index, _name in enumerate(FRUIT_ITEM_NAMES, start=101):
    ITEM_TABLE[_name] = ItemData(_index, ItemClassification.useful)

ITEM_NAME_TO_ID = {name: data.code for name, data in ITEM_TABLE.items()}
ITEM_NAME_GROUPS = {"Fruits": set(FRUIT_ITEM_NAMES), "Extra Pikmin": set(EXTRA_PIKMIN_SLOTS)}
FILLER_ITEM_NAMES = [JUICE_DROP, EXTRA_RED_PIKMIN, EXTRA_YELLOW_PIKMIN, EXTRA_ROCK_PIKMIN, EXTRA_BLUE_PIKMIN,
                     EXTRA_WINGED_PIKMIN, ULTRA_SPICY_SPRAY, ULTRA_SPICY_BERRY]


def pikmin_limit_item_count(start: int, step: int) -> int:
    """Nombre d'items nécessaires pour passer de `start` à la limite normale (100)."""
    return math.ceil(max(0, memory_map.FIELD_LIMIT_VANILLA - start) / step)


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
