"""
Outil de Phase 0 : sonde mémoire pour Pikmin 3 sous Cemu (Windows uniquement).

Lit et écrit la mémoire émulée de la Wii U dans le processus Cemu.
La Wii U est big-endian : toutes les valeurs sont (dé)codées en big-endian.
Aucune dépendance externe : uniquement la bibliothèque standard (ctypes).

Les adresses passées en argument sont des adresses *Wii U* (« guest »),
par ex. 0x10000000. L'outil ajoute lui-même la base mémoire de Cemu.

Exemples :
    py tools/memory_probe.py info
    py tools/memory_probe.py ranges
    py tools/memory_probe.py read 0x10000000 --type u32 --count 4
    py tools/memory_probe.py hexdump 0x10000000 0x40
    py tools/memory_probe.py find 150 --type u32
    py tools/memory_probe.py refine 149
    py tools/memory_probe.py refine changed
    py tools/memory_probe.py watch 0x12345678 --type u16
    py tools/memory_probe.py snapshot avant 0x10000000 0x100000
    py tools/memory_probe.py diff avant apres --type u8 --noise repos
    py tools/memory_probe.py findptr 0x12345678 --max-offset 0x400
    py tools/memory_probe.py write 0x12345678 u16 999
"""

import argparse
import bisect
import ctypes
import json
import os
import re
import struct
import sys
import time
from array import array
from ctypes import wintypes

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

CEMU_EXE_NAME = "cemu.exe"

# Cemu réserve l'espace d'adressage complet de la Wii U (4 Gio) d'un seul bloc.
# À confirmer en Phase 0 : c'est l'hypothèse utilisée pour trouver la base.
GUEST_SPACE_SIZE = 0x1_0000_0000

# Plage scannée par défaut (MEM2, où vivent les données du jeu).
# TODO: à confirmer — affiner une fois la disposition mémoire de Pikmin 3 connue.
DEFAULT_SCAN_START = 0x1000_0000
DEFAULT_SCAN_END = 0x5000_0000

# Offsets (adresses Wii U) dont la présence en mémoire engagée rend un candidat
# de base plus crédible : zone de code des RPX et début de MEM2.
BASE_HINT_OFFSETS = (0x0200_0000, 0x1000_0000)

CHUNK_SIZE = 16 * 1024 * 1024
# Au-delà de PER_HIT_REFINE_LIMIT, « refine <valeur> » rebalaye la mémoire au lieu
# de relire chaque candidat ; les comparaisons (changed…) exigent moins de candidats.
MAX_STORED_HITS = 20_000_000
PER_HIT_REFINE_LIMIT = 200_000

STATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".probe_state")

# Types acceptés -> format struct big-endian
VALUE_TYPES = {
    "u8": ">B", "s8": ">b",
    "u16": ">H", "s16": ">h",
    "u32": ">I", "s32": ">i",
    "u64": ">Q", "s64": ">q",
    "f32": ">f", "f64": ">d",
}

# ---------------------------------------------------------------------------
# API Windows (ctypes)
# ---------------------------------------------------------------------------

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_VM_OPERATION = 0x0008
TH32CS_SNAPPROCESS = 0x0000_0002
MEM_COMMIT = 0x1000
MEM_FREE = 0x10000
PAGE_NOACCESS = 0x01
PAGE_GUARD = 0x100
USER_SPACE_END = 0x7FFF_FFFF_0000
INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", wintypes.DWORD),
        ("PartitionId", wintypes.WORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", wintypes.DWORD),
        ("Protect", wintypes.DWORD),
        ("Type", wintypes.DWORD),
    ]


class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.c_size_t),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", ctypes.c_long),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", ctypes.c_wchar * 260),
    ]


if sys.platform != "win32":
    sys.exit("memory_probe.py ne fonctionne que sous Windows.")

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

kernel32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
kernel32.CloseHandle.restype = wintypes.BOOL
kernel32.VirtualQueryEx.argtypes = (
    wintypes.HANDLE, ctypes.c_void_p, ctypes.POINTER(MEMORY_BASIC_INFORMATION), ctypes.c_size_t)
kernel32.VirtualQueryEx.restype = ctypes.c_size_t
kernel32.ReadProcessMemory.argtypes = (
    wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t))
