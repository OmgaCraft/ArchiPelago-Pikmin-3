"""
Tests en solo de la V1, sans serveur Archipelago : utilise directement le code du client
(worlds/pikmin3/client/game_interface.py), donc teste exactement ce que fera le client.

Le pack « Pikmin 3 > Mods > Archipelago » doit être actif. Ne pas lancer le Pikmin 3 Client en même temps.
Sauvegarder la partie avant d'écrire (tools/… ou copie du dossier de sauvegarde).

Usage :
    py -3.13 tools/solo_test.py status               (lecture comme le client + checks qui seraient envoyés)
    py -3.13 tools/solo_test.py watch                (signale chaque changement : Oignons, objets, fruits, jus…)
    py -3.13 tools/solo_test.py pikmin 5 [--slot 3]  (item Extra Red Pikmin : +5 feuilles dans l'Oignon rouge)
    py -3.13 tools/solo_test.py set 7 100            (total de l'Oignon roc (type 7) fixé à 100, via les feuilles)
    Types : 2 bleu, 3 rouge, 5 jaune, 6 ailé, 7 roc (jamais les blancs, type 4 : plantage).
    N'ajouter des Pikmin qu'à un Oignon déjà découvert dans la partie.
    py -3.13 tools/solo_test.py juice 1.5            (item fruit / Juice Drop ; négatif = piège, jamais sous 1)
    py -3.13 tools/solo_test.py spray 1              (item Ultra-Spicy Spray)
    py -3.13 tools/solo_test.py nojuice on|off       (fruits pressés sans jus, comme quand le client est connecté)
    py -3.13 tools/solo_test.py limit 30             (limite de Pikmin sur le terrain)
"""

import argparse
import importlib
import os
import sys
import time
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORLD_DIR = os.path.join(ROOT, "worlds", "pikmin3")

# Paquet synthétique : charge client/ et data/ sans exécuter worlds/pikmin3/__init__.py (qui demande Archipelago).
_package = types.ModuleType("p3ap")
_package.__path__ = [WORLD_DIR]
sys.modules["p3ap"] = _package
mm = importlib.import_module("p3ap.data.memory_map")
gi = importlib.import_module("p3ap.client.game_interface")
cemu = importlib.import_module("p3ap.client.cemu_memory")


def connect():
    pid = cemu.find_cemu_pid()
    if pid is None:
        sys.exit("Cemu n'est pas lancé.")
    return cemu.CemuMemory(pid)


def snapshot_or_exit(mem):
    snap = gi.read_snapshot(mem)
    if snap is None:
        sys.exit("Pas de partie Histoire lisible (menu, chargement, Mission/Bingo ?).")
    return snap


def mailbox_or_exit(mem):
    address = gi.find_mailbox(mem)
    if address is None:
        sys.exit("Boîte aux lettres introuvable : le pack Archipelago est-il actif ?")
    return address


def describe(snap):
    """Résumé lisible + checks que le client enverrait (options par défaut, notes comprises)."""
    onions = [name for slot, (name, bit) in mm.ONION_SLOTS.items() if snap.onion_bits & bit]
    unknown_onion_bits = snap.onion_bits & ~sum(bit for _, bit in mm.ONION_SLOTS.values())
    items = [name for bit, name in mm.KEY_ITEM_BITS.items() if snap.key_item_bits & bit]
    unknown_items = snap.key_item_bits & ~sum(mm.KEY_ITEM_BITS)
    counts = snap.onion_counts
    per_onion = {mm.ONION_SLOTS[s][0]: counts[s * 3:s * 3 + 3] for s in mm.ONION_SLOTS if any(counts[s * 3:s * 3 + 3])}
    return [
        f"jour {snap.day} | jus {snap.juice:g} | fruits pressés {snap.fruits_juiced} (types {snap.fruit_type_count})",
        f"population {snap.population} (terrain {snap.field}) | Oignons [feuille, bouton, fleur] {per_onion}",
        f"Oignons découverts (0x{snap.onion_bits:02X}) : {onions}"
        + (f" | bits inconnus 0x{unknown_onion_bits:02X}" if unknown_onion_bits else ""),
        f"objets importants (0x{snap.key_item_bits:08X}) : {items}"
        + (f" | bits inconnus 0x{unknown_items:X}" if unknown_items else ""),
        f"notes : tuto {snap.tutorial_notes} (A+B+C), Olimar {snap.olimar_notes} (D+F), Secret Memos {snap.secret_memos} (G)",
    ]


def cmd_status(mem, args):
    snap = snapshot_or_exit(mem)
    print("\n".join(describe(snap)))
    address = gi.find_mailbox(mem)
    if address is None:
        print("boîte aux lettres : absente (pack inactif)")
    else:
        flags = mem.read_u32(address + mm.MAILBOX_FLAGS_OFFSET)
        limit = mem.read_u32(address + mm.MAILBOX_PIKMIN_LIMIT_OFFSET)
        print(f"boîte aux lettres 0x{address:08X} : jus des fruits "
              f"{'supprimé' if flags & mm.MAILBOX_FLAG_NO_FRUIT_JUICE else 'normal'}, limite {limit}")
    sprays = mem.read_u32(snap.state_address + mm.STATE_SPRAY_COUNT)
    berries = mem.read_u32(snap.state_address + mm.STATE_BERRY_COUNT)
    print(f"sprays {sprays}, baies {berries}")


