"""
Accès à la mémoire Wii U émulée par Cemu (Windows uniquement), sans dépendance externe.

Cemu réserve exactement 4 Gio pour l'espace mémoire de la Wii U, à une base qui change à chaque
lancement. On la retrouve dans log.txt (« Init Wii U memory space (base: 0x…) ») ou, à défaut,
en cherchant la réservation de 4 Gio dans le processus. Adresse hôte = base + adresse Wii U.
La Wii U est big-endian.
"""

from __future__ import annotations

import ctypes
import os
import re
import struct
import sys
from ctypes import wintypes
from typing import Optional

CEMU_EXE_NAME = "cemu.exe"
GUEST_SPACE_SIZE = 0x1_0000_0000
USER_SPACE_END = 0x7FFF_FFFF_0000

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_VM_OPERATION = 0x0008
TH32CS_SNAPPROCESS = 0x0000_0002
MEM_COMMIT = 0x1000
MEM_FREE = 0x10000


class MemoryError_(Exception):
    """Lecture ou écriture impossible (Cemu fermé, adresse invalide…)."""


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


_kernel32 = None


def _k32():
    """Charge kernel32 à la demande (le module reste importable hors Windows, ex. pour les tests)."""
    global _kernel32
    if _kernel32 is None:
        if sys.platform != "win32":
            raise MemoryError_("Le client Pikmin 3 ne fonctionne que sous Windows.")
        k = ctypes.WinDLL("kernel32", use_last_error=True)
        k.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        k.OpenProcess.restype = wintypes.HANDLE
        k.CloseHandle.argtypes = (wintypes.HANDLE,)
        k.CloseHandle.restype = wintypes.BOOL
        k.VirtualQueryEx.argtypes = (wintypes.HANDLE, ctypes.c_void_p,
                                     ctypes.POINTER(MEMORY_BASIC_INFORMATION), ctypes.c_size_t)
        k.VirtualQueryEx.restype = ctypes.c_size_t
        k.ReadProcessMemory.argtypes = (wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p,
                                        ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t))
        k.ReadProcessMemory.restype = wintypes.BOOL
        k.WriteProcessMemory.argtypes = (wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p,
                                         ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t))
        k.WriteProcessMemory.restype = wintypes.BOOL
        k.CreateToolhelp32Snapshot.argtypes = (wintypes.DWORD, wintypes.DWORD)
        k.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
        k.Process32FirstW.argtypes = (wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W))
        k.Process32FirstW.restype = wintypes.BOOL
        k.Process32NextW.argtypes = (wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W))
        k.Process32NextW.restype = wintypes.BOOL
        _kernel32 = k
    return _kernel32


def find_cemu_pid() -> Optional[int]:
    """PID du premier processus Cemu.exe trouvé, ou None."""
    k = _k32()
    snapshot = k.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snapshot == wintypes.HANDLE(-1).value:
        return None
    try:
        entry = PROCESSENTRY32W()
        entry.dwSize = ctypes.sizeof(PROCESSENTRY32W)
        ok = k.Process32FirstW(snapshot, ctypes.byref(entry))
        while ok:
            if entry.szExeFile.lower() == CEMU_EXE_NAME:
                return int(entry.th32ProcessID)
            ok = k.Process32NextW(snapshot, ctypes.byref(entry))
    finally:
        k.CloseHandle(snapshot)
    return None


def cemu_log_path() -> str:
    return os.path.join(os.environ.get("APPDATA", ""), "Cemu", "log.txt")


def base_from_log() -> Optional[int]:
    """Base mémoire annoncée par log.txt de Cemu (réécrit à chaque démarrage de Cemu)."""
    try:
        with open(cemu_log_path(), "r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                match = re.search(r"Init Wii U memory space \(base:\s*0x([0-9A-Fa-f]+)\)", line)
                if match:
                    return int(match.group(1), 16)
    except OSError:
        return None
    return None


class CemuMemory:
    """Connexion à un processus Cemu : lecture/écriture big-endian aux adresses Wii U."""

    def __init__(self, pid: int) -> None:
        k = _k32()
        access = PROCESS_QUERY_INFORMATION | PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION
        self.pid = pid
        self.handle = k.OpenProcess(access, False, pid)
        if not self.handle:
            raise MemoryError_(f"Impossible d'ouvrir le processus Cemu (pid {pid}).")
        self.base = self._find_base()
        if self.base is None:
            self.close()
            raise MemoryError_("Espace mémoire Wii U introuvable dans Cemu.")

    # --- Base mémoire -------------------------------------------------------

    def _regions(self):
        k = _k32()
        address = 0
        while address < USER_SPACE_END:
            mbi = MEMORY_BASIC_INFORMATION()
            if not k.VirtualQueryEx(self.handle, ctypes.c_void_p(address), ctypes.byref(mbi), ctypes.sizeof(mbi)):
                break
            yield mbi
            next_address = (mbi.BaseAddress or 0) + mbi.RegionSize
            if next_address <= address:
                break
            address = next_address

    def _find_base(self) -> Optional[int]:
        spans: dict[int, int] = {}
        for mbi in self._regions():
            if mbi.State == MEM_FREE or not mbi.AllocationBase:
                continue
            end = (mbi.BaseAddress or 0) + mbi.RegionSize
            spans[mbi.AllocationBase] = max(spans.get(mbi.AllocationBase, 0), end)
        candidates = [base for base, end in spans.items() if end - base == GUEST_SPACE_SIZE]
        logged = base_from_log()
        if logged in candidates:
            return logged
        return candidates[0] if len(candidates) == 1 else None

    # --- Accès bruts ----------------------------------------------------------

    def close(self) -> None:
        if self.handle:
            _k32().CloseHandle(self.handle)
            self.handle = None

    def read(self, address: int, size: int) -> bytes:
        buffer = ctypes.create_string_buffer(size)
        done = ctypes.c_size_t(0)
        ok = _k32().ReadProcessMemory(self.handle, ctypes.c_void_p(self.base + address), buffer, size,
                                      ctypes.byref(done))
        if not ok or done.value != size:
            raise MemoryError_(f"Lecture impossible à 0x{address:08X}")
        return buffer.raw

    def write(self, address: int, data: bytes) -> None:
        done = ctypes.c_size_t(0)
        ok = _k32().WriteProcessMemory(self.handle, ctypes.c_void_p(self.base + address), data, len(data),
                                       ctypes.byref(done))
        if not ok or done.value != len(data):
            raise MemoryError_(f"Écriture impossible à 0x{address:08X}")

    # --- Types big-endian -------------------------------------------------------

    def read_u8(self, address: int) -> int:
        return self.read(address, 1)[0]

    def read_u32(self, address: int) -> int:
        return struct.unpack(">I", self.read(address, 4))[0]

    def read_f32(self, address: int) -> float:
        return struct.unpack(">f", self.read(address, 4))[0]

    def write_u32(self, address: int, value: int) -> None:
        self.write(address, struct.pack(">I", value & 0xFFFFFFFF))

    def write_f32(self, address: int, value: float) -> None:
        self.write(address, struct.pack(">f", value))
