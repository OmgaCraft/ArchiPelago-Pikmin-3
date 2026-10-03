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
    onion_counts: list[int]       # [type * 3 + maturité] ; 0 pour les types absents de ONION_SLOTS (non lus)
    field: Optional[int]          # None si le gestionnaire des Pikmin n'est pas lisible
    note_set_bits: dict[str, bytes]   # BÊTA : ensemble de notes ("A".."D") -> bits
    story_bits: bytes                 # BÊTA : ensemble F, étapes d'histoire
    spray_count: int
    berry_count: int
    open_areas: int = 0               # BÊTA : OpenAreaFlag (zones ouvertes)
    merged_onions: int = 0            # BÊTA : UniteOnyon (Oignons fusionnés)

    @property
    def fruits_juiced(self) -> int:
        return popcount(self.fruit_bits)

    @property
    def note_counts(self) -> dict[str, int]:
        return {key: popcount(bits) for key, bits in self.note_set_bits.items()}

    @property
    def olimar_notes(self) -> int:
        return popcount(self.note_set_bits["D"])

    @property
    def story_events(self) -> int:
        return popcount(self.story_bits)

    def onion_discovered(self, slot: int) -> bool:
        return bool(self.onion_bits & mm.ONION_SLOTS[slot][1])

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

    # Pikmin des Oignons, par type : seuls les types connus sont lus (jamais les blancs, type 4).
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
        onion_counts=onion_counts,
        field=field,
        note_set_bits={key: mem.read(state + offset, mm.NOTES_SET_SIZE) for key, offset in mm.NOTE_SETS.items()},
        story_bits=mem.read(state + mm.STATE_STORY_FLAGS, mm.NOTES_SET_SIZE),
        spray_count=mem.read_u32(state + mm.STATE_SPRAY_COUNT),
        berry_count=mem.read_u32(state + mm.STATE_BERRY_COUNT),
        open_areas=mem.read_u8(state + mm.STATE_OPEN_AREA_FLAG),
        merged_onions=mem.read_u8(state + mm.STATE_UNITE_ONYON),
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
        raise ValueError(f"type de Pikmin {slot} refusé (inconnu, ou blancs : plantage)")
    address = snapshot.state_address + mm.STATE_ONION_COUNTS + slot * mm.ONION_SLOT_STRIDE
    mem.write_u32(address, mem.read_u32(address) + amount)


def add_sprays(mem: CemuMemory, snapshot: GameSnapshot, amount: int) -> None:
    address = snapshot.state_address + mm.STATE_SPRAY_COUNT
    mem.write_u32(address, mem.read_u32(address) + amount)


def add_berries(mem: CemuMemory, snapshot: GameSnapshot, amount: int) -> int:
    """BÊTA : ajoute des baies ultra-épicées. Renvoie le nouveau nombre."""
    address = snapshot.state_address + mm.STATE_BERRY_COUNT
    value = mem.read_u32(address) + amount
    mem.write_u32(address, value)
    return value


def read_regions(mem: CemuMemory, state_address: int) -> dict[int, bytes]:
    """BÊTA : contenu des zones surveillées par le journal des découvertes (décalage -> octets)."""
    return {offset: mem.read(state_address + offset, size) for _, offset, size in mm.DISCOVERY_REGIONS}