kernel32.ReadProcessMemory.restype = wintypes.BOOL
kernel32.WriteProcessMemory.argtypes = (
    wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t))
kernel32.WriteProcessMemory.restype = wintypes.BOOL
kernel32.CreateToolhelp32Snapshot.argtypes = (wintypes.DWORD, wintypes.DWORD)
kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
kernel32.Process32FirstW.argtypes = (wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W))
kernel32.Process32FirstW.restype = wintypes.BOOL
kernel32.Process32NextW.argtypes = (wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W))
kernel32.Process32NextW.restype = wintypes.BOOL


def win_error(what):
    code = ctypes.get_last_error()
    return OSError(f"{what} a échoué (erreur Windows {code}: {ctypes.FormatError(code).strip()})")


def find_cemu_pids():
    """Retourne la liste des PID des processus Cemu.exe."""
    snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snapshot == INVALID_HANDLE_VALUE:
        raise win_error("CreateToolhelp32Snapshot")
    pids = []
    try:
        entry = PROCESSENTRY32W()
        entry.dwSize = ctypes.sizeof(PROCESSENTRY32W)
        ok = kernel32.Process32FirstW(snapshot, ctypes.byref(entry))
        while ok:
            if entry.szExeFile.lower() == CEMU_EXE_NAME:
                pids.append(entry.th32ProcessID)
            ok = kernel32.Process32NextW(snapshot, ctypes.byref(entry))
    finally:
        kernel32.CloseHandle(snapshot)
    return pids


def is_readable(mbi):
    return mbi.State == MEM_COMMIT and mbi.Protect != 0 and not (mbi.Protect & (PAGE_NOACCESS | PAGE_GUARD))


# ---------------------------------------------------------------------------
# Accès au processus hôte (adresses Windows)
# ---------------------------------------------------------------------------

class HostProcess:
    def __init__(self, pid, writable=False):
        access = PROCESS_QUERY_INFORMATION | PROCESS_VM_READ
        if writable:
            access |= PROCESS_VM_WRITE | PROCESS_VM_OPERATION
        self.pid = pid
        self.handle = kernel32.OpenProcess(access, False, pid)
        if not self.handle:
            raise win_error(f"OpenProcess(pid={pid})")

    def close(self):
        if self.handle:
            kernel32.CloseHandle(self.handle)
            self.handle = None

    def query(self, address):
        mbi = MEMORY_BASIC_INFORMATION()
        if not kernel32.VirtualQueryEx(self.handle, ctypes.c_void_p(address), ctypes.byref(mbi), ctypes.sizeof(mbi)):
            return None
        return mbi

    def regions(self, start=0, end=USER_SPACE_END):
        """Parcourt les régions mémoire de [start, end)."""
        address = start
        while address < end:
            mbi = self.query(address)
            if mbi is None:
                break
            yield mbi
            next_address = (mbi.BaseAddress or 0) + mbi.RegionSize
            if next_address <= address:
                break
            address = next_address

    def read(self, address, size):
        buffer = ctypes.create_string_buffer(size)
        done = ctypes.c_size_t(0)
        if not kernel32.ReadProcessMemory(self.handle, ctypes.c_void_p(address), buffer, size, ctypes.byref(done)):
            raise win_error(f"ReadProcessMemory(0x{address:X}, {size})")
        return buffer.raw[:done.value]

    def write(self, address, data):
        done = ctypes.c_size_t(0)
        if not kernel32.WriteProcessMemory(self.handle, ctypes.c_void_p(address), data, len(data), ctypes.byref(done)):
            raise win_error(f"WriteProcessMemory(0x{address:X}, {len(data)})")
        if done.value != len(data):
            raise OSError(f"Écriture partielle : {done.value}/{len(data)} octets")


# ---------------------------------------------------------------------------
# Recherche de la base mémoire Wii U dans Cemu
# ---------------------------------------------------------------------------

