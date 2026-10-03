"""
Console des checks — Pikmin 3 (bêta).

Affiche en direct chaque check accompli dans ta partie (fruit pressé, Oignon découvert, objet obtenu, note,
nouveau jour…), sans Archipelago ni serveur : il suffit que Cemu et Pikmin 3 tournent.
Utilise le même code que le Pikmin 3 Beta Client (beta/worlds/pikmin3_beta/client/events.py).

Lancement : double-clic sur « Console des checks.bat », ou  py -3.13 beta/console_checks.py
Arrêt : Ctrl+C. Une copie de la console est écrite dans beta/logs/checks_AAAA-MM-JJ.txt.
"""

import importlib
import os
import sys
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(HERE, "logs")
SYNC_INTERVAL = 0.5
CEMU_RETRY_INTERVAL = 5.0


def find_world_dir() -> str:
    """Code du monde bêta : dossier source, sinon un pikmin3_beta.apworld (archive zip) à côté ou installé."""
    source = os.path.join(HERE, "worlds", "pikmin3_beta")
    if os.path.isdir(source):
        return source
    for apworld in (os.path.join(HERE, "pikmin3_beta.apworld"),
                    os.path.join(HERE, "dist", "pikmin3_beta.apworld"),
                    os.path.join(os.environ.get("PROGRAMDATA", r"C:\ProgramData"), "Archipelago", "custom_worlds",
                                 "pikmin3_beta.apworld")):
        if os.path.isfile(apworld):
            return os.path.join(apworld, "pikmin3_beta")  # chargé directement depuis l'archive
    sys.exit("pikmin3_beta.apworld introuvable : mets ce script à côté de l'apworld, ou installe l'apworld.")


# Paquet synthétique : charge data/ et client/ sans exécuter __init__.py du monde (qui demande Archipelago).
_package = types.ModuleType("p3beta")
_package.__path__ = [find_world_dir()]
sys.modules["p3beta"] = _package
gi = importlib.import_module("p3beta.client.game_interface")
cemu = importlib.import_module("p3beta.client.cemu_memory")
events = importlib.import_module("p3beta.client.events")

GREEN, CYAN, YELLOW, GREY, RESET = "\033[92m", "\033[96m", "\033[93m", "\033[90m", "\033[0m"


class Console:
    def __init__(self) -> None:
        os.makedirs(LOG_DIR, exist_ok=True)
        self.log_path = os.path.join(LOG_DIR, time.strftime("checks_%Y-%m-%d.txt"))

    def show(self, text: str, color: str = "") -> None:
        stamp = time.strftime("%H:%M:%S")
        print(f"{GREY}{stamp}{RESET} {color}{text}{RESET}", flush=True)
        with open(self.log_path, "a", encoding="utf-8") as handle:
            handle.write(f"{time.strftime('%Y-%m-%d')} {stamp} {text}\n")


def color_for(event) -> str:
    if event.location:
        return GREEN
    if "inconnu" in event.message:
        return YELLOW
    return CYAN


def run() -> None:
    os.system("")  # active les couleurs ANSI dans la console Windows
    console = Console()
    print(f"{CYAN}Console des checks — Pikmin 3 (bêta){RESET}  (Ctrl+C pour quitter)")
    print(f"{GREY}Copie de la console : {console.log_path}{RESET}")
    tracker = events.CheckEventTracker()
    memory = None
    waiting_message = ""
    while True:
        if memory is None:
            pid = cemu.find_cemu_pid()
            if pid is None:
                if waiting_message != "cemu":
                    console.show("En attente de Cemu…", GREY)
                    waiting_message = "cemu"
                time.sleep(CEMU_RETRY_INTERVAL)
                continue
            try:
                memory = cemu.CemuMemory(pid)
            except cemu.MemoryError_ as error:
                console.show(f"Cemu trouvé mais illisible : {error}", YELLOW)
                time.sleep(CEMU_RETRY_INTERVAL)
                continue
            console.show(f"Cemu connecté (pid {pid}).", GREY)
            tracker.reset()
        try:
            snap = gi.read_snapshot(memory)
        except cemu.MemoryError_:
            console.show("Cemu fermé.", GREY)
            memory.close()
            memory = None
            waiting_message = ""
            continue
        if snap is None:
            if waiting_message != "partie":
                console.show("En attente d'une partie en mode Histoire…", GREY)
                waiting_message = "partie"
        else:
            waiting_message = ""
            for event in tracker.update(snap):
                text = event.message + (f"  → check « {event.location} »" if event.location else "")
                console.show(("✔ " if event.location else "• ") + text, color_for(event))
        time.sleep(SYNC_INTERVAL)


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print(f"\n{GREY}Console fermée.{RESET}")
