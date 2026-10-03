"""
Outil de Phase 0 : affiche toutes les valeurs de Pikmin 3 trouvées jusqu'ici.

Version ciblée : Pikmin 3 EUR (000500001012BE00) v1, module `carrot` 0x838be11a.
Chaque valeur est lue via une chaîne de pointeurs partant d'une adresse fixe
du RPX, donc sans dépendre de la base mémoire de Cemu ni des réallocations.

Ces constantes sont provisoires (Phase 0) : elles migreront dans
worlds/pikmin3/data/memory_map.py une fois validées.

Usage :
    py -3.13 tools/p3_status.py
    py -3.13 tools/p3_status.py --watch      (rafraîchit et signale les changements)
"""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memory_probe as mp  # noqa: E402

# --- Objet d'état de la partie (sauvegarde en cours) ------------------------
STATE_OBJECT_PTR = 0x103E448C          # pointeur fixe vers l'objet d'état
STATE_DAY = 0x48                       # u32, jour courant (✅)
STATE_UNKNOWN_4C = 0x4C                # u32, augmente dans la journée (❓)
STATE_JUICE = 0x50                     # f32, bouteilles de jus (✅)
STATE_FRUIT_COUNT = 0x54               # u32, SORTES de fruits enregistrées (✅ ; fruits pressés = bits de +0x70)
STATE_FRUIT_BITS = 0x5C                # champ de bits des fruits pressés (✅) : +0x5C à +0x83 (Pocked Airhead en +0x66)
STATE_FRUIT_BITS_SIZE = 40             # 320 bits ; nombre de bits = « ×N » fruits du bilan
STATE_TYPE_BITS = 0xA4                 # u8, bits des types/Oignons : 0x08 -> 0x88 avec les Rocs (🔶)
STATE_UNKNOWN_C0 = 0xC0                # u32, 0 -> 2 avec les Rocs (❓)
STATE_UNKNOWN_C4 = 0xC4                # u32 (❓)
STATE_UNKNOWN_C8 = 0xC8                # u32 (❓)
STATE_FRUIT_PENDING = 0x19C            # u8, rôle inconnu (❓, pas « fruit en attente »)
STATE_SPRAY_COUNT = 0x598              # u32, Ultra-Spicy Nectar (sprays) (✅ jour 10)
STATE_BERRY_COUNT = 0x59C              # u32, baies ultra-épicées ramassées, remises à 0 à la fabrication (✅)
STATE_KEY_ITEM_BITS = 0x58             # u32, objets importants : 0x01 Louie, 0x10 Anti-Electrifier, 0x40 Metal Suit Z, 0x80 Dodge Whistle (✅)

# Oignons : tableau [type][maturité] de u32, disposition à confirmer.
ONION_RED_SLOTS = (0xF0, 0xF4, 0xF8)       # ✅ emplacement 0 [feuille, bouton, fleur]
ONION_YELLOW_SLOTS = (0x108, 0x10C, 0x110) # ✅ emplacement 2 (jour 8)
ONION_ROCK_SLOTS = (0x120, 0x124, 0x128)   # ✅ emplacement 4

# --- Gestionnaire des Pikmin sur le terrain ---------------------------------
PIKMIN_MANAGER_PTR = 0x103E288C        # pointeur fixe (✅ valable après changement de jour)
PIKMIN_SQUADS = 0xED8                  # u32, Pikmin dans les équipes (🔶)
PIKMIN_FIELD = 0xEE8                   # u32, Pikmin sur le terrain (✅)


def read_status(memory):
    state = memory.read_value(STATE_OBJECT_PTR, "u32")
    manager = memory.read_value(PIKMIN_MANAGER_PTR, "u32")
    onion_red = [memory.read_value(state + off, "u32") for off in ONION_RED_SLOTS]
    onion_rock = [memory.read_value(state + off, "u32") for off in ONION_ROCK_SLOTS]
    onion_yellow = [memory.read_value(state + off, "u32") for off in ONION_YELLOW_SLOTS]
    field = memory.read_value(manager + PIKMIN_FIELD, "u32")
    return {
        "objet d'état": f"0x{state:08X}",
        "gestionnaire Pikmin": f"0x{manager:08X}",
        "jour": memory.read_value(state + STATE_DAY, "u32"),
        "jus": memory.read_value(state + STATE_JUICE, "f32"),
        "sortes de fruits": memory.read_value(state + STATE_FRUIT_COUNT, "u32"),
        "bits fruits (+0x5C..)": memory.read(state + STATE_FRUIT_BITS, STATE_FRUIT_BITS_SIZE).hex(" ").upper(),
        "fruit en attente (+0x19C)": memory.read_value(state + STATE_FRUIT_PENDING, "u8"),
        "bits types (+0xA4)": f"0x{memory.read_value(state + STATE_TYPE_BITS, 'u8'):02X}",
        "objets importants (+0x58)": f"0x{memory.read_value(state + STATE_KEY_ITEM_BITS, 'u32'):08X}",
        "sprays / baies": [memory.read_value(state + STATE_SPRAY_COUNT, "u32"),
                           memory.read_value(state + STATE_BERRY_COUNT, "u32")],
        "Oignon Rouge [maturités]": onion_red,
        "Oignon Jaune [maturités]": onion_yellow,
        "Oignon Roc [maturités]": onion_rock,
        "équipes": memory.read_value(manager + PIKMIN_SQUADS, "u32"),
        "terrain": field,
        "population (Oignons + terrain)": sum(onion_red) + sum(onion_yellow) + sum(onion_rock) + field,
        "inconnu +0x4C": memory.read_value(state + STATE_UNKNOWN_4C, "u32"),
        "inconnu +0xC0/+0xC4/+0xC8": [memory.read_value(state + off, "u32")
                                      for off in (STATE_UNKNOWN_C0, STATE_UNKNOWN_C4, STATE_UNKNOWN_C8)],
    }


def main():
    parser = argparse.ArgumentParser(description="État de Pikmin 3 (valeurs connues en Phase 0).")
    parser.add_argument("--watch", action="store_true", help="Rafraîchit chaque seconde")
    args = parser.parse_args()

    class ProbeArgs:
        pid = None
        base = None

    memory = mp.open_memory(ProbeArgs())
    previous = None
    while True:
        status = read_status(memory)
        if previous is None:
            for key, value in status.items():
                print(f"{key:>32} : {value}")
        else:
            for key, value in status.items():
                if value != previous[key]:
                    print(f"[{time.strftime('%H:%M:%S')}] {key} : {previous[key]} -> {value}")
        previous = status
        if not args.watch:
            break
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