def find_guest_base_candidates(proc):
    """
    Regroupe les régions par AllocationBase et garde celles qui couvrent au moins
    4 Gio (l'espace Wii U). Chaque candidat reçoit un score de crédibilité.
    """
    allocations = {}
    for mbi in proc.regions():
        if mbi.State == MEM_FREE or not mbi.AllocationBase:
            continue
        alloc = allocations.setdefault(mbi.AllocationBase, {"end": 0, "committed": []})
        region_start = mbi.BaseAddress or 0
        region_end = region_start + mbi.RegionSize
        alloc["end"] = max(alloc["end"], region_end)
        if mbi.State == MEM_COMMIT:
            alloc["committed"].append((region_start - mbi.AllocationBase, region_end - mbi.AllocationBase))

    candidates = []
    for base, alloc in allocations.items():
        span = alloc["end"] - base
        if span < GUEST_SPACE_SIZE:
            continue
        score = 0
        if span == GUEST_SPACE_SIZE:
            score += 2
        for hint in BASE_HINT_OFFSETS:
            if any(start <= hint < end for start, end in alloc["committed"]):
                score += 1
        committed_bytes = sum(end - start for start, end in alloc["committed"])
        candidates.append({"base": base, "span": span, "score": score, "committed_bytes": committed_bytes})
    candidates.sort(key=lambda c: (-c["score"], -c["committed_bytes"]))
    return candidates


def find_base_in_logs():
    """
    Cherche la ligne « Init Wii U memory space (base: 0x...) » dans log.txt de Cemu
    (vérifié avec Cemu 2.6 : le log est réécrit à chaque démarrage de Cemu).
    """
    paths = [os.path.join(os.environ.get("APPDATA", ""), "Cemu", "log.txt")]
    found = []
    for path in paths:
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                match = re.search(r"Init Wii U memory space \(base:\s*0x([0-9A-Fa-f]+)\)", line)
                if match:
                    found.append((path, int(match.group(1), 16), line.strip()))
    return found


# ---------------------------------------------------------------------------
# Accès à la mémoire Wii U (adresses guest, big-endian)
# ---------------------------------------------------------------------------

class GuestMemory:
    def __init__(self, proc, base):
        self.proc = proc
        self.base = base

    def read(self, guest_address, size):
        return self.proc.read(self.base + guest_address, size)

    def write(self, guest_address, data):
        self.proc.write(self.base + guest_address, data)

    def read_value(self, guest_address, value_type):
        fmt = VALUE_TYPES[value_type]
        return struct.unpack(fmt, self.read(guest_address, struct.calcsize(fmt)))[0]

    def committed_ranges(self, start, end):
        """Plages Wii U lisibles dans [start, end), fusionnées."""
        merged = []
        for mbi in self.proc.regions(self.base + start, self.base + end):
            if not is_readable(mbi):
                continue
            region_start = max((mbi.BaseAddress or 0) - self.base, start)
            region_end = min((mbi.BaseAddress or 0) + mbi.RegionSize - self.base, end)
            if merged and merged[-1][1] == region_start:
                merged[-1][1] = region_end
            else:
                merged.append([region_start, region_end])
        return [(s, e) for s, e in merged]

    def iter_chunks(self, start, end, overlap):
        """
        Lit la mémoire par blocs. Chaque bloc déborde de `overlap` octets sur le
        suivant ; l'appelant ne garde que les positions < CHUNK_SIZE.
        """
        skipped = 0
        for range_start, range_end in self.committed_ranges(start, end):
            address = range_start
            while address < range_end:
                size = min(CHUNK_SIZE + overlap, range_end - address)
                try:
                    yield address, self.read(address, size)
                except OSError:
                    skipped += 1
                address += CHUNK_SIZE
        if skipped:
            print(f"[!] {skipped} bloc(s) illisible(s) ignoré(s).", file=sys.stderr)


def parse_value(text, value_type):
    return float(text) if value_type.startswith("f") else int(text, 0)


def pack_value(value, value_type):
    return struct.pack(VALUE_TYPES[value_type], value)


def format_value(value, value_type):
    if value_type.startswith("f"):
        return f"{value!r}"
    width = struct.calcsize(VALUE_TYPES[value_type]) * 2
    return f"{value} (0x{value & ((1 << (width * 4)) - 1):0{width}X})"


# ---------------------------------------------------------------------------
# État persistant (résultats de recherche, snapshots)
# ---------------------------------------------------------------------------

