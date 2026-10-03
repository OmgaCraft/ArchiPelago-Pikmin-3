import unittest
from dataclasses import replace

from ..client.events import CheckEventTracker
from ..client.game_interface import GameSnapshot
from ..locations import LOCATION_NAME_TO_ID


def snapshot(**changes) -> GameSnapshot:
    base = GameSnapshot(
        state_address=0x34A4D75C, day=13, juice=12.5, fruit_bits=bytes(40), fruit_type_count=12,
        key_item_bits=0x0A, onion_bits=0x88, onion_counts=[100] + [0] * 14, field=0,
        note_set_bits={key: bytes(32) for key in "ABCD"}, story_bits=bytes(32), spray_count=0, berry_count=0,
    )
    return replace(base, **changes)


class TestCheckEvents(unittest.TestCase):
    def test_first_snapshot_is_a_summary(self) -> None:
        events = CheckEventTracker().update(snapshot())
        self.assertEqual(len(events), 1)
        self.assertIsNone(events[0].location)
        self.assertIn("Partie lue", events[0].message)

    def test_every_check_event_matches_a_location(self) -> None:
        tracker = CheckEventTracker()
        tracker.update(snapshot())
        after = snapshot(
            day=14,
            fruit_bits=bytes([0x01]) + bytes(39),
            fruit_type_count=13,
            key_item_bits=0x0A | 0x10 | 0x80 | 0x100,
            onion_bits=0x88 | 0x04 | 0x20 | 0x10,
            onion_counts=[160] + [0] * 14,
            note_set_bits={"A": bytes([0x03]) + bytes(31), "B": bytes(32), "C": bytes([0x01]) + bytes(31),
                           "D": bytes([0x01]) + bytes(31)},
            story_bits=bytes([0x01]) + bytes(31),
            spray_count=1,
        )
        events = tracker.update(after, milestones=[50, 100, 150, 200])
        messages = [event.message for event in events]
        for event in events:
            if event.location is not None:
                self.assertIn(event.location, LOCATION_NAME_TO_ID, event.message)
        locations = {event.location for event in events}
        for expected in ("Reach Day 14", "Fruit 1", "Fruit Kind 13", "Obtain Anti-Electrifier", "Obtain Dodge Whistle",
                         "Discover Blue Onion", "Discover Yellow Onion", "Notes A #1", "Notes A #2", "Notes C #1",
                         "Olimar Note 1", "Story Event 1", "Population 150"):
            self.assertIn(expected, locations)
        self.assertNotIn("Population 100", locations)  # déjà atteinte au premier instantané
        self.assertTrue(any("Note « Pikmin-ology » obtenue (ensemble A, n°2)" == m for m in messages))
        self.assertTrue(any("Objet inconnu obtenu (bit 0x100)" == m for m in messages))
        self.assertTrue(any("vu seulement en le forçant" in m for m in messages))  # Oignon bleu (forcé)
        self.assertTrue(any("Pikmin blancs" in m for m in messages))  # bit 0x10 = blancs, jamais un check

    def test_population_milestone_announced_once(self) -> None:
        tracker = CheckEventTracker()
        tracker.update(snapshot(onion_counts=[140] + [0] * 14))
        first = tracker.update(snapshot(onion_counts=[160] + [0] * 14), milestones=[150])
        tracker.update(snapshot(onion_counts=[140] + [0] * 14), milestones=[150])  # Pikmin perdus
        again = tracker.update(snapshot(onion_counts=[160] + [0] * 14), milestones=[150])
        self.assertEqual([event.location for event in first], ["Population 150"])
        self.assertEqual(again, [])

    def test_new_area_is_announced(self) -> None:
        tracker = CheckEventTracker()
        tracker.update(snapshot(open_areas=0x07))
        events = tracker.update(snapshot(open_areas=0x0F))
        self.assertEqual([event.message for event in events], ["Nouvelle zone ouverte : Twilight River"])

    def test_reload_is_reported_without_checks(self) -> None:
        tracker = CheckEventTracker()
        tracker.update(snapshot(day=14))
        events = tracker.update(snapshot(day=13))
        self.assertEqual(len(events), 1)
        self.assertIn("Partie rechargée", events[0].message)
