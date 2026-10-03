"""
BÊTA : journal des découvertes.

À chaque passage, le client compare les zones de memory_map.DISCOVERY_REGIONS avec le passage précédent
et note chaque octet qui change (bits allumés / éteints), avec le jour et la dernière note du joueur (/note).
Les octets qui changent trop souvent (minuteurs, positions…) sont mis de côté automatiquement.
Le journal est écrit dans un fichier texte, à relire après la partie pour identifier de nouveaux items et checks.
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from typing import Optional

from ..data import memory_map as mm

# Un octet qui change plus de NOISE_CHANGES fois en NOISE_WINDOW secondes est considéré comme du bruit.
NOISE_CHANGES = 4
NOISE_WINDOW = 60.0
RECENT_SIZE = 200
# Une note du joueur accompagne les découvertes pendant ce délai (secondes).
NOTE_LIFETIME = 180.0


def _bits(value: int) -> list[int]:
    return [bit for bit in range(8) if value & (1 << bit)]


def _in(offset: int, start: int, size: int) -> bool:
    return start <= offset < start + size


def describe(offset: int, old: int, new: int) -> str:
    """Sens connu (ou supposé) d'un changement, d'après la carte mémoire."""
    turned_on = new & ~old
    if _in(offset, mm.STATE_FRUIT_BITS, mm.STATE_FRUIT_BITS_SIZE):
        return "fruit pressé ✅"
    if _in(offset, mm.STATE_FRUIT_TYPE_COUNT, 4):
        return "sortes de fruits ✅"
    if _in(offset, mm.STATE_KEY_ITEM_BITS, 4):
        # Mot big-endian : l'octet +3 porte les bits 0–7 du mot.
        shift = (mm.STATE_KEY_ITEM_BITS + 3 - offset) * 8
        names = []
        for bit in _bits(turned_on):
            mask = 1 << (bit + shift)
            names.append(mm.KEY_ITEM_BITS.get(mask, f"objet inconnu 0x{mask:X} ❓"))
        return "objet important : " + (", ".join(names) if names else "bit éteint")
    if offset == mm.STATE_ONION_BITS:
        names = [name + (" (bit vu seulement en le forçant 🔶)" if slot in mm.ONION_SLOTS_UNVERIFIED else " ✅")
                 for slot, (name, mask) in mm.ONION_SLOTS.items() if turned_on & mask]
        unknown = turned_on & ~sum(mask for _, mask in mm.ONION_SLOTS.values())
        text = "Oignon découvert : " + (", ".join(names) if names else "?")
        return text + (f" + bits inconnus 0x{unknown:02X} ❓" if unknown else "")
    if offset == mm.STATE_UNITE_ONYON:
        return "Oignon fusionné (UniteOnyon) 🔶"
    if offset == mm.STATE_OPEN_AREA_FLAG:
        return "zone ouverte (OpenAreaFlag) : " + ", ".join(mm.AREA_BITS.get(b, f"bit {b}") for b in _bits(turned_on)) + " ✅"
    if offset == mm.STATE_SEEN_AREA_FLAG:
        return f"zone vue (SeenAreaFlag) : bits {_bits(turned_on)} 🔶"
    if _in(offset, mm.STATE_SPRAY_COUNT, 4):
        return "sprays ✅"
    if _in(offset, mm.STATE_BERRY_COUNT, 4):
        return "baies ✅"
    if _in(offset, mm.STATE_STORY_FLAGS, mm.NOTES_SET_SIZE):
        return "étape d'histoire (ensemble F) 🔶"
    for key, start in mm.NOTE_SETS.items():
        if _in(offset, start, mm.NOTES_SET_SIZE):
            return "note d'Olimar (ensemble D) ✅" if key == "D" else f"note (ensemble {key}) 🔶"
    return "inconnu ❓"


@dataclass
class Discovery:
    clock: str
    day: int
    region: str
    offset: int
    old: int
    new: int
    meaning: str
    note: str

    def line(self) -> str:
        on, off = _bits(self.new & ~self.old), _bits(self.old & ~self.new)
        text = (f"{self.clock} | jour {self.day} | {self.region} | état+0x{self.offset:04X} : "
                f"0x{self.old:02X} -> 0x{self.new:02X} | allumés {on} éteints {off} | {self.meaning}")
        return text + (f" | note : {self.note}" if self.note else "")


class DiscoveryTracker:
    def __init__(self, log_path: Optional[str]) -> None:
        self.log_path = log_path
        self.state_address: Optional[int] = None
        self.previous: Optional[dict[int, bytes]] = None
        self.change_times: dict[int, deque[float]] = {}
        self.noisy: set[int] = set()
        self.recent: deque[Discovery] = deque(maxlen=RECENT_SIZE)
        self.note_text = ""
        self.note_time = 0.0
        self.ignored = {mm.STATE_GAMEPAD_BADGE}

    def reset(self) -> None:
        """Nouvelle base de comparaison (reconnexion, jeu relancé…)."""
        self.state_address = None
        self.previous = None

    def _write(self, text: str) -> None:
        if not self.log_path:
            return
        try:
            with open(self.log_path, "a", encoding="utf-8") as handle:
                handle.write(text + "\n")
        except OSError:
            pass

    def add_note(self, text: str, day: Optional[int]) -> None:
        """Note du joueur (« j'ai trouvé l'Oignon bleu ») : rattachée aux découvertes qui suivent."""
        self.note_text = text
        self.note_time = time.monotonic()
        self._write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | jour {day if day is not None else '?'} | NOTE : {text}")

    def _is_noise(self, offset: int, now: float) -> bool:
        if offset in self.noisy:
            return True
        times = self.change_times.setdefault(offset, deque())
        times.append(now)
        while times and now - times[0] > NOISE_WINDOW:
            times.popleft()
        if len(times) > NOISE_CHANGES:
            self.noisy.add(offset)
            self._write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | état+0x{offset:04X} écarté (change trop souvent)")
            return True
        return False

    def update(self, state_address: int, day: int, regions: dict[int, bytes]) -> list[Discovery]:
        """Compare avec le passage précédent ; renvoie les nouvelles découvertes."""
        if state_address != self.state_address or self.previous is None:
            self.state_address = state_address
            self.previous = regions
            self._write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | jour {day} | début de la surveillance")
            return []
        now = time.monotonic()
        if self.note_text and now - self.note_time > NOTE_LIFETIME:
            self.note_text = ""
        found: list[Discovery] = []
        names = {offset: name for name, offset, _ in mm.DISCOVERY_REGIONS}
        for start, data in regions.items():
            before = self.previous.get(start)
            if before is None or before == data:
                continue
            for index, (old, new) in enumerate(zip(before, data)):
                offset = start + index
                if old == new or offset in self.ignored or self._is_noise(offset, now):
                    continue
                found.append(Discovery(time.strftime("%Y-%m-%d %H:%M:%S"), day, names[start], offset, old, new,
                                       describe(offset, old, new), self.note_text))
        self.previous = regions
        for discovery in found:
            self.recent.append(discovery)
            self._write(discovery.line())
        return found