class SearchState:
    """
    Résultats d'une recherche (« session ») : adresses triées + dernière valeur lue.
    Stockés en binaire (array) pour tenir des millions de candidats.
    """

    def __init__(self, value_type, alignment, addresses=None, values=None):
        self.value_type = value_type
        self.alignment = alignment
        self.addresses = addresses if addresses is not None else array("I")
        self.values = values if values is not None else array("d")

    def __len__(self):
        return len(self.addresses)

    @staticmethod
    def paths(session):
        # Une recherche par « session » : permet de suivre plusieurs valeurs en parallèle.
        stem = os.path.join(STATE_DIR, f"search_{session}")
        return stem + ".json", stem + ".bin"

    def save(self, session):
        os.makedirs(STATE_DIR, exist_ok=True)
        meta_path, bin_path = self.paths(session)
        with open(bin_path, "wb") as handle:
            self.addresses.tofile(handle)
            self.values.tofile(handle)
        with open(meta_path, "w", encoding="utf-8") as handle:
            json.dump({"type": self.value_type, "alignment": self.alignment, "count": len(self)}, handle)

    @classmethod
    def load(cls, session):
        meta_path, bin_path = cls.paths(session)
        if not os.path.isfile(meta_path):
            sys.exit(f"Aucune recherche « {session} » : lance d'abord « find ».")
        with open(meta_path, "r", encoding="utf-8") as handle:
            meta = json.load(handle)
        value_type = meta["type"]
        if "hits" in meta:
            # Ancien format JSON (liste de paires [adresse, valeur]).
            alignment = struct.calcsize(VALUE_TYPES[value_type])
            return cls(value_type, alignment,
                       array("I", (address for address, _ in meta["hits"])),
                       array("d", (float(value) for _, value in meta["hits"])))
        state = cls(value_type, meta["alignment"])
        with open(bin_path, "rb") as handle:
            state.addresses.fromfile(handle, meta["count"])
            state.values.fromfile(handle, meta["count"])
        return state

    def print(self, limit=20):
        for address, value in zip(self.addresses[:limit], self.values[:limit]):
            shown = value if self.value_type.startswith("f") else int(value)
            print(f"  0x{address:08X} = {format_value(shown, self.value_type)}")
        if len(self) > limit:
            print(f"  ... et {len(self) - limit} autre(s)")


def snapshot_paths(name):
    return os.path.join(STATE_DIR, f"{name}.bin"), os.path.join(STATE_DIR, f"{name}.json")


# ---------------------------------------------------------------------------
# Commandes
# ---------------------------------------------------------------------------

def open_memory(args, writable=False):
    pids = [args.pid] if args.pid else find_cemu_pids()
    if not pids:
        sys.exit("Cemu n'est pas lancé.")
    if len(pids) > 1:
        sys.exit(f"Plusieurs Cemu trouvés {pids} : précise --pid.")
    proc = HostProcess(pids[0], writable=writable)
    if args.base is not None:
        return GuestMemory(proc, args.base)
    candidates = find_guest_base_candidates(proc)
    if not candidates:
        sys.exit("Base mémoire Wii U introuvable (aucune réservation de 4 Gio). Le jeu est-il lancé ?")
    # log.txt est réécrit à chaque démarrage de Cemu : si sa base correspond à un
    # candidat, c'est la bonne. Sinon (log d'une autre instance…), on garde le score.
    log_bases = {base for _, base, _ in find_base_in_logs()}
    for cand in candidates:
        if cand["base"] in log_bases:
            return GuestMemory(proc, cand["base"])
    best = candidates[0]
    if len(candidates) > 1 and candidates[1]["score"] == best["score"]:
        print("[!] Base ambiguë, lance « info » et précise --base.", file=sys.stderr)
    return GuestMemory(proc, best["base"])


def cmd_info(args):
    pids = [args.pid] if args.pid else find_cemu_pids()
    if not pids:
        sys.exit("Cemu n'est pas lancé.")
    print(f"Processus Cemu : {pids}")
    proc = HostProcess(pids[0])
    try:
        candidates = find_guest_base_candidates(proc)
        if not candidates:
            print("Aucune réservation de 4 Gio trouvée (le jeu n'est peut-être pas encore lancé).")
        log_bases = {base for _, base, _ in find_base_in_logs()}
        confirmed = [cand for cand in candidates if cand["base"] in log_bases]
        chosen = confirmed[0] if confirmed else (candidates[0] if candidates else None)
        for cand in candidates:
            tag = ""
            if cand is chosen:
                tag = "  <= choisie (confirmée par log.txt)" if confirmed else "  <= choisie"
            print(f"Candidat base : 0x{cand['base']:X}  taille réservée 0x{cand['span']:X}  "
                  f"engagé {cand['committed_bytes'] / 2**20:.0f} Mio  score {cand['score']}{tag}")
        for path, base, line in find_base_in_logs():
            print(f"log.txt : 0x{base:X}  ({line})")
    finally:
        proc.close()


