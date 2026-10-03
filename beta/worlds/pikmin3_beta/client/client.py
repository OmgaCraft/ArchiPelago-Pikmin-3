"""
Client Archipelago de Pikmin 3 BÊTA (Wii U / Cemu) — jeu « Pikmin 3 Beta », séparé de la version finale.

En plus du client final : checks bêta (jours, sortes de fruits, ensembles de notes A–D, étapes d'histoire),
items bêta (Pikmin d'autres couleurs, baies) et journal des découvertes (actif même sans serveur) :
chaque octet qui change dans les zones surveillées est noté avec le jour et la dernière note du joueur (/note).

Boucle principale (toutes les 0,5 s) :
  1. se connecter à Cemu et vérifier le graphic pack (boîte aux lettres) ;
  2. lire un instantané de la partie (mode Histoire uniquement) ;
  3. gérer les changements de jour (index des items par jour, modes de jus) ;
  4. appliquer les items reçus pas encore donnés ;
  5. envoyer les checks et la victoire.

Suivi des items reçus : l'index « items déjà donnés » est rangé dans le stockage de données du
serveur, avec sa valeur au début de chaque jour. Si le joueur recharge un jour précédent, le
client reprend l'index de ce jour et redonne les items perdus. Commande /resync_day en secours.
"""

from __future__ import annotations

import asyncio
import logging
import traceback
from typing import Any, Optional

import Utils
from MultiServer import mark_raw
from CommonClient import ClientCommandProcessor, CommonContext, get_base_parser, gui_enabled, handle_url_arg, \
    logger, server_loop
from NetUtils import ClientStatus

from .. import items as p3_items
from .. import locations as p3_locations
from ..data import fruits
from ..data import memory_map as mm
from ..data.game_info import GAME_NAME
from . import game_interface as gi
from .cemu_memory import CemuMemory, MemoryError_, find_cemu_pid
from .discovery import DiscoveryTracker
from .events import CheckEventTracker
from .graphic_pack import final_pack_also_enabled, install_graphic_pack, installed_phase0_packs

SYNC_INTERVAL = 0.5
CEMU_RETRY_INTERVAL = 5.0
SAFE_JUICE_FLOOR = 2.0
DISCOVERY_LOG_NAME = "Pikmin3Beta_decouvertes.txt"
ITEM_ID_TO_NAME = {code: name for name, code in p3_items.ITEM_NAME_TO_ID.items()}
# Console des checks : onglet « Checks » de la fenêtre du client (et lignes « [Checks] » en mode console).
CHECKS_LOGGER_NAME = "Pikmin3Checks"
check_logger = logging.getLogger(CHECKS_LOGGER_NAME)


class Pikmin3CommandProcessor(ClientCommandProcessor):
    def _cmd_cemu(self) -> None:
        """Affiche l'état de la connexion à Cemu et au graphic pack."""
        if isinstance(self.ctx, Pikmin3Context):
            logger.info(f"Cemu : {self.ctx.cemu_status}")

    def _cmd_state(self) -> None:
        """Affiche l'état de la partie lu en mémoire (jour, jus, fruits, population…)."""
        if isinstance(self.ctx, Pikmin3Context):
            self.ctx.log_state()

    def _cmd_install_pack(self, cemu_data_dir: str = "") -> None:
        """Installe le graphic pack dans Cemu (dossier Cemu optionnel, défaut : %APPDATA%\\Cemu)."""
        try:
            target = install_graphic_pack(cemu_data_dir or None)
        except OSError as error:
            logger.error(f"Installation impossible : {error}")
            return
        logger.info(f"Graphic pack installé dans : {target}")
        logger.info("Dans Cemu : Graphic packs > Pikmin 3 > Mods > Archipelago Beta (cocher, et décocher "
                    "« Archipelago » s'il l'est), puis relancer le jeu.")
        leftovers = installed_phase0_packs(cemu_data_dir or None)
        if leftovers:
            logger.warning("Désactivez les anciens packs de test : " + ", ".join(leftovers))

    def _cmd_resync_day(self) -> None:
        """Redonne les items reçus depuis le début du jour en cours (après un rechargement non détecté)."""
        if isinstance(self.ctx, Pikmin3Context):
            self.ctx.request_day_resync = True
            logger.info("Resynchronisation demandée : prise en compte au prochain passage.")

    @mark_raw
    def _cmd_note(self, text: str = "") -> None:
        """Note ce que tu viens de faire (« Oignon bleu trouvé ») : elle accompagne les découvertes qui suivent."""
        if isinstance(self.ctx, Pikmin3Context):
            day = self.ctx.last_snapshot.day if self.ctx.last_snapshot else None
            self.ctx.discovery.add_note(text.strip(), day)
            logger.info(f"Note enregistrée : {text.strip() or '(vide : plus de note)'}")

    def _cmd_checks(self) -> None:
        """Résumé de ce qui est accompli dans la partie (fruits, Oignons, objets, notes…)."""
        if isinstance(self.ctx, Pikmin3Context):
            if self.ctx.last_snapshot is None:
                check_logger.info("Aucune partie lisible pour l'instant.")
            else:
                check_logger.info(self.ctx.check_events.summary(self.ctx.last_snapshot))

    def _cmd_decouvertes(self, count: str = "20") -> None:
        """Affiche les dernières découvertes (changements en mémoire) ; argument : nombre de lignes."""
        if isinstance(self.ctx, Pikmin3Context):
            recent = list(self.ctx.discovery.recent)[-max(1, int(count) if count.isdigit() else 20):]
            if not recent:
                logger.info("Aucune découverte pour l'instant.")
            for discovery in recent:
                logger.info(discovery.line())
            logger.info(f"Journal complet : {self.ctx.discovery.log_path}")


