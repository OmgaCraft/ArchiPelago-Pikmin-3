"""
Outil de Phase 0 : journal des changements d'une zone mémoire (par défaut l'objet
d'état de Pikmin 3 et ses alentours).

Relit la zone à intervalle régulier et journalise chaque octet qui change, avec
l'heure, pour relier les événements du jeu (objet important, Oignon, fruit…) aux
données modifiées. Les adresses qui changent trop souvent (compteurs, minuteurs)
sont automatiquement déclarées « bruyantes » et ignorées.

Usage :
    py -3.13 tools/state_journal.py --log docs/phase0/logs/state_journal.log
    py -3.13 tools/state_journal.py --start 0x34A4C000 --length 0x4000 --interval 1
Arrêt : Ctrl+C, ou créer tools/.probe_state/journal_stop
"""

import argparse
import collections
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memory_probe as mp  # noqa: E402

# Objet d'état (voir docs/phase0/findings.md) : les décalages sont affichés par rapport à lui.
STATE_OBJECT = 0x34A4D75C
DEFAULT_START = 0x34A4C000
DEFAULT_LENGTH = 0x4000

# Une adresse qui change plus de NOISE_CHANGES fois en NOISE_WINDOW secondes est ignorée.
NOISE_CHANGES = 4
NOISE_WINDOW = 60.0

STOP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".probe_state", "journal_stop")


def main():
    parser = argparse.ArgumentParser(description="Journal des changements d'une zone mémoire Wii U.")
    parser.add_argument("--start", type=mp.auto_int, default=DEFAULT_START)
    parser.add_argument("--length", type=mp.auto_int, default=DEFAULT_LENGTH)
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--log", help="Fichier journal")
    args = parser.parse_args()

    class ProbeArgs:
        pid = None
        base = None

    memory = mp.open_memory(ProbeArgs())
    log_file = open(args.log, "a", encoding="utf-8") if args.log else None

    def log(line):
        stamped = f"[{time.strftime('%H:%M:%S')}] {line}"
        print(stamped, flush=True)
        if log_file:
            log_file.write(stamped + "\n")
            log_file.flush()

    if os.path.exists(STOP_FILE):
        os.remove(STOP_FILE)
    previous = memory.read(args.start, args.length)
    history = collections.defaultdict(collections.deque)   # adresse -> instants des changements
    noisy = set()
    log(f"Journal démarré : 0x{args.start:08X} + 0x{args.length:X}, toutes les {args.interval} s")

    try:
        while not os.path.exists(STOP_FILE):
            time.sleep(args.interval)
            try:
                current = memory.read(args.start, args.length)
            except OSError as error:
                log(f"Lecture impossible ({error}) : jeu fermé ?")
                break
            if current == previous:
                continue
            now = time.time()
            changes = []
            for offset in range(len(current)):
                if current[offset] == previous[offset]:
                    continue
                address = args.start + offset
                if address in noisy:
                    continue
                times = history[address]
                times.append(now)
                while times and now - times[0] > NOISE_WINDOW:
                    times.popleft()
                if len(times) > NOISE_CHANGES:
                    noisy.add(address)
                    log(f"(adresse bruyante ignorée désormais : 0x{address:08X})")
                    continue
                relative = address - STATE_OBJECT
                where = f"état{relative:+#06x}" if -0x1000 <= relative < 0x2000 else f"0x{address:08X}"
                changes.append(f"{where} (0x{address:08X}) : 0x{previous[offset]:02X} -> 0x{current[offset]:02X}")
            if changes:
                for change in changes[:40]:
                    log(change)
                if len(changes) > 40:
                    log(f"... et {len(changes) - 40} autre(s) octet(s)")
            previous = current
    except KeyboardInterrupt:
        pass
    finally:
        if os.path.exists(STOP_FILE):
            os.remove(STOP_FILE)
        log("Journal arrêté.")
        if log_file:
            log_file.close()


if __name__ == "__main__":
    main()
