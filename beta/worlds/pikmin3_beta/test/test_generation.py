from ..data import memory_map
from ..items import EXTRA_PIKMIN_SLOTS, FILLER_ITEM_NAMES, PROGRESSIVE_PIKMIN_LIMIT, pikmin_limit_item_count
from ..locations import fruit_kind_required_limit, fruit_required_limit
from .bases import Pikmin3TestBase


class TestDefaultOptions(Pikmin3TestBase):
    """Options par défaut de la bêta : limite progressive, objectif « 40 fruits », checks bêta activés."""

    def test_limit_items_in_pool(self) -> None:
        expected = pikmin_limit_item_count(30, 10)
        limit_items = [item for item in self.multiworld.itempool if item.name == PROGRESSIVE_PIKMIN_LIMIT]
        self.assertEqual(len(limit_items), expected)

    def test_first_fruits_need_no_item(self) -> None:
        self.assertTrue(self.can_reach_location("Fruit 1"))

    def test_last_fruit_needs_all_limit_items(self) -> None:
        self.assertEqual(fruit_required_limit(66), 100)
        self.assertFalse(self.can_reach_location("Fruit 66"))
        self.collect_by_name(PROGRESSIVE_PIKMIN_LIMIT)
        self.assertTrue(self.can_reach_location("Fruit 66"))

    def test_item_count_matches_locations(self) -> None:
        own_items = [item for item in self.multiworld.itempool if item.player == self.player]
        self.assertEqual(len(own_items), len(self.multiworld.get_unfilled_locations(self.player)))

    def test_beta_locations_exist(self) -> None:
        names = {location.name for location in self.multiworld.get_locations(self.player)}
        for expected in ("Reach Day 2", "Reach Day 20", "Fruit Kind 20", "Story Event 2",
                         "Notes A #10", "Notes B #3", "Notes C #10", "Olimar Note 2"):
            self.assertIn(expected, names)
        for unexpected in ("Reach Day 21", "Fruit Kind 21", "Story Event 3", "Notes A #11", "Olimar Note 3"):
            self.assertNotIn(unexpected, names)

    def test_days_and_tutorial_notes_need_nothing(self) -> None:
        self.assertTrue(self.can_reach_location("Reach Day 20"))
        self.assertTrue(self.can_reach_location("Notes B #3"))

    def test_last_fruit_kind_needs_limit_items(self) -> None:
        self.assertEqual(fruit_kind_required_limit(30), 100)
        self.assertFalse(self.can_reach_location("Fruit Kind 20"))

    def test_every_filler_has_a_handler(self) -> None:
        # Chaque Pikmin en plus vise un type de Pikmin connu (jamais les blancs).
        for name in FILLER_ITEM_NAMES:
            if "Pikmin" in name:
                self.assertIn(name, EXTRA_PIKMIN_SLOTS)
                self.assertIn(EXTRA_PIKMIN_SLOTS[name], memory_map.ONION_SLOTS)
                self.assertNotEqual(EXTRA_PIKMIN_SLOTS[name], memory_map.WHITE_TYPE)


class TestNoProgressiveLimit(Pikmin3TestBase):
    options = {"progressive_pikmin_limit": False}

    def test_everything_reachable_from_start(self) -> None:
        self.assertTrue(self.can_reach_location("Fruit 66"))
        self.assertNotIn(PROGRESSIVE_PIKMIN_LIMIT, {item.name for item in self.multiworld.itempool})


class TestMinimalBeta(Pikmin3TestBase):
    """Checks bêta désactivés : on retombe sur les checks de la V1."""

    options = {
        "note_checks": False,
        "day_checks": False,
        "fruit_kind_checks": False,
        "story_event_checks": False,
        "goal": "population",
        "population_required": 500,
        "population_milestone_step": 100,
        "population_milestone_max": 400,
        "trap_percentage": 50,
    }

    def test_only_v1_locations(self) -> None:
        names = {location.name for location in self.multiworld.get_locations(self.player)}
        self.assertIn("Population 400", names)
        self.assertNotIn("Population 500", names)
        self.assertFalse(any(name.startswith(("Reach Day", "Fruit Kind", "Story Event", "Notes ", "Olimar"))
                             for name in names))


class TestManyNotes(Pikmin3TestBase):
    options = {"notes_a_count": 40, "notes_b_count": 0, "notes_c_count": 40, "olimar_note_count": 40}

    def test_note_counts(self) -> None:
        names = {location.name for location in self.multiworld.get_locations(self.player)}
        self.assertIn("Notes A #40", names)
        self.assertIn("Notes C #40", names)
        self.assertIn("Olimar Note 40", names)
        self.assertFalse(any(name.startswith("Notes B") for name in names))