class Pikmin3Context(CommonContext):
    command_processor = Pikmin3CommandProcessor
    game = GAME_NAME
    items_handling = 0b111  # les checks ne donnent rien dans le jeu : tous les items viennent du serveur

    def __init__(self, server_address: Optional[str], password: Optional[str]) -> None:
        super().__init__(server_address, password)
        self.memory: Optional[CemuMemory] = None
        self.cemu_status = "non connecté"
        self.next_cemu_attempt = 0.0
        self.mailbox_address: Optional[int] = None
        self.warned_no_pack = False
        self.slot_data: dict[str, Any] = {}
        self.sync_task: Optional[asyncio.Task[None]] = None
        # Suivi des items donnés (persisté dans le stockage de données du serveur).
        self.storage_loaded = False
        self.applied_index = 0
        self.day_start_index: dict[str, int] = {}
        self.stored_last_day: Optional[int] = None
        self.session_day: Optional[int] = None
        self.request_day_resync = False
        self.game_restarted = False
        self.last_snapshot: Optional[gi.GameSnapshot] = None
        self.discovery = DiscoveryTracker(Utils.user_path("logs", DISCOVERY_LOG_NAME))
        self.check_events = CheckEventTracker()

    # --- Serveur -----------------------------------------------------------------

    @property
    def storage_key(self) -> str:
        return f"pikmin3beta_items_{self.team}_{self.slot}"

    async def server_auth(self, password_requested: bool = False) -> None:
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    async def disconnect(self, allow_autoreconnect: bool = False) -> None:
        self.storage_loaded = False
        self.session_day = None
        await super().disconnect(allow_autoreconnect)

    def on_package(self, cmd: str, args: dict[str, Any]) -> None:
        if cmd == "Connected":
            self.slot_data = args.get("slot_data", {}) or {}
            self.storage_loaded = False
            self.session_day = None
            Utils.async_start(self.send_msgs([{"cmd": "Get", "keys": [self.storage_key]}]))
        elif cmd == "Retrieved" and self.storage_key in args.get("keys", {}):
            stored = args["keys"][self.storage_key] or {}
            self.applied_index = int(stored.get("applied_index", 0))
            self.day_start_index = {str(k): int(v) for k, v in stored.get("day_start_index", {}).items()}
            last_day = stored.get("last_day")
            self.stored_last_day = int(last_day) if last_day is not None else None
            self.storage_loaded = True
            logger.info(f"Suivi des items chargé : {self.applied_index} item(s) déjà donné(s).")

    async def save_item_tracking(self) -> None:
        value = {
            "applied_index": self.applied_index,
            "day_start_index": self.day_start_index,
            "last_day": self.session_day,
        }
        await self.send_msgs([{
            "cmd": "Set", "key": self.storage_key, "default": {}, "want_reply": False,
            "operations": [{"operation": "replace", "value": value}],
        }])

    def make_gui(self):
        ui = super().make_gui()
        ui.base_title = "Archipelago Pikmin 3 Beta Client"
        # Onglet « Checks » : la console des checks accomplis (nouvelle liste, pour ne pas modifier celle d'origine).
        ui.logging_pairs = ui.logging_pairs + [(CHECKS_LOGGER_NAME, "Checks")]
        return ui

    # --- Options du slot ------------------------------------------------------------

    def option(self, name: str, default: Any = None) -> Any:
        return self.slot_data.get(name, default)

    def pikmin_limit(self) -> int:
        if not self.option("progressive_pikmin_limit", False):
            return mm.FIELD_LIMIT_VANILLA
        received = sum(1 for item in self.items_received
                       if ITEM_ID_TO_NAME.get(item.item) == p3_items.PROGRESSIVE_PIKMIN_LIMIT)
        start = int(self.option("pikmin_limit_start", 30))
        step = int(self.option("pikmin_limit_step", 10))
        return min(mm.FIELD_LIMIT_VANILLA, start + received * step)

    def log_state(self) -> None:
        snap = self.last_snapshot
        if snap is None:
            logger.info("Aucune partie lisible (Cemu fermé, menu, chargement ou mode Mission).")
            return
        notes = ", ".join(f"{key} {count}" for key, count in snap.note_counts.items())
        onions = [name for slot, (name, _) in mm.ONION_SLOTS.items() if snap.onion_discovered(slot)]
        logger.info(
            f"Jour {snap.day} | jus {snap.juice:.1f} | fruits pressés {snap.fruits_juiced} "
            f"({snap.fruit_type_count} sortes) | population {snap.population} (terrain {snap.field}) | "
            f"Oignons {onions} | objets 0x{snap.key_item_bits:X} | notes {notes} | "
            f"étapes d'histoire {snap.story_events} | sprays {snap.spray_count}, baies {snap.berry_count} | "
            f"limite de Pikmin {self.pikmin_limit()} | items donnés {self.applied_index}/{len(self.items_received)}"
        )


