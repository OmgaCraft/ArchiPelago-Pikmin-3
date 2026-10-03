"""
Tests manuels de la bêta, sans serveur : lit et écrit la partie avec le code du client bêta.

Sauvegarder la partie avant toute écriture. Ne pas lancer le Pikmin 3 Beta Client en même temps.

Usage :
    py -3.13 beta/tools/beta_test.py status                 (jour, Oignons découverts, Pikmin par type…)
    py -3.13 beta/tools/beta_test.py pikmin 2 10            (+10 feuilles dans l'Oignon du type 2 = bleu, sans repli)
    py -3.13 beta/tools/beta_test.py onion 2 on|off         (allume / éteint le bit « Oignon découvert » du type)
    Types : 2 bleu, 3 rouge, 5 jaune, 6 ailé, 7 roc (jamais 4 = blancs : plantage). Pour débloquer un type, allumer
    aussi son bit dans « fusionnés » (état+0x908), sinon scène de fusion puis plantage.
    py -3.13 beta/tools/beta_test.py zones                  (zones ouvertes / vues, bit par bit)
    py -3.13 beta/tools/beta_test.py zone 3 on|off [--seen on|off]
                                                            (ouvre / ferme la zone n° 3 = bit 0x08 de OpenAreaFlag ;
                                                             sauvegarde la partie dans backups/ avant d'écrire)
    py -3.13 beta/tools/beta_test.py backup etiquette       (copie la sauvegarde du jeu dans backups/)
"""

import argparse
import importlib
import os
import shutil
import sys
import time
import types

BETA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BETA_DIR)
SAVE_DIR = os.path.join(os.environ.get("APPDATA", ""), "Cemu", "mlc01", "usr", "save", "00050000", "1012be00")
_package = types.ModuleType("p3beta")
_package.__path__ = [os.path.join(BETA_DIR, "worlds", "pikmin3_beta")]
sys.modules["p3beta"] = _package
mm = importlib.import_module("p3beta.data.memory_map")
gi = importlib.import_module("p3beta.client.game_interface")
cemu = importlib.import_module("p3beta.client.cemu_memory")


def connect():
    pid = cemu.find_cemu_pid()
    if pid is None:
        sys.exit("Cemu n'est pas lancé.")
    return cemu.CemuMemory(pid)


def snapshot_or_exit(mem):
    snap = gi.read_snapshot(mem)
    if snap is None:
        sys.exit("Pas de partie Histoire lisible (menu, chargement ?).")
    return snap


def describe_slots(snap) -> str:
    lines = []
    for slot, (name, mask) in mm.ONION_SLOTS.items():
        counts = snap.onion_counts[slot * 3:slot * 3 + 3]
        found = "découvert" if snap.onion_bits & mask else "non découvert"
        doubt = " (vu seulement en le forçant)" if slot in mm.ONION_SLOTS_UNVERIFIED else ""
        lines.append(f"  type {slot} {name}{doubt} : bit 0x{mask:02X} {found}, "
                     f"[feuille, bouton, fleur] = {counts}")
    return "\n".join(lines)


def backup_save(label: str) -> str:
    """Copie le dossier de sauvegarde du jeu dans backups/ (même format que les sauvegardes précédentes)."""
    target = os.path.join(ROOT_DIR, "backups", f"save_1012be00_{time.strftime('%Y-%m-%d_%H%M')}_{label}")
    if os.path.exists(target):
        target += time.strftime("%S")
    shutil.copytree(SAVE_DIR, target)
    return target


