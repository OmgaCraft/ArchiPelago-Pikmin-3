from __future__ import annotations

import math
from typing import TYPE_CHECKING

from worlds.generic.Rules import set_rule

from . import locations
from .items import PROGRESSIVE_PIKMIN_LIMIT, PROGRESSIVE_ZONE, ZONE_ITEM_COUNT, pikmin_limit_item_count

if TYPE_CHECKING:
    from .world import Pikmin3World


def limit_items_needed(world: Pikmin3World, required_limit: int) -> int:
    """Nombre d'items « Progressive Pikmin Limit » pour atteindre `required_limit`."""
    start = world.options.pikmin_limit_start.value
    step = world.options.pikmin_limit_step.value
    needed = math.ceil(max(0, required_limit - start) / step)
    return min(needed, pikmin_limit_item_count(start, step))


def make_rule(world: Pikmin3World, required_limit: int, required_zones: int):
    """Règle « assez de limite de Pikmin et de zones », ou None si rien n'est nécessaire."""
    player = world.player
    limit_needed = limit_items_needed(world, required_limit) if world.options.progressive_pikmin_limit else 0
    zones_needed = min(required_zones, ZONE_ITEM_COUNT) if world.options.progressive_zones else 0
    if limit_needed == 0 and zones_needed == 0:
        return None
    return lambda state: (state.has(PROGRESSIVE_PIKMIN_LIMIT, player, limit_needed)
                          and state.has(PROGRESSIVE_ZONE, player, zones_needed))


def set_all_rules(world: Pikmin3World) -> None:
    player = world.player
    options = world.options

    # Règles des checks : limite de Pikmin et zones minimales.
    for data in locations.enabled_locations(world):
        rule = make_rule(world, data.required_limit, data.required_zones)
        if rule is not None:
            set_rule(world.get_location(data.name), rule)

    # Victoire : mêmes besoins que les checks correspondants à l'objectif.
    fruits_required = options.fruits_required.value
    if options.goal == options.goal.option_final_boss:
        # Boss final : toutes les zones (la dernière est celle du boss) et la limite de Pikmin maximale,
        # en plus des fruits demandés.
        goal_rule = make_rule(world, 100, ZONE_ITEM_COUNT)
    elif options.goal == options.goal.option_fruits:
        goal_rule = make_rule(world, locations.fruit_required_limit(fruits_required),
                              locations.fruit_required_zones(fruits_required))
    else:
        population = options.population_required.value
        goal_rule = make_rule(world, locations.population_required_limit(population),
                              locations.population_required_zones(population))
    if goal_rule is not None:
        set_rule(world.get_location("Goal Reached"), goal_rule)

    world.multiworld.completion_condition[player] = lambda state: state.has("Victory", player)
