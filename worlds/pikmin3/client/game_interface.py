"""
Lecture de l'état de Pikmin 3 et application des items, à partir de la carte mémoire (data/memory_map.py).

Toutes les lectures passent par `read_snapshot`, qui renvoie None dès qu'une valeur est incohérente
(menu, chargement, mode Mission/Bingo…) : le client ne fait alors rien.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..data import memory_map as mm
from .cemu_memory import CemuMemory, MemoryError_

HEAP_MIN = 0x10000000
HEAP_MAX = 0x50000000


def popcount(data: bytes) -> int:
    return sum(bin(byte).count("1") for byte in data)


def _is_heap_pointer(value: int) -> bool:
    return HEAP_MIN <= value < HEAP_MAX


@dataclass
class GameSnapshot:
    state_address: int
    day: int
    juice: float
    fruit_bits: bytes
    fruit_type_count: int
    key_item_bits: int
    onion_bits: int
    open_areas: int               # OpenAreaFlag : bit n = zone n ouverte
    onion_counts: list[int]       # [type * 3 + maturité] ; 0 pour les types absents de ONION_SLOTS (non lus)
    field: Optional[int]          # None si le gestionnaire des Pikmin n'est pas lisible
    note_categories: list[bytes]  # catégorie c (A = 0 … G = 6) : 256 bits, note n° n = bit n
    onion_merged: int = 0         # « UniteOnyon » : Oignons fusionnés (même codage que onion_bits)

    @property
    def fruits_juiced(self) -> int:
        return popcount(self.fruit_bits)

    def notes_in(self, categories: tuple[int, ...]) -> int:
        return sum(popcount(self.note_categories[c]) for c in categories)

    @property
    def tutorial_notes(self) -> int:
        return self.notes_in(mm.TUTORIAL_NOTE_CATEGORIES)

    @property
    def olimar_notes(self) -> int:
        return self.notes_in(mm.OLIMAR_NOTE_CATEGORIES)

    @property
    def secret_memos(self) -> int:
        return self.notes_in(mm.SECRET_MEMO_CATEGORIES)

    @property
    def population(self) -> int:
        return sum(self.onion_counts) + (self.field or 0)


def read_snapshot(mem: CemuMemory) -> Optional[GameSnapshot]:
    """État courant, ou None si le jeu n'est pas dans une partie « Histoire » lisible."""
    game_data = mem.read_u32(mm.GAME_DATA_PTR)
    state = mem.read_u32(mm.STATE_OBJECT_PTR)
    if not (_is_heap_pointer(game_data) and _is_heap_pointer(state)):
        return None
    if mem.read_u32(game_data + mm.GAME_DATA_MODE) != mm.MODE_STORY:
        return None

    day = mem.read_u32(state + mm.STATE_DAY)
    juice = mem.read_f32(state + mm.STATE_JUICE)
    if not (1 <= day <= 999) or not (0.0 <= juice <= mm.JUICE_MAX):
        return None

    onion_counts = [0] * ((max(mm.ONION_SLOTS) + 1) * mm.ONION_MATURITIES)
    for slot in mm.ONION_SLOTS:
        for maturity in range(mm.ONION_MATURITIES):
            count = mem.read_u32(state + mm.STATE_ONION_COUNTS + slot * mm.ONION_SLOT_STRIDE + maturity * 4)
            if count > 10000:
                return None
            onion_counts[slot * mm.ONION_MATURITIES + maturity] = count

    field: Optional[int] = None
    manager = mem.read_u32(mm.PIKMIN_MANAGER_PTR)
    if _is_heap_pointer(manager):
        value = mem.read_u32(manager + mm.PIKMIN_FIELD_TOTAL)
        if 0 <= value <= mm.FIELD_LIMIT_VANILLA:
            field = value

    return GameSnapshot(
        state_address=state,
        day=day,
        juice=juice,
        fruit_bits=mem.read(state + mm.STATE_FRUIT_BITS, mm.STATE_FRUIT_BITS_SIZE),
        fruit_type_count=mem.read_u32(state + mm.STATE_FRUIT_TYPE_COUNT),
        key_item_bits=mem.read_u32(state + mm.STATE_KEY_ITEM_BITS),
        onion_bits=mem.read_u8(state + mm.STATE_ONION_BITS),
        open_areas=mem.read_u8(state + mm.STATE_OPEN_AREA_FLAG),
        onion_counts=onion_counts,
        field=field,
        note_categories=[mem.read(state + mm.STATE_NOTE_CATEGORIES + c * mm.NOTES_SET_SIZE, mm.NOTES_SET_SIZE)
                         for c in range(mm.NOTE_CATEGORY_COUNT)],
        onion_merged=mem.read_u8(state + mm.STATE_ONION_MERGED),
    )