# --------------------------------------------------------------------------
# Connexion à Cemu
# --------------------------------------------------------------------------

def connect_cemu(ctx: Pikmin3Context) -> None:
    loop_time = asyncio.get_running_loop().time()
    if loop_time < ctx.next_cemu_attempt:
        return
    ctx.next_cemu_attempt = loop_time + CEMU_RETRY_INTERVAL
    pid = find_cemu_pid()
    if pid is None:
        ctx.cemu_status = "Cemu introuvable (lancez Cemu et Pikmin 3)"
        return
    try:
        ctx.memory = CemuMemory(pid)
    except MemoryError_ as error:
        ctx.cemu_status = str(error)
        return
    ctx.cemu_status = f"connecté (pid {pid}, base 0x{ctx.memory.base:X})"
    ctx.mailbox_address = None
    ctx.discovery.reset()
    ctx.check_events.reset()
    logger.info(f"Cemu : {ctx.cemu_status}")
    if final_pack_also_enabled():
        logger.warning("Les packs « Archipelago » (finale) et « Archipelago Beta » sont cochés ensemble dans Cemu : "
                       "décoche « Archipelago » et relance le jeu.")


def lose_cemu(ctx: Pikmin3Context, reason: str) -> None:
    if ctx.memory is not None:
        ctx.memory.close()
    ctx.memory = None
    ctx.mailbox_address = None
    ctx.session_day = None
    ctx.last_snapshot = None
    ctx.discovery.reset()
    ctx.check_events.reset()
    ctx.cemu_status = f"déconnecté ({reason})"
    logger.info(f"Cemu : {ctx.cemu_status}")


