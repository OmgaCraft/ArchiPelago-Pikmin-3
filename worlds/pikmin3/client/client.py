"""
Client Archipelago de Pikmin 3 (Wii U / Cemu).

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
import traceback
from typing import Any, Optional

import Utils
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
from .graphic_pack import install_graphic_pack, installed_phase0_packs

SYNC_INTERVAL = 0.5
CEMU_RETRY_INTERVAL = 5.0
SAFE_JUICE_FLOOR = 2.0
ITEM_ID_TO_NAME = {code: name for name, code in p3_items.ITEM_NAME_TO_ID.items()}


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
        logger.info("Dans Cemu : Options > Graphic packs > Pikmin 3 > Mods > Archipelago (cocher), puis relancer le jeu.")
        leftovers = installed_phase0_packs(cemu_data_dir or None)
        if leftovers:
            logger.warning("Désactivez les anciens packs de test : " + ", ".join(leftovers))

    def _cmd_resync_day(self) -> None:
        """Redonne les items reçus depuis le début du jour en cours (après un rechargement non détecté)."""
        if isinstance(self.ctx, Pikmin3Context):
            self.ctx.request_day_resync = True
            logger.info("Resynchronisation demandée : prise en compte au prochain passage.")


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

    # --- Serveur -----------------------------------------------------------------

    @property
    def storage_key(self) -> str:
        return f"pikmin3_items_{self.team}_{self.slot}"

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
        ui.base_title = "Archipelago Pikmin 3 Client"
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

    def received_count(self, name: str) -> int:
        return sum(1 for item in self.items_received if ITEM_ID_TO_NAME.get(item.item) == name)

    def zone_items(self) -> int:
        """Nombre d'items « Progressive Zone » reçus."""
        return self.received_count(p3_items.PROGRESSIVE_ZONE)

    def pikmin_type_items(self) -> int:
        """Nombre d'items « Progressive Pikmin » reçus."""
        return self.received_count(p3_items.PROGRESSIVE_PIKMIN)

    def log_state(self) -> None:
        snap = self.last_snapshot
        if snap is None:
            logger.info("Aucune partie lisible (Cemu fermé, menu, chargement ou mode Mission).")
            return
        logger.info(
            f"Jour {snap.day} | jus {snap.juice:.1f} | fruits pressés {snap.fruits_juiced} | "
            f"population {snap.population} (terrain {snap.field}) | notes tuto {snap.tutorial_notes}, "
            f"Olimar {snap.olimar_notes}, Secret Memos {snap.secret_memos} | limite de Pikmin {self.pikmin_limit()} | "
            f"zones : {gi.zone_names(snap.open_areas)} ({self.zone_items()} item(s) de zone) | "
            f"boss final {'vaincu' if gi.final_boss_defeated(self.memory, snap) else 'pas encore vaincu'} | "
            f"items donnés {self.applied_index}/{len(self.items_received)}"
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
    logger.info(f"Cemu : {ctx.cemu_status}")


def lose_cemu(ctx: Pikmin3Context, reason: str) -> None:
    if ctx.memory is not None:
        ctx.memory.close()
    ctx.memory = None
    ctx.mailbox_address = None
    ctx.session_day = None
    ctx.last_snapshot = None
    ctx.cemu_status = f"déconnecté ({reason})"
    logger.info(f"Cemu : {ctx.cemu_status}")


def update_mailbox(ctx: Pikmin3Context) -> None:
    assert ctx.memory is not None
    if ctx.mailbox_address is None or not gi.mailbox_valid(ctx.memory, ctx.mailbox_address):
        ctx.mailbox_address = gi.find_mailbox(ctx.memory)
        if ctx.mailbox_address is None:
            if not ctx.warned_no_pack:
                logger.warning(
                    "Graphic pack Archipelago inactif : les fruits donneront leur jus en plus des items, "
                    "et la limite de Pikmin reste à 100. Utilisez /install_pack puis activez-le dans Cemu."
                )
                ctx.warned_no_pack = True
            return
        logger.info(f"Graphic pack Archipelago détecté (boîte aux lettres 0x{ctx.mailbox_address:08X}).")
        ctx.warned_no_pack = False
    gi.write_mailbox(ctx.memory, ctx.mailbox_address, no_fruit_juice=True, pikmin_limit=ctx.pikmin_limit())
    if gi.consume_game_restart(ctx.memory, ctx.mailbox_address):
        # Jeu (re)lancé : la partie sera chargée depuis la sauvegarde du début du jour.
        ctx.game_restarted = True


# --------------------------------------------------------------------------
# Jours, items, checks
# --------------------------------------------------------------------------

def apply_pikmin_types(ctx: Pikmin3Context, snap: gi.GameSnapshot) -> None:
    """Débloque les types de Pikmin reçus (« Progressive Pikmin »). Appelé seulement au changement de jour."""
    if not ctx.option("progressive_pikmin", False):
        return
    types = mm.PROGRESSIVE_PIKMIN_TYPES[:ctx.pikmin_type_items()]
    for pikmin_type in gi.unlock_pikmin_types(ctx.memory, snap, types):
        logger.info(f"Pikmin {mm.ONION_SLOTS[pikmin_type][0]} débloqués pour la journée qui commence "
                    f"(Oignon vide : une pousse arrive le lendemain).")


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
        # Le jour change dès le début de la fin de journée, avant la sauvegarde : un type de Pikmin débloqué
        # maintenant est sauvegardé et chargé avec la journée suivante (seul moment sûr).
        apply_pikmin_types(ctx, snap)
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
    if name == p3_items.EXTRA_RED_PIKMIN:
        gi.add_onion_pikmin(ctx.memory, snap, slot=mm.RED_SLOT, amount=p3_items.EXTRA_PIKMIN_AMOUNT)
        return f"+{p3_items.EXTRA_PIKMIN_AMOUNT} Pikmin Rouges dans l'Oignon"
    if name == p3_items.ULTRA_SPICY_SPRAY:
        gi.add_sprays(ctx.memory, snap, 1)
        return "+1 spray ultra-épicé"
    if name == p3_items.PROGRESSIVE_PIKMIN_LIMIT:
        return f"limite de Pikmin : {ctx.pikmin_limit()}"
    if name == p3_items.PROGRESSIVE_ZONE:
        return f"zone {ctx.zone_items()}/{p3_items.ZONE_ITEM_COUNT} débloquée"  # ouverture : apply_zones
    if name == p3_items.PROGRESSIVE_PIKMIN:
        return "nouveau type de Pikmin à la fin de la journée"  # déblocage : apply_pikmin_types
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


def apply_zones(ctx: Pikmin3Context, snap: gi.GameSnapshot) -> None:
    """Impose les zones débloquées par les items reçus : ouvre les zones reçues et referme celles que l'histoire
    ouvre trop tôt. Refait à chaque passage : résiste aux rechargements et au recalcul du jeu."""
    if not ctx.option("progressive_zones", False) or snap.day < mm.ZONE_LOCK_FIRST_DAY:
        return
    opened, closed = gi.set_zones(ctx.memory, snap, gi.allowed_zone_bits(ctx.zone_items()))
    if opened:
        logger.info(f"Zone(s) ouverte(s) sur la carte du vaisseau : {gi.zone_names(opened)}.")
    if closed:
        logger.info(f"Zone(s) refermée(s) en attendant l'item « Progressive Zone » : {gi.zone_names(closed)}.")


def checked_location_ids(ctx: Pikmin3Context, snap: gi.GameSnapshot) -> set[int]:
    """Identifiants des checks accomplis d'après l'instantané."""
    ids: set[int] = set()
    for n in range(1, min(fruits.TOTAL_FRUITS, snap.fruits_juiced) + 1):
        ids.add(p3_locations.FRUIT_BASE + n)
    if ctx.option("onion_checks", True) and not ctx.option("progressive_pikmin", False):
        for slot in p3_locations.ONION_REQUIRED_LIMIT:
            if snap.onion_bits & mm.ONION_SLOTS[slot][1]:
                ids.add(p3_locations.ONION_LOCATION_ID[slot])
    if ctx.option("key_item_checks", True):
        for bit in p3_locations.KEY_ITEM_REQUIRED_LIMIT:
            if snap.key_item_bits & bit:
                ids.add(p3_locations.KEY_ITEM_BASE + bit.bit_length() - 1)
    if ctx.option("note_checks", False):
        for n in range(1, min(int(ctx.option("tutorial_note_count", 0)), snap.tutorial_notes) + 1):
            ids.add(p3_locations.TUTORIAL_NOTE_BASE + n)
        for n in range(1, min(int(ctx.option("olimar_note_count", 0)), snap.olimar_notes) + 1):
            ids.add(p3_locations.OLIMAR_NOTE_BASE + n)
    for n in range(1, min(int(ctx.option("secret_memo_count", 0)), snap.secret_memos) + 1):
        ids.add(p3_locations.SECRET_MEMO_BASE + n)
    for population in ctx.option("population_milestones", []):
        if snap.population >= int(population):
            ids.add(p3_locations.POPULATION_BASE + int(population))
    return ids


def goal_reached(ctx: Pikmin3Context, snap: gi.GameSnapshot) -> bool:
    goal = ctx.option("goal", 0)
    if goal == 1:
        return snap.population >= int(ctx.option("population_required", 300))
    enough_fruits = snap.fruits_juiced >= int(ctx.option("fruits_required", 40))
    if goal == 2:
        # Boss final + fruits demandés.
        return enough_fruits and gi.final_boss_defeated(ctx.memory, snap)
    return enough_fruits


async def sync_once(ctx: Pikmin3Context) -> None:
    if ctx.memory is None:
        connect_cemu(ctx)
        if ctx.memory is None:
            return
    if ctx.slot is None or not ctx.storage_loaded:
        return

    update_mailbox(ctx)
    snap = gi.read_snapshot(ctx.memory)
    ctx.last_snapshot = snap
    if snap is None:
        return

    await handle_day(ctx, snap)
    await give_items(ctx, snap)
    apply_zones(ctx, snap)

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
    logger.info("Recherche de Cemu… (/cemu pour l'état, /state pour la partie)")
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
    Utils.init_logging("Pikmin3Client", exception_logger="Client")

    async def _main(parsed) -> None:
        ctx = Pikmin3Context(parsed.connect, parsed.password)
        if getattr(parsed, "name", None):
            ctx.auth = parsed.name
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="ServerLoop")
        if gui_enabled and not getattr(parsed, "nogui", False):
            ctx.run_gui()
        ctx.run_cli()
        ctx.sync_task = asyncio.create_task(game_sync_task(ctx), name="Pikmin3Sync")
        await ctx.exit_event.wait()
        ctx.watcher_event.set()
        ctx.server_address = None
        await ctx.shutdown()
        if ctx.sync_task:
            await ctx.sync_task
        if ctx.memory is not None:
            ctx.memory.close()

    parser = get_base_parser(description="Pikmin 3 Archipelago Client (Cemu)")
    parser.add_argument("--name", default=None, help="Nom du slot.")
    parser.add_argument("url", nargs="?", help="URL de connexion Archipelago")
    parsed = handle_url_arg(parser.parse_args(args), parser=parser)

    import colorama
    colorama.just_fix_windows_console()
    asyncio.run(_main(parsed))
    colorama.deinit()