# --------------------------------------------------------------------------
# Boîte aux lettres du graphic pack
# --------------------------------------------------------------------------

def mailbox_valid(mem: CemuMemory, address: int) -> bool:
    """Vrai si la boîte aux lettres du graphic pack (bonne version) se trouve à `address`."""
    try:
        if mem.read(address, len(mm.MAILBOX_SIGNATURE)) != mm.MAILBOX_SIGNATURE:
            return False
        return mem.read_u32(address + mm.MAILBOX_VERSION_OFFSET) == mm.MAILBOX_VERSION
    except MemoryError_:
        return False


def find_mailbox(mem: CemuMemory) -> Optional[int]:
    """Adresse de la boîte aux lettres, ou None si le graphic pack Archipelago n'est pas actif.

    Cemu place les code caves les uns après les autres à partir de 0x01800000 : si d'autres packs avec
    code cave sont actifs, la boîte aux lettres est plus loin. On cherche donc la signature.
    """
    if mailbox_valid(mem, mm.MAILBOX_ADDRESS):
        return mm.MAILBOX_ADDRESS
    page = 0x1000
    for chunk_address in range(mm.MAILBOX_ADDRESS, mm.MAILBOX_ADDRESS + mm.MAILBOX_SEARCH_SIZE, page):
        try:
            chunk = mem.read(chunk_address, page)
        except MemoryError_:
            return None
        offset = chunk.find(mm.MAILBOX_SIGNATURE)
        while offset != -1:
            if offset % 4 == 0 and mailbox_valid(mem, chunk_address + offset):
                return chunk_address + offset
            offset = chunk.find(mm.MAILBOX_SIGNATURE, offset + 1)
    return None


def write_mailbox(mem: CemuMemory, address: int, no_fruit_juice: bool, pikmin_limit: int) -> None:
    flags = mm.MAILBOX_FLAG_NO_FRUIT_JUICE if no_fruit_juice else 0
    mem.write_u32(address + mm.MAILBOX_FLAGS_OFFSET, flags)
    mem.write_u32(address + mm.MAILBOX_PIKMIN_LIMIT_OFFSET, max(1, min(mm.FIELD_LIMIT_VANILLA, pikmin_limit)))


def consume_game_restart(mem: CemuMemory, address: int) -> bool:
    """Vrai si le jeu a été relancé depuis le dernier passage (marqueur à 0), puis pose le marqueur."""
    marker_address = address + mm.MAILBOX_CLIENT_MARKER_OFFSET
    if mem.read_u32(marker_address) == mm.MAILBOX_CLIENT_MARKER:
        return False
    mem.write_u32(marker_address, mm.MAILBOX_CLIENT_MARKER)
    return True


# --------------------------------------------------------------------------
# Application des items (sur l'objet d'état d'un instantané valide)
# --------------------------------------------------------------------------

def add_juice(mem: CemuMemory, snapshot: GameSnapshot, amount: float, minimum: float = 0.0) -> float:
    """Ajoute (ou retire) du jus, borné entre `minimum` et le plafond du jeu. Renvoie la nouvelle valeur."""
    address = snapshot.state_address + mm.STATE_JUICE
    value = mem.read_f32(address) + amount
    value = max(minimum, min(mm.JUICE_MAX, value))
    mem.write_f32(address, value)
    return value


