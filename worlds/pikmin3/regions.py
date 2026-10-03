from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Region

if TYPE_CHECKING:
    from .world import Pikmin3World

# V1 : une seule région. Les zones (Tropical Wilds, Garden of Hope, Distant Tundra, Twilight River,
# Formidable Oak) deviendront des régions quand leur déblocage pourra être contrôlé (option B).


def create_all_regions(world: Pikmin3World) -> None:
    world.multiworld.regions.append(Region("Planet", world.player, world.multiworld))