def cmd_ranges(args):
    memory = open_memory(args)
    print(f"Base : 0x{memory.base:X}")
    for start, end in memory.committed_ranges(0, GUEST_SPACE_SIZE):
        print(f"  0x{start:08X} - 0x{end:08X}  ({(end - start) / 2**20:.2f} Mio)")


def cmd_read(args):
    memory = open_memory(args)
    size = struct.calcsize(VALUE_TYPES[args.type])
    for index in range(args.count):
        address = args.address + index * size
        print(f"0x{address:08X} = {format_value(memory.read_value(address, args.type), args.type)}")


def cmd_hexdump(args):
    memory = open_memory(args)
    data = memory.read(args.address, args.length)
    for offset in range(0, len(data), 16):
        line = data[offset:offset + 16]
        text = "".join(chr(b) if 32 <= b < 127 else "." for b in line)
        print(f"0x{args.address + offset:08X}  {line.hex(' ').upper():<47}  {text}")


def cmd_write(args):
    memory = open_memory(args, writable=True)
    value = parse_value(args.value, args.type)
    old = memory.read_value(args.address, args.type)
    print(f"0x{args.address:08X} : {format_value(old, args.type)} -> {format_value(value, args.type)}")
    if not args.yes and input("Confirmer l'écriture ? [o/N] ").strip().lower() not in ("o", "oui", "y"):
        print("Annulé.")
        return
    memory.write(args.address, pack_value(value, args.type))
    print(f"Relu : {format_value(memory.read_value(args.address, args.type), args.type)}")


def cmd_watch(args):
    memory = open_memory(args)
    last = None
    print(f"Surveillance de 0x{args.address:08X} ({args.type}), Ctrl+C pour arrêter.")
    try:
        while True:
            value = memory.read_value(args.address, args.type)
            if value != last:
                print(f"[{time.strftime('%H:%M:%S')}] {format_value(value, args.type)}")
                last = value
            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass


def scan_for(memory, pattern, start, end, alignment):
    """Génère, dans l'ordre croissant, les adresses où `pattern` apparaît."""
    for chunk_address, data in memory.iter_chunks(start, end, len(pattern) - 1):
        position = data.find(pattern)
        while 0 <= position < CHUNK_SIZE:
            address = chunk_address + position
            if address % alignment == 0:
                yield address
            position = data.find(pattern, position + 1)


def cmd_find(args):
    memory = open_memory(args)
    value = parse_value(args.value, args.type)
    pattern = pack_value(value, args.type)
    state = SearchState(args.type, 1 if args.unaligned else len(pattern))
    for address in scan_for(memory, pattern, args.start, args.end, state.alignment):
        state.addresses.append(address)
        if len(state) > MAX_STORED_HITS:
            sys.exit(f"Plus de {MAX_STORED_HITS} résultats : choisis une valeur plus distinctive.")
    state.values = array("d", [float(value)]) * len(state)
    state.save(args.session)
    print(f"{len(state)} résultat(s) pour {format_value(value, args.type)}.")
    state.print()