def update_mailbox(ctx: Pikmin3Context) -> None:
    assert ctx.memory is not None
    if ctx.mailbox_address is None or not gi.mailbox_valid(ctx.memory, ctx.mailbox_address):
        ctx.mailbox_address = gi.find_mailbox(ctx.memory)
        if ctx.mailbox_address is None:
            if not ctx.warned_no_pack:
                logger.warning(
                    "Graphic pack Archipelago Beta inactif : les fruits donneront leur jus en plus des items, "
                    "et la limite de Pikmin reste à 100. Utilisez /install_pack puis activez-le dans Cemu."
                )
                ctx.warned_no_pack = True
            return
        logger.info(f"Graphic pack Archipelago Beta détecté (boîte aux lettres 0x{ctx.mailbox_address:08X}).")
        ctx.warned_no_pack = False
    gi.write_mailbox(ctx.memory, ctx.mailbox_address, no_fruit_juice=True, pikmin_limit=ctx.pikmin_limit())
    if gi.consume_game_restart(ctx.memory, ctx.mailbox_address):
        # Jeu (re)lancé : la partie sera chargée depuis la sauvegarde du début du jour.
        ctx.game_restarted = True


# --------------------------------------------------------------------------
# Jours, items, checks
# --------------------------------------------------------------------------

async def handle_day(ctx: Pikmin3Context, snap: gi.GameSnapshot) -> None:
    """Détecte les changements de jour et les rechargements ; applique le mode de jus."""
    assert ctx.memory is not None
    changed = False
    day_key = str(snap.day)

    if ctx.session_day is None:
        # Premier instantané de la session : rechargement d'un jour antérieur ?
        if ctx.stored_last_day is not None and snap.day < ctx.stored_last_day and day_key in ctx.day_start_index:
            ctx.applied_index = ctx.day_start_index[day_key]
            logger.info(f"Jour {snap.day} rechargé : les items reçus depuis ce jour seront redonnés.")
        ctx.session_day = snap.day
        ctx.day_start_index.setdefault(day_key, ctx.applied_index)
        changed = True
    elif snap.day > ctx.session_day:
        nights = snap.day - ctx.session_day
        if ctx.option("juice_mode") == 2:  # no_consumption : on rend les bouteilles bues
            gi.add_juice(ctx.memory, snap, float(nights))
            logger.info(f"Mode « no_consumption » : {nights} bouteille(s) rendue(s).")
        ctx.session_day = snap.day
        ctx.day_start_index[day_key] = ctx.applied_index
        changed = True
    elif snap.day < ctx.session_day:
        ctx.applied_index = ctx.day_start_index.get(day_key, ctx.applied_index)
        ctx.session_day = snap.day
        logger.info(f"Retour au jour {snap.day} : resynchronisation des items.")
        changed = True

    if ctx.game_restarted:
        ctx.game_restarted = False
        if day_key in ctx.day_start_index and ctx.day_start_index[day_key] < ctx.applied_index:
            ctx.applied_index = ctx.day_start_index[day_key]
            logger.info(f"Jeu relancé au jour {snap.day} : les items reçus pendant ce jour seront redonnés.")
            changed = True

    if ctx.request_day_resync:
        ctx.request_day_resync = False
        ctx.applied_index = ctx.day_start_index.get(day_key, ctx.applied_index)
        changed = True

    if ctx.option("juice_mode") == 1 and gi.set_juice_floor(ctx.memory, snap, SAFE_JUICE_FLOOR):
        logger.info(f"Mode « safe » : jus remonté à {SAFE_JUICE_FLOOR:.0f} bouteilles.")

    if changed:
        await ctx.save_item_tracking()


