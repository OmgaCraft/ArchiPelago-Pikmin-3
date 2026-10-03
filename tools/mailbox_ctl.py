"""
Pilote la boîte aux lettres du graphic pack Archipelago sans serveur (tests en jeu).

Le pack « Pikmin 3 > Mods > Archipelago » doit être actif (et les packs P3AP_Phase0_* désactivés).
Le client Archipelago écrit les mêmes valeurs : ne pas lancer les deux en même temps.

Usage :
    py -3.13 tools/mailbox_ctl.py status          (adresse, drapeaux, limite, marqueur)
    py -3.13 tools/mailbox_ctl.py limit 30        (limite de Pikmin sur le terrain, 1–100)
    py -3.13 tools/mailbox_ctl.py juice off       (les fruits pressés ne donnent plus de jus)
    py -3.13 tools/mailbox_ctl.py juice on        (comportement normal)
"""

import argparse
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memory_probe as mp  # noqa: E402

# Mêmes valeurs que worlds/pikmin3/data/memory_map.py (boîte aux lettres v2).
MAILBOX_ADDRESS = 0x01800000
MAILBOX_SEARCH_SIZE = 0x10000
MAILBOX_SIGNATURE = b"P3APMBOX"
MAILBOX_VERSION = 2
VERSION_OFFSET = 0x08
FLAGS_OFFSET = 0x0C
FLAG_NO_FRUIT_JUICE = 0x1
PIKMIN_LIMIT_OFFSET = 0x10
CLIENT_MARKER_OFFSET = 0x14


def u32(memory, address):
    return struct.unpack(">I", memory.read(address, 4))[0]


def find_mailbox(memory):
    for chunk_address in range(MAILBOX_ADDRESS, MAILBOX_ADDRESS + MAILBOX_SEARCH_SIZE, 0x1000):
        try:
            chunk = memory.read(chunk_address, 0x1000)
        except OSError:
            return None
        offset = chunk.find(MAILBOX_SIGNATURE)
        while offset != -1:
            address = chunk_address + offset
            if offset % 4 == 0 and u32(memory, address + VERSION_OFFSET) == MAILBOX_VERSION:
                return address
            offset = chunk.find(MAILBOX_SIGNATURE, offset + 1)
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pid", type=int)
    parser.add_argument("--base", type=lambda text: int(text, 0))
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    limit = sub.add_parser("limit")
    limit.add_argument("value", type=int)
    juice = sub.add_parser("juice")
    juice.add_argument("state", choices=("on", "off"))
    args = parser.parse_args()

    memory = mp.open_memory(args, writable=args.command != "status")
    address = find_mailbox(memory)
    if address is None:
        sys.exit("Boîte aux lettres introuvable : le pack Archipelago est-il actif et le jeu lancé ?")

    if args.command == "limit":
        memory.write(address + PIKMIN_LIMIT_OFFSET, struct.pack(">I", max(1, min(100, args.value))))
    elif args.command == "juice":
        flags = u32(memory, address + FLAGS_OFFSET)
        flags = flags | FLAG_NO_FRUIT_JUICE if args.state == "off" else flags & ~FLAG_NO_FRUIT_JUICE
        memory.write(address + FLAGS_OFFSET, struct.pack(">I", flags))

    flags = u32(memory, address + FLAGS_OFFSET)
    print(f"Boîte aux lettres : 0x{address:08X}")
    print(f"  jus des fruits : {'supprimé' if flags & FLAG_NO_FRUIT_JUICE else 'normal'} (drapeaux 0x{flags:X})")
    print(f"  limite de Pikmin : {u32(memory, address + PIKMIN_LIMIT_OFFSET)}")
    print(f"  marqueur du client : 0x{u32(memory, address + CLIENT_MARKER_OFFSET):08X}")


if __name__ == "__main__":
    main()