def cmd_watch(mem, args):
    print("Surveillance (Ctrl+C pour arrêter)…")
    last = None
    while True:
        try:
            snap = gi.read_snapshot(mem)
        except cemu.MemoryError_:
            print(f"{time.strftime('%H:%M:%S')} Cemu fermé : surveillance arrêtée.", flush=True)
            return
        lines = describe(snap) if snap else ["(pas de partie lisible)"]
        if lines != last:
            stamp = time.strftime("%H:%M:%S")
            for index, line in enumerate(lines):
                if last is None or index >= len(last) or line != last[index]:
                    print(f"{stamp} {line}", flush=True)
            last = lines
        time.sleep(0.5)


def cmd_pikmin(mem, args):
    snap = snapshot_or_exit(mem)
    gi.add_onion_pikmin(mem, snap, slot=args.slot, amount=args.amount)
    after = snapshot_or_exit(mem)
    print(f"Oignon {mm.ONION_SLOTS[args.slot][0]} : {snap.onion_counts[args.slot * 3]} -> "
          f"{after.onion_counts[args.slot * 3]} feuilles (population {snap.population} -> {after.population})")


def cmd_set(mem, args):
    snap = snapshot_or_exit(mem)
    counts = snap.onion_counts[args.slot * 3:args.slot * 3 + 3]
    delta = args.total - sum(counts)
    if counts[0] + delta < 0:
        sys.exit(f"Impossible : il faudrait retirer plus de feuilles qu'il n'y en a ({counts}).")
    gi.add_onion_pikmin(mem, snap, slot=args.slot, amount=delta)
    after = snapshot_or_exit(mem).onion_counts[args.slot * 3:args.slot * 3 + 3]
    print(f"Oignon {mm.ONION_SLOTS[args.slot][0]} : {counts} (total {sum(counts)}) -> {after} (total {sum(after)})")


def cmd_juice(mem, args):
    snap = snapshot_or_exit(mem)
    value = gi.add_juice(mem, snap, args.amount, minimum=1.0 if args.amount < 0 else 0.0)
    print(f"jus {snap.juice:g} -> {value:g}")


def cmd_spray(mem, args):
    snap = snapshot_or_exit(mem)
    before = mem.read_u32(snap.state_address + mm.STATE_SPRAY_COUNT)
    gi.add_sprays(mem, snap, args.amount)
    print(f"sprays {before} -> {mem.read_u32(snap.state_address + mm.STATE_SPRAY_COUNT)}")


def _write_mailbox(mem, no_fruit_juice=None, limit=None):
    address = mailbox_or_exit(mem)
    flags = mem.read_u32(address + mm.MAILBOX_FLAGS_OFFSET)
    if no_fruit_juice is not None:
        no_juice = no_fruit_juice
    else:
        no_juice = bool(flags & mm.MAILBOX_FLAG_NO_FRUIT_JUICE)
    if limit is None:
        limit = mem.read_u32(address + mm.MAILBOX_PIKMIN_LIMIT_OFFSET)
    gi.write_mailbox(mem, address, no_fruit_juice=no_juice, pikmin_limit=limit)
    print(f"boîte aux lettres 0x{address:08X} : jus des fruits {'supprimé' if no_juice else 'normal'}, limite {limit}")


def cmd_nojuice(mem, args):
    _write_mailbox(mem, no_fruit_juice=args.state == "on")


def cmd_limit(mem, args):
    _write_mailbox(mem, limit=args.value)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status").set_defaults(func=cmd_status)
    sub.add_parser("watch").set_defaults(func=cmd_watch)
    p = sub.add_parser("pikmin")
    p.add_argument("amount", type=int)
    p.add_argument("--slot", type=int, default=mm.RED_SLOT, choices=sorted(mm.ONION_SLOTS))
    p.set_defaults(func=cmd_pikmin)
    p = sub.add_parser("set")
    p.add_argument("slot", type=int, choices=sorted(mm.ONION_SLOTS))
    p.add_argument("total", type=int)
    p.set_defaults(func=cmd_set)
    p = sub.add_parser("juice")
    p.add_argument("amount", type=float)
    p.set_defaults(func=cmd_juice)
    p = sub.add_parser("spray")
    p.add_argument("amount", type=int)
    p.set_defaults(func=cmd_spray)
    p = sub.add_parser("nojuice")
    p.add_argument("state", choices=("on", "off"))
    p.set_defaults(func=cmd_nojuice)
    p = sub.add_parser("limit")
    p.add_argument("value", type=int)
    p.set_defaults(func=cmd_limit)
    args = parser.parse_args()

    mem = connect()
    try:
        args.func(mem, args)
    except KeyboardInterrupt:
        pass
    finally:
        mem.close()


if __name__ == "__main__":
    main()