def describe_zones(mem, state: int) -> str:
    """Les trois octets de zones, bit par bit (nom de la zone quand il est connu)."""
    opened = mem.read_u8(state + mm.STATE_OPEN_AREA_FLAG)
    seen = mem.read_u8(state + mm.STATE_SEEN_AREA_FLAG)
    other = mem.read_u8(state + mm.STATE_AREA_FLAG_90B)
    last_days = [mem.read_u32(state + mm.STATE_AREA_LAST_DAY + 4 * n) for n in range(mm.AREA_COUNT)]
    last_days = [day if day != 0xFFFFFFFF else -1 for day in last_days]
    lines = [f"  OpenAreaFlag 0x{opened:02X} | SeenAreaFlag 0x{seen:02X} | état+0x90B 0x{other:02X} | "
             f"curseur de la carte {mem.read_u32(state + mm.STATE_CURRENT_AREA)} | dernier jour par zone {last_days}"]
    for bit in range(8):
        mask = 1 << bit
        if (opened | seen | other) & mask or bit in mm.AREA_BITS:
            name = mm.AREA_BITS.get(bit, "?")
            lines.append(f"  zone {bit} (bit 0x{mask:02X}) {name} : "
                         f"{'ouverte' if opened & mask else 'fermée'}, {'vue' if seen & mask else 'pas vue'}, "
                         f"0x90B {'1' if other & mask else '0'}")
    return "\n".join(lines)


def set_bit(mem, address: int, mask: int, on: bool) -> tuple:
    before = mem.read_u8(address)
    after = before | mask if on else before & ~mask
    mem.write(address, bytes([after]))
    return before, mem.read_u8(address)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    p = sub.add_parser("pikmin")
    p.add_argument("slot", type=int, choices=sorted(mm.ONION_SLOTS))
    p.add_argument("amount", type=int)
    p = sub.add_parser("onion")
    p.add_argument("slot", type=int, choices=sorted(mm.ONION_SLOTS))
    p.add_argument("state", choices=("on", "off"))
    sub.add_parser("zones")
    p = sub.add_parser("zone")
    p.add_argument("area", type=int, choices=range(8))
    p.add_argument("state", choices=("on", "off"))
    p.add_argument("--seen", choices=("on", "off"), help="change aussi SeenAreaFlag")
    p.add_argument("--no-backup", action="store_true")
    p = sub.add_parser("backup")
    p.add_argument("label")
    args = parser.parse_args()

    if args.command == "backup":
        print(f"Sauvegarde copiée : {backup_save(args.label)}")
        return

    mem = connect()
    try:
        snap = snapshot_or_exit(mem)
        stamp = time.strftime("%H:%M:%S")
        if args.command in ("zones", "zone"):
            if args.command == "zone":
                if not args.no_backup:
                    print(f"Sauvegarde copiée : {backup_save(f'avant_zone{args.area}_{args.state}')}")
                mask = 1 << args.area
                before, after = set_bit(mem, snap.state_address + mm.STATE_OPEN_AREA_FLAG, mask, args.state == "on")
                print(f"{stamp} OpenAreaFlag 0x{before:02X} -> 0x{after:02X} (jour {snap.day})")
                if args.seen:
                    before, after = set_bit(mem, snap.state_address + mm.STATE_SEEN_AREA_FLAG, mask, args.seen == "on")
                    print(f"{stamp} SeenAreaFlag 0x{before:02X} -> 0x{after:02X}")
            print(f"Jour {snap.day} | terrain {snap.field}")
            print(describe_zones(mem, snap.state_address))
            return
        if args.command == "pikmin":
            gi.add_onion_pikmin(mem, snap, slot=args.slot, amount=args.amount)
            print(f"+{args.amount} feuilles dans l'Oignon du type {args.slot}.")
        elif args.command == "onion":
            mask = mm.ONION_SLOTS[args.slot][1]
            address = snap.state_address + mm.STATE_ONION_BITS
            value = mem.read_u8(address)
            value = value | mask if args.state == "on" else value & ~mask
            mem.write(address, bytes([value]))
            print(f"Bits des Oignons : 0x{snap.onion_bits:02X} -> 0x{value:02X}")
        snap = snapshot_or_exit(mem)
        print(f"Jour {snap.day} | jus {snap.juice:g} | population {snap.population} (terrain {snap.field}) | "
              f"Oignons découverts 0x{snap.onion_bits:02X}")
        print(describe_slots(snap))
    finally:
        mem.close()


if __name__ == "__main__":
    main()
