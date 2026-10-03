from __future__ import annotations

import math
from typing import TYPE_CHECKING

from worlds.generic.Rules import set_rule

from . import locations
from .items import PROGRESSIVE_PIKMIN_LIMIT, pikmin_limit_item_count

if TYPE_CHECKING:
    from .world import Pikmin3World


def limit_items_needed(world: Pikmin3World, required_limit: int) -> int:
    """Nombre d'items « Progressive Pikmin Limit » pour atteindre `required_limit`."""
    start = world.options.pikmin_limit_start.value
    step = world.options.pikmin_limit_step.value
    needed = math.ceil(max(0, required_limit - start) / step)
    return min(needed, pikmin_limit_item_count(start, step))


def set_all_rules(world: Pikmin3World) -> None:
    player = world.player
    progressive = bool(world.options.progressive_pikmin_limit)

    # Règles des checks : chaque check demande une limite de Pikmin minimale.
    if progressive:
        for data in locations.enabled_locations(world):
            needed = limit_items_needed(world, data.required_limit)
            if needed > 0:
                set_rule(world.get_location(data.name),
                         lambda state, n=needed: state.has(PROGRESSIVE_PIKMIN_LIMIT, player, n))

    # Victoire : même besoin que le check correspondant à l'objectif.
    if world.options.goal == world.options.goal.option_fruits:
        goal_limit = locations.fruit_required_limit(world.options.fruits_required.value)
    else:
        goal_limit = locations.population_required_limit(world.options.population_required.value)
    goal_needed = limit_items_needed(world, goal_limit) if progressive else 0
    if goal_needed > 0:
        set_rule(world.get_location("Goal Reached"),
                 lambda state: state.has(PROGRESSIVE_PIKMIN_LIMIT, player, goal_needed))

    world.multiworld.completion_condition[player] = lambda state: state.has("Victory", player)