def cmd_refine(args):
    state = SearchState.load(args.session)
    memory = open_memory(args)
    fmt = VALUE_TYPES[state.value_type]
    size = struct.calcsize(fmt)
    keywords = {
        "changed": lambda old, new: new != old,
        "unchanged": lambda old, new: new == old,
        "increased": lambda old, new: new > old,
        "decreased": lambda old, new: new < old,
    }
    target_bytes = None
    if args.condition not in keywords:
        target_bytes = pack_value(parse_value(args.condition, state.value_type), state.value_type)

    result = SearchState(state.value_type, state.alignment)
    if target_bytes is not None and len(state) > PER_HIT_REFINE_LIMIT:
        # Trop de candidats pour les relire un par un : on rebalaye la mémoire pour
        # la nouvelle valeur et on ne garde que les adresses déjà candidates.
        end = state.addresses[-1] + size if len(state) else 0
        for address in scan_for(memory, target_bytes, state.addresses[0] if len(state) else 0, end, state.alignment):
            index = bisect.bisect_left(state.addresses, address)
            if index < len(state) and state.addresses[index] == address:
                result.addresses.append(address)
        result.values = array("d", [float(struct.unpack(fmt, target_bytes)[0])]) * len(result)
    else:
        if target_bytes is None and len(state) > PER_HIT_REFINE_LIMIT:
            sys.exit(f"Plus de {PER_HIT_REFINE_LIMIT} candidats : filtre d'abord avec une valeur exacte.")
        for address, old in zip(state.addresses, state.values):
            try:
                raw = memory.read(address, size)
            except OSError:
                continue
            if target_bytes is not None:
                keep = raw == target_bytes
            else:
                keep = keywords[args.condition](old, struct.unpack(fmt, raw)[0])
            if keep:
                result.addresses.append(address)
                result.values.append(float(struct.unpack(fmt, raw)[0]))
    result.save(args.session)
    print(f"{len(state)} -> {len(result)} résultat(s).")
    result.print()


def cmd_snapshot(args):
    memory = open_memory(args)
    data = memory.read(args.address, args.length)
    os.makedirs(STATE_DIR, exist_ok=True)
    bin_path, meta_path = snapshot_paths(args.name)
    with open(bin_path, "wb") as handle:
        handle.write(data)
    with open(meta_path, "w", encoding="utf-8") as handle:
        json.dump({"address": args.address, "length": len(data), "time": time.time()}, handle)
    print(f"Snapshot « {args.name} » : 0x{args.address:08X} + 0x{len(data):X} octets.")


def load_snapshot(name):
    bin_path, meta_path = snapshot_paths(name)
    if not os.path.isfile(bin_path):
        sys.exit(f"Snapshot « {name} » introuvable.")
    with open(meta_path, "r", encoding="utf-8") as handle:
        meta = json.load(handle)
    with open(bin_path, "rb") as handle:
        return meta["address"], handle.read()


def cmd_diff(args):
    address_a, data_a = load_snapshot(args.before)
    address_b, data_b = load_snapshot(args.after)
    if address_a != address_b or len(data_a) != len(data_b):
        sys.exit("Les deux snapshots ne couvrent pas la même plage.")
    # Snapshot « bruit » : pris entre avant et après SANS rien faire en jeu.
    # Tout ce qui a changé entre « avant » et « bruit » (minuteurs, animations…) est ignoré.
    data_noise = None
    if args.noise:
        address_n, data_noise = load_snapshot(args.noise)
        if address_n != address_a or len(data_noise) != len(data_a):
            sys.exit("Le snapshot de bruit ne couvre pas la même plage.")
    fmt = VALUE_TYPES[args.type]
    size = struct.calcsize(fmt)
    changes = 0
    for offset in range(0, len(data_a) - size + 1, size):
        old_bytes = data_a[offset:offset + size]
        new_bytes = data_b[offset:offset + size]
        if data_noise is not None and data_noise[offset:offset + size] != old_bytes:
            continue
        if old_bytes != new_bytes:
            changes += 1
            if changes <= args.limit:
                old = struct.unpack(fmt, old_bytes)[0]
                new = struct.unpack(fmt, new_bytes)[0]
                print(f"  0x{address_a + offset:08X} : {format_value(old, args.type)} -> {format_value(new, args.type)}")
    print(f"{changes} différence(s).")


def cmd_findptr(args):
    """Cherche les u32 alignés dont la valeur tombe dans [cible - max_offset, cible]."""
    memory = open_memory(args)
    low = max(args.target - args.max_offset, 0)
    high = args.target
    # On repère d'abord les 16 bits de poids fort (recherche rapide en C), puis on filtre.
    prefixes = range(low >> 16, (high >> 16) + 1)
    patterns = [re.compile(b"(?=" + re.escape(struct.pack(">H", prefix)) + b"..)", re.DOTALL) for prefix in prefixes]
    results = []
    for chunk_address, data in memory.iter_chunks(args.start, args.end, 3):
        for pattern in patterns:
            for match in pattern.finditer(data):
                position = match.start()
                if position >= CHUNK_SIZE or (chunk_address + position) % 4:
                    continue
                value = struct.unpack_from(">I", data, position)[0]
                if low <= value <= high:
                    results.append((chunk_address + position, value))
    results.sort()
    for address, value in results[:args.limit]:
        print(f"  0x{address:08X} -> 0x{value:08X}  (cible - 0x{high - value:X})")
    print(f"{len(results)} pointeur(s) candidat(s).")