def apply_item(ctx: Pikmin3Context, snap: gi.GameSnapshot, name: str) -> str:
    """Applique un item dans le jeu. Renvoie une description pour le journal."""
    assert ctx.memory is not None
    if name in fruits.FRUIT_JUICE:
        value = gi.add_juice(ctx.memory, snap, fruits.FRUIT_JUICE[name])
        return f"+{fruits.FRUIT_JUICE[name]:g} jus (total {value:g})"
    if name == p3_items.JUICE_DROP:
        value = gi.add_juice(ctx.memory, snap, p3_items.JUICE_DROP_AMOUNT)
        return f"+{p3_items.JUICE_DROP_AMOUNT:g} jus (total {value:g})"
    if name == p3_items.JUICE_LEAK_TRAP:
        value = gi.add_juice(ctx.memory, snap, -p3_items.JUICE_LEAK_AMOUNT, minimum=1.0)
        return f"piège : jus {value:g}"
    if name in p3_items.EXTRA_PIKMIN_SLOTS:
        slot = p3_items.EXTRA_PIKMIN_SLOTS[name]
        note = ""
        if not snap.onion_discovered(slot):
            # Oignon pas encore découvert : on donne des Pikmin rouges à la place.
            note = f" (Oignon {mm.ONION_SLOTS[slot][0]} pas encore découvert)"
            slot = mm.RED_SLOT
        gi.add_onion_pikmin(ctx.memory, snap, slot=slot, amount=p3_items.EXTRA_PIKMIN_AMOUNT)
        return f"+{p3_items.EXTRA_PIKMIN_AMOUNT} Pikmin dans l'Oignon {mm.ONION_SLOTS[slot][0]}{note}"
    if name == p3_items.ULTRA_SPICY_SPRAY:
        gi.add_sprays(ctx.memory, snap, 1)
        return "+1 spray ultra-épicé"
    if name == p3_items.ULTRA_SPICY_BERRY:
        value = gi.add_berries(ctx.memory, snap, p3_items.BERRY_AMOUNT)
        return f"+{p3_items.BERRY_AMOUNT} baie ultra-épicée (total {value})"
    if name == p3_items.PROGRESSIVE_PIKMIN_LIMIT:
        return f"limite de Pikmin : {ctx.pikmin_limit()}"
    return "item inconnu (ignoré)"


async def give_items(ctx: Pikmin3Context, snap: gi.GameSnapshot) -> None:
    received = ctx.items_received
    if ctx.applied_index >= len(received):
        return
    while ctx.applied_index < len(received):
        item = received[ctx.applied_index]
        name = ITEM_ID_TO_NAME.get(item.item, f"#{item.item}")
        logger.info(f"Item reçu : {name} ({apply_item(ctx, snap, name)})")
        ctx.applied_index += 1
    await ctx.save_item_tracking()


def checked_location_ids(ctx: Pikmin3Context, snap: gi.GameSnapshot) -> set[int]:
    """Identifiants des checks accomplis d'après l'instantané."""
    ids: set[int] = set()
    for n in range(1, min(fruits.TOTAL_FRUITS, snap.fruits_juiced) + 1):
        ids.add(p3_locations.FRUIT_BASE + n)
    if ctx.option("onion_checks", True):
        for slot in p3_locations.ONION_REQUIRED_LIMIT:
            if snap.onion_bits & mm.ONION_SLOTS[slot][1]:
                ids.add(p3_locations.ONION_LOCATION_ID[slot])
    if ctx.option("key_item_checks", True):
        for bit in p3_locations.KEY_ITEM_REQUIRED_LIMIT:
            if snap.key_item_bits & bit:
                ids.add(p3_locations.KEY_ITEM_BASE + bit.bit_length() - 1)
    # BÊTA : un check par bit allumé dans chaque ensemble de notes, dans la limite des options.
    note_counts = snap.note_counts
    for key, count in (ctx.option("note_counts", {}) or {}).items():
        base = p3_locations.NOTE_SET_LOCATIONS[key][0]
        for n in range(1, min(int(count), note_counts.get(key, 0)) + 1):
            ids.add(base + n)
    if ctx.option("day_checks", False):
        for day in range(2, min(int(ctx.option("day_check_max", 0)), snap.day) + 1):
            ids.add(p3_locations.DAY_BASE + day)
    if ctx.option("fruit_kind_checks", False):
        for n in range(1, min(int(ctx.option("fruit_kind_max", 0)), snap.fruit_type_count) + 1):
            ids.add(p3_locations.FRUIT_KIND_BASE + n)
    if ctx.option("story_event_checks", False):
        for n in range(1, min(int(ctx.option("story_event_count", 0)), snap.story_events) + 1):
            ids.add(p3_locations.STORY_EVENT_BASE + n)
    for population in ctx.option("population_milestones", []):
        if snap.population >= int(population):
            ids.add(p3_locations.POPULATION_BASE + int(population))
    return ids


def goal_reached(ctx: Pikmin3Context, snap: gi.GameSnapshot) -> bool:
    if ctx.option("goal", 0) == 1:
        return snap.population >= int(ctx.option("population_required", 300))
    return snap.fruits_juiced >= int(ctx.option("fruits_required", 40))