def set_juice_floor(mem: CemuMemory, snapshot: GameSnapshot, floor: float) -> bool:
    """Remonte le jus à `floor` s'il est plus bas. Renvoie vrai si une écriture a eu lieu."""
    address = snapshot.state_address + mm.STATE_JUICE
    if mem.read_f32(address) < floor:
        mem.write_f32(address, floor)
        return True
    return False


def add_onion_pikmin(mem: CemuMemory, snapshot: GameSnapshot, slot: int, amount: int) -> None:
    """Ajoute des Pikmin (stade feuille) dans l'Oignon du type donné (types de ONION_SLOTS seulement)."""
    if slot not in mm.ONION_SLOTS:
        # Garde-fou : un type inconnu, ou les Pikmin blancs (type 4), font planter le jeu.
        raise ValueError(f"Type de Pikmin non autorisé : {slot}")
    address = snapshot.state_address + mm.STATE_ONION_COUNTS + slot * mm.ONION_SLOT_STRIDE
    mem.write_u32(address, mem.read_u32(address) + amount)


def unlock_pikmin_types(mem: CemuMemory, snapshot: GameSnapshot, types: tuple[int, ...]) -> list[int]:
    """Débloque les types de Pikmin donnés (Oignon découvert + fusionné). Renvoie les types nouvellement débloqués.

    À n'appeler qu'au changement de jour : un type débloqué en pleine journée fait planter le jeu à la sortie.
    """
    newly = []
    for pikmin_type in types:
        if pikmin_type not in mm.ONION_SLOTS:
            raise ValueError(f"Type de Pikmin non autorisé : {pikmin_type}")  # garde-fou (blancs, inconnus)
        bit = mm.ONION_SLOTS[pikmin_type][1]
        if snapshot.onion_bits & bit and snapshot.onion_merged & bit:
            continue
        # « Fusionné » d'abord, puis « découvert » : jamais un Oignon découvert sans être fusionné.
        merged = snapshot.state_address + mm.STATE_ONION_MERGED
        mem.write(merged, bytes([mem.read_u8(merged) | bit]))
        discovered = snapshot.state_address + mm.STATE_ONION_BITS
        mem.write(discovered, bytes([mem.read_u8(discovered) | bit]))
        newly.append(pikmin_type)
    return newly


def allowed_zone_bits(zone_items: int) -> int:
    """Zones ouvertes avec `zone_items` items « Progressive Zone » (zones de départ comprises, bits connus seuls)."""
    bits = mm.AREA_FLAGS_AT_START
    for bit in mm.PROGRESSIVE_ZONE_BITS[:zone_items]:
        bits |= bit
    return bits


def set_zones(mem: CemuMemory, snapshot: GameSnapshot, bits: int) -> tuple[int, int]:
    """Impose exactement les zones `bits` (ouvre et referme). Renvoie (bits ouverts, bits refermés)."""
    current = snapshot.open_areas
    if current == bits:
        return 0, 0
    mem.write(snapshot.state_address + mm.STATE_OPEN_AREA_FLAG, bytes([bits]))
    return bits & ~current, current & ~bits


def zone_names(bits: int) -> str:
    return ", ".join(name for bit, name in mm.ZONE_NAMES.items() if bits & bit) or f"0x{bits:02X}"


def final_boss_defeated(mem: CemuMemory, snapshot: GameSnapshot) -> bool:
    """Vrai si le boss final est vaincu."""
    offset, mask = mm.FINAL_BOSS_FLAG
    return bool(mem.read_u8(snapshot.state_address + offset) & mask)


def add_sprays(mem: CemuMemory, snapshot: GameSnapshot, amount: int) -> None:
    address = snapshot.state_address + mm.STATE_SPRAY_COUNT
    mem.write_u32(address, mem.read_u32(address) + amount)