# ---------------------------------------------------------------------------
# Ligne de commande
# ---------------------------------------------------------------------------

def auto_int(text):
    return int(text, 0)


def build_parser():
    parser = argparse.ArgumentParser(description="Sonde mémoire Cemu / Pikmin 3 (Phase 0).")
    parser.add_argument("--pid", type=int, help="PID de Cemu (si plusieurs instances)")
    parser.add_argument("--base", type=auto_int, help="Force la base mémoire hôte (ex. 0x23FEE060000)")
    parser.add_argument("--session", default="default", help="Nom de la recherche (find/refine), pour en mener plusieurs")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("info", help="Trouve Cemu et la base mémoire Wii U").set_defaults(func=cmd_info)
    sub.add_parser("ranges", help="Liste les plages Wii U engagées").set_defaults(func=cmd_ranges)

    p = sub.add_parser("read", help="Lit une ou plusieurs valeurs")
    p.add_argument("address", type=auto_int)
    p.add_argument("--type", choices=VALUE_TYPES, default="u32")
    p.add_argument("--count", type=int, default=1)
    p.set_defaults(func=cmd_read)

    p = sub.add_parser("hexdump", help="Affiche une zone en hexadécimal")
    p.add_argument("address", type=auto_int)
    p.add_argument("length", type=auto_int)
    p.set_defaults(func=cmd_hexdump)

    p = sub.add_parser("write", help="Écrit une valeur (demande confirmation)")
    p.add_argument("address", type=auto_int)
    p.add_argument("type", choices=VALUE_TYPES)
    p.add_argument("value")
    p.add_argument("--yes", action="store_true", help="Pas de confirmation")
    p.set_defaults(func=cmd_write)

    p = sub.add_parser("watch", help="Affiche chaque changement d'une valeur")
    p.add_argument("address", type=auto_int)
    p.add_argument("--type", choices=VALUE_TYPES, default="u32")
    p.add_argument("--interval", type=float, default=0.25)
    p.set_defaults(func=cmd_watch)

    p = sub.add_parser("find", help="Recherche une valeur exacte (nouvelle recherche)")
    p.add_argument("value")
    p.add_argument("--type", choices=VALUE_TYPES, default="u32")
    p.add_argument("--start", type=auto_int, default=DEFAULT_SCAN_START)
    p.add_argument("--end", type=auto_int, default=DEFAULT_SCAN_END)
    p.add_argument("--unaligned", action="store_true", help="Accepte les adresses non alignées")
    p.set_defaults(func=cmd_find)

    p = sub.add_parser("refine", help="Filtre la recherche : valeur, changed, unchanged, increased, decreased")
    p.add_argument("condition")
    p.set_defaults(func=cmd_refine)

    p = sub.add_parser("snapshot", help="Sauvegarde une zone mémoire")
    p.add_argument("name")
    p.add_argument("address", type=auto_int)
    p.add_argument("length", type=auto_int)
    p.set_defaults(func=cmd_snapshot)

    p = sub.add_parser("diff", help="Compare deux snapshots")
    p.add_argument("before")
    p.add_argument("after")
    p.add_argument("--type", choices=VALUE_TYPES, default="u8")
    p.add_argument("--noise", help="Snapshot pris sans rien faire : ses changements sont ignorés")
    p.add_argument("--limit", type=int, default=200)
    p.set_defaults(func=cmd_diff)

    p = sub.add_parser("findptr", help="Cherche des pointeurs vers une adresse (ou juste avant)")
    p.add_argument("target", type=auto_int)
    p.add_argument("--max-offset", type=auto_int, default=0x400)
    p.add_argument("--start", type=auto_int, default=DEFAULT_SCAN_START)
    p.add_argument("--end", type=auto_int, default=DEFAULT_SCAN_END)
    p.add_argument("--limit", type=int, default=100)
    p.set_defaults(func=cmd_findptr)
    return parser


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