def track_discoveries(ctx: Pikmin3Context, snap: gi.GameSnapshot) -> None:
    """BÊTA : journal des découvertes (fonctionne aussi sans serveur Archipelago)."""
    assert ctx.memory is not None
    regions = gi.read_regions(ctx.memory, snap.state_address)
    for discovery in ctx.discovery.update(snap.state_address, snap.day, regions):
        logger.info(f"[Découverte] {discovery.region} état+0x{discovery.offset:04X} : "
                    f"0x{discovery.old:02X} -> 0x{discovery.new:02X} ({discovery.meaning})")


def report_check_events(ctx: Pikmin3Context, snap: gi.GameSnapshot) -> None:
    """BÊTA : console des checks (onglet « Checks ») : une phrase par check accompli, même sans serveur."""
    for event in ctx.check_events.update(snap, ctx.option("population_milestones") or None):
        text = event.message
        if event.location:
            location_id = p3_locations.LOCATION_NAME_TO_ID.get(event.location)
            if ctx.slot is None:
                text += f" → check « {event.location} » (hors connexion)"
            elif location_id in ctx.server_locations:
                text += f" → check « {event.location} »"
            else:
                text += " (pas un check de cette partie)"
        check_logger.info(("✔ " if event.location else "• ") + text)


async def sync_once(ctx: Pikmin3Context) -> None:
    if ctx.memory is None:
        connect_cemu(ctx)
        if ctx.memory is None:
            return

    snap = gi.read_snapshot(ctx.memory)
    ctx.last_snapshot = snap
    if snap is not None:
        track_discoveries(ctx, snap)
        report_check_events(ctx, snap)
    if ctx.slot is None or not ctx.storage_loaded:
        return

    update_mailbox(ctx)
    if snap is None:
        return

    await handle_day(ctx, snap)
    await give_items(ctx, snap)

    new_checks = checked_location_ids(ctx, snap) - ctx.locations_checked
    if new_checks:
        sent = await ctx.check_locations(new_checks)
        ctx.locations_checked |= new_checks
        if sent:
            logger.info(f"{len(sent)} check(s) envoyé(s).")

    if not ctx.finished_game and goal_reached(ctx, snap):
        await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
        ctx.finished_game = True
        logger.info("Objectif atteint !")


async def game_sync_task(ctx: Pikmin3Context) -> None:
    logger.info("Recherche de Cemu… (/cemu pour l'état, /state pour la partie, /checks, /note et /decouvertes pour la bêta)")
    while not ctx.exit_event.is_set():
        try:
            await asyncio.wait_for(ctx.watcher_event.wait(), SYNC_INTERVAL)
        except asyncio.TimeoutError:
            pass
        ctx.watcher_event.clear()
        try:
            await sync_once(ctx)
        except MemoryError_ as error:
            lose_cemu(ctx, str(error))
        except Exception:
            logger.error(traceback.format_exc())
            await asyncio.sleep(CEMU_RETRY_INTERVAL)


def main(*args: str) -> None:
    Utils.init_logging("Pikmin3BetaClient", exception_logger="Client")

    async def _main(parsed) -> None:
        ctx = Pikmin3Context(parsed.connect, parsed.password)
        if getattr(parsed, "name", None):
            ctx.auth = parsed.name
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="ServerLoop")
        if gui_enabled and not getattr(parsed, "nogui", False):
            ctx.run_gui()
        ctx.run_cli()
        ctx.sync_task = asyncio.create_task(game_sync_task(ctx), name="Pikmin3BetaSync")
        await ctx.exit_event.wait()
        ctx.watcher_event.set()
        ctx.server_address = None
        await ctx.shutdown()
        if ctx.sync_task:
            await ctx.sync_task
        if ctx.memory is not None:
            ctx.memory.close()

    parser = get_base_parser(description="Pikmin 3 Beta Archipelago Client (Cemu)")
    parser.add_argument("--name", default=None, help="Nom du slot.")
    parser.add_argument("url", nargs="?", help="URL de connexion Archipelago")
    parsed = handle_url_arg(parser.parse_args(args), parser=parser)

    import colorama
    colorama.just_fix_windows_console()
    asyncio.run(_main(parsed))
    colorama.deinit()
