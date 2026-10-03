"""
BÊTA : console des checks.

Compare deux instantanés successifs de la partie et produit une phrase lisible pour chaque check accompli
(« Note « Pikmin-ology » obtenue (ensemble A, n°21) »), avec le nom du check Archipelago correspondant.
Sans dépendance à Archipelago : utilisé par le client (onglet « Checks ») et par beta/console_checks.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from ..data import check_names as names
from ..data import memory_map as mm
from .game_interface import GameSnapshot

# Paliers de population affichés quand on ne connaît pas ceux de la partie (console sans serveur).
DEFAULT_POPULATION_MILESTONES = tuple(range(50, 1001, 50))


@dataclass
class CheckEvent:
    category: str              # fruit, sorte, oignon, objet, note, histoire, jour, population, info
    message: str               # phrase en français
    location: Optional[str]    # nom du check Archipelago (None si ce n'est pas un check)


def _new_range(before: int, after: int) -> range:
    return range(before + 1, after + 1)


class CheckEventTracker:
    def __init__(self) -> None:
        self.previous: Optional[GameSnapshot] = None
        self.best_population = 0

    def reset(self) -> None:
        self.previous = None
        self.best_population = 0

    def summary(self, snap: GameSnapshot) -> str:
        """Résumé de départ, affiché à la première lecture de la partie."""
        onions = [names.ONION_LABELS[name] for slot, (name, _) in mm.ONION_SLOTS.items() if snap.onion_discovered(slot)]
        objects = [name for bit, name in mm.KEY_ITEM_BITS.items() if snap.key_item_bits & bit]
        notes = ", ".join(f"{names.NOTE_SET_LABELS[key]} {count}" for key, count in snap.note_counts.items())
        return (f"Partie lue : jour {snap.day}, {snap.fruits_juiced} fruits pressés ({snap.fruit_type_count} sortes), "
                f"population {snap.population}, Oignons {', '.join(onions) or 'aucun'}, "
                f"objets {', '.join(objects) or 'aucun'}, notes : {notes}, étapes d'histoire {snap.story_events}")

    def update(self, snap: GameSnapshot, milestones: Optional[Iterable[int]] = None) -> list[CheckEvent]:
        previous, self.previous = self.previous, snap
        if previous is None or previous.state_address != snap.state_address:
            self.best_population = snap.population
            return [CheckEvent("info", self.summary(snap), None)]
        if snap.day < previous.day or snap.fruits_juiced < previous.fruits_juiced:
            self.best_population = snap.population
            return [CheckEvent("info", "Partie rechargée : " + self.summary(snap), None)]

        events: list[CheckEvent] = []
        for day in _new_range(previous.day, snap.day):
            events.append(CheckEvent("jour", f"Jour {day} atteint", names.day(day) if day >= 2 else None))
        for n in _new_range(previous.fruits_juiced, snap.fruits_juiced):
            events.append(CheckEvent("fruit", f"Fruit pressé (n°{n})", names.fruit(n)))
        for n in _new_range(previous.fruit_type_count, snap.fruit_type_count):
            events.append(CheckEvent("sorte", f"Nouvelle sorte de fruit enregistrée ({n}e sorte)", names.fruit_kind(n)))

        new_onions = snap.onion_bits & ~previous.onion_bits
        for slot, (name, mask) in mm.ONION_SLOTS.items():
            if new_onions & mask:
                doubt = " (bit vu seulement en le forçant 🔶)" if slot in mm.ONION_SLOTS_UNVERIFIED else ""
                location = names.onion(slot) if slot != mm.RED_SLOT else None
                events.append(CheckEvent("oignon", f"Oignon {names.ONION_LABELS[name]} découvert{doubt}", location))
        unknown_onions = new_onions & ~sum(mask for _, mask in mm.ONION_SLOTS.values())
        white = unknown_onions & (1 << mm.WHITE_TYPE)
        if white:
            events.append(CheckEvent("oignon", "Bit des Pikmin blancs allumé (0x10) : ne pas en sortir (plantage)", None))
        if unknown_onions & ~white:
            events.append(CheckEvent("oignon", f"Bit d'Oignon inconnu allumé (0x{unknown_onions & ~white:02X})", None))

        new_items = snap.key_item_bits & ~previous.key_item_bits
        for bit in range(32):
            mask = 1 << bit
            if new_items & mask:
                if mask in mm.KEY_ITEM_BITS:
                    events.append(CheckEvent("objet", f"Objet obtenu : {mm.KEY_ITEM_BITS[mask]}", names.key_item(mask)))
                else:
                    events.append(CheckEvent("objet", f"Objet inconnu obtenu (bit 0x{mask:X})", None))

        before_notes, after_notes = previous.note_counts, snap.note_counts
        for key, count in after_notes.items():
            for n in _new_range(before_notes.get(key, 0), count):
                label = names.NOTE_SET_LABELS[key]
                events.append(CheckEvent("note", f"Note « {label} » obtenue (ensemble {key}, n°{n})", names.note(key, n)))

        for n in _new_range(previous.story_events, snap.story_events):
            events.append(CheckEvent("histoire", f"Étape d'histoire franchie (n°{n})", names.story_event(n)))

        # La population baisse pendant la journée (Pikmin perdus) : on n'annonce chaque palier qu'une fois.
        if snap.population > self.best_population:
            for value in sorted(milestones or DEFAULT_POPULATION_MILESTONES):
                if self.best_population < value <= snap.population:
                    events.append(CheckEvent("population", f"Population {value} atteinte", names.population(value)))
            self.best_population = snap.population

        new_areas = snap.open_areas & ~previous.open_areas
        for bit in range(8):
            if new_areas & (1 << bit):
                name = mm.AREA_BITS.get(bit, f"zone n°{bit + 1}")
                events.append(CheckEvent("zone", f"Nouvelle zone ouverte : {name}", None))

        if snap.spray_count > previous.spray_count:
            events.append(CheckEvent("info", f"Spray ultra-épicé obtenu (total {snap.spray_count})", None))
        return events
