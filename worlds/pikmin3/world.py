from collections.abc import Mapping
from typing import Any

from worlds.AutoWorld import World

from . import items, locations, regions, rules, web_world
from . import options as pikmin3_options  # renommé : conflit avec World.options


class Pikmin3World(World):
    """
    Pikmin 3 (Wii U, émulé par Cemu). Ramenez des fruits, découvrez les Oignons et faites grandir
    votre armée de Pikmin : chaque fruit pressé est un check, et le jus qui vous fait survivre
    arrive sous forme d'items.
    """

    game = "Pikmin 3"
    web = web_world.Pikmin3WebWorld()

    options_dataclass = pikmin3_options.Pikmin3Options
    options: pikmin3_options.Pikmin3Options

    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_to_id = items.ITEM_NAME_TO_ID
    location_name_groups = locations.LOCATION_NAME_GROUPS
    item_name_groups = items.ITEM_NAME_GROUPS

    origin_region_name = "Planet"

    def create_regions(self) -> None:
        regions.create_all_regions(self)
        locations.create_all_locations(self)

    def set_rules(self) -> None:
        rules.set_all_rules(self)

    def create_items(self) -> None:
        items.create_all_items(self)

    def create_item(self, name: str) -> items.Pikmin3Item:
        return items.create_item(self, name)

    def get_filler_item_name(self) -> str:
        return items.get_random_filler_item_name(self)

    def fill_slot_data(self) -> Mapping[str, Any]:
        # Transmis au client à chaque connexion.
        slot_data = self.options.as_dict(
            "goal", "fruits_required", "population_required", "onion_checks", "key_item_checks",
            "note_checks", "tutorial_note_count", "olimar_note_count", "secret_memo_count", "progressive_pikmin_limit",
            "pikmin_limit_start", "pikmin_limit_step", "progressive_zones", "progressive_pikmin", "juice_mode",
        )
        slot_data["population_milestones"] = locations.population_milestones(
            self.options.population_milestone_step.value, self.options.population_milestone_max.value
        )
        slot_data["world_version"] = "1.0.0"
        return slot_data
