from ..items import (PIKMIN_TYPE_ITEM_COUNT, PROGRESSIVE_PIKMIN, PROGRESSIVE_PIKMIN_LIMIT, PROGRESSIVE_ZONE,
                     ZONE_ITEM_COUNT, pikmin_limit_item_count)
from ..locations import fruit_required_limit, fruit_required_zones
from .bases import Pikmin3TestBase


class TestDefaultOptions(Pikmin3TestBase):
    """Options par défaut : limite progressive et zones activées, objectif « boss final + 40 fruits »."""

    def test_limit_items_in_pool(self) -> None:
        expected = pikmin_limit_item_count(30, 10)
        limit_items = [item for item in self.multiworld.itempool if item.name == PROGRESSIVE_PIKMIN_LIMIT]
        self.assertEqual(len(limit_items), expected)

    def test_zone_items_in_pool(self) -> None:
        zone_items = [item for item in self.multiworld.itempool if item.name == PROGRESSIVE_ZONE]
        self.assertEqual(len(zone_items), ZONE_ITEM_COUNT)

    def test_first_fruits_need_no_item(self) -> None:
        self.assertTrue(self.can_reach_location("Fruit 1"))

    def test_last_fruit_needs_limit_and_zones(self) -> None:
        self.assertEqual(fruit_required_limit(66), 100)
        self.assertEqual(fruit_required_zones(66), 2)
        self.assertFalse(self.can_reach_location("Fruit 66"))
        self.collect_by_name(PROGRESSIVE_PIKMIN_LIMIT)
        self.assertFalse(self.can_reach_location("Fruit 66"))  # zones encore fermées
        self.collect(self.get_items_by_name(PROGRESSIVE_ZONE)[:2])
        self.assertTrue(self.can_reach_location("Fruit 66"))

    def test_final_boss_needs_every_zone(self) -> None:
        self.collect_by_name(PROGRESSIVE_PIKMIN_LIMIT)
        self.collect(self.get_items_by_name(PROGRESSIVE_ZONE)[:ZONE_ITEM_COUNT - 1])
        self.assertFalse(self.can_reach_location("Goal Reached"))
        self.collect_by_name(PROGRESSIVE_ZONE)
        self.assertTrue(self.can_reach_location("Goal Reached"))

    def test_item_count_matches_locations(self) -> None:
        own_items = [item for item in self.multiworld.itempool if item.player == self.player]
        self.assertEqual(len(own_items), len(self.multiworld.get_unfilled_locations(self.player)))


class TestNoProgression(Pikmin3TestBase):
    options = {"progressive_pikmin_limit": False, "progressive_zones": False, "goal": "fruits"}

    def test_everything_reachable_from_start(self) -> None:
        self.assertTrue(self.can_reach_location("Fruit 66"))
        pool_names = {item.name for item in self.multiworld.itempool}
        self.assertNotIn(PROGRESSIVE_PIKMIN_LIMIT, pool_names)
        self.assertNotIn(PROGRESSIVE_ZONE, pool_names)


class TestZonesOnly(Pikmin3TestBase):
    options = {"progressive_pikmin_limit": False, "goal": "fruits", "fruits_required": 10}

    def test_zone_requirements(self) -> None:
        self.assertTrue(self.can_reach_location("Fruit 5"))
        self.assertFalse(self.can_reach_location("Fruit 6"))
        self.assertFalse(self.can_reach_location("Goal Reached"))
        self.collect(self.get_items_by_name(PROGRESSIVE_ZONE)[:1])
        self.assertTrue(self.can_reach_location("Fruit 15"))
        self.assertFalse(self.can_reach_location("Fruit 16"))
        self.assertTrue(self.can_reach_location("Goal Reached"))


class TestNotesMemosAndPikminTypes(Pikmin3TestBase):
    options = {
        "progressive_pikmin_limit": False,
        "goal": "fruits",
        "fruits_required": 10,
        "tutorial_note_count": 63,
        "olimar_note_count": 15,
        "secret_memo_count": 10,
        "progressive_pikmin": True,
    }

    def test_pikmin_type_items_in_pool(self) -> None:
        pikmin_items = [item for item in self.multiworld.itempool if item.name == PROGRESSIVE_PIKMIN]
        self.assertEqual(len(pikmin_items), PIKMIN_TYPE_ITEM_COUNT)
        self.assertFalse(pikmin_items[0].advancement)  # utiles, pas en logique
        names = {location.name for location in self.multiworld.get_locations(self.player)}
        self.assertNotIn("Discover Winged Onion", names)  # l'item allume lui-même le bit de l'Oignon

    def test_note_zone_requirements(self) -> None:
        self.assertTrue(self.can_reach_location("Tutorial Note 29"))
        self.assertFalse(self.can_reach_location("Tutorial Note 30"))
        self.assertTrue(self.can_reach_location("Olimar Note 1"))
        self.assertFalse(self.can_reach_location("Olimar Note 2"))
        zones = self.get_items_by_name(PROGRESSIVE_ZONE)
        self.collect(zones[:2])
        self.assertTrue(self.can_reach_location("Tutorial Note 51"))
        self.assertFalse(self.can_reach_location("Tutorial Note 52"))  # au-delà : Formidable Oak
        self.assertFalse(self.can_reach_location("Secret Memo 1"))
        self.collect(zones[2:])
        self.assertTrue(self.can_reach_location("Tutorial Note 63"))
        self.assertTrue(self.can_reach_location("Olimar Note 15"))
        self.assertTrue(self.can_reach_location("Secret Memo 10"))


class TestPopulationGoalWithNotes(Pikmin3TestBase):
    options = {
        "goal": "population",
        "population_required": 500,
        "note_checks": True,
        "tutorial_note_count": 5,
        "olimar_note_count": 2,
        "population_milestone_step": 100,
        "population_milestone_max": 400,
        "trap_percentage": 50,
    }

    def test_note_and_milestone_locations_exist(self) -> None:
        names = {location.name for location in self.multiworld.get_locations(self.player)}
        self.assertIn("Tutorial Note 5", names)
        self.assertNotIn("Tutorial Note 6", names)
        self.assertIn("Olimar Note 2", names)
        self.assertIn("Population 400", names)
        self.assertNotIn("Population 500", names)
