"""
Installation du graphic pack Archipelago dans le dossier des graphic packs de Cemu.

Les fichiers sont lus depuis l'APWorld (dossier ou archive .apworld) via importlib.resources.
"""

from __future__ import annotations

import os
import re
from importlib import resources
from typing import Optional

from ..data.game_info import FINAL_GRAPHIC_PACK_FOLDER, GRAPHIC_PACK_FOLDER

PACK_FILES = ("rules.txt", "patches.txt")
# Anciens packs de test de la Phase 0 : ils patchent les mêmes adresses et doivent être désactivés.
PHASE0_TEST_PACKS = ("P3AP_Phase0_Test", "P3AP_Phase0_NoFruitJuice", "P3AP_Phase0_PikminLimit30")


def default_cemu_data_dir() -> str:
    return os.path.join(os.environ.get("APPDATA", ""), "Cemu")


def install_graphic_pack(cemu_data_dir: Optional[str] = None) -> str:
    """Copie le pack dans <dossier Cemu>/graphicPacks/Pikmin3_Archipelago. Renvoie le dossier cible."""
    cemu_dir = cemu_data_dir or default_cemu_data_dir()
    target = os.path.join(cemu_dir, "graphicPacks", GRAPHIC_PACK_FOLDER)
    os.makedirs(target, exist_ok=True)
    source = resources.files(__package__.rsplit(".", 1)[0]).joinpath("graphic_pack", GRAPHIC_PACK_FOLDER)
    for name in PACK_FILES:
        with open(os.path.join(target, name), "wb") as handle:
            handle.write(source.joinpath(name).read_bytes())
    return target


def installed_phase0_packs(cemu_data_dir: Optional[str] = None) -> list[str]:
    """Packs de test de la Phase 0 encore présents (à désactiver dans Cemu)."""
    folder = os.path.join(cemu_data_dir or default_cemu_data_dir(), "graphicPacks")
    return [name for name in PHASE0_TEST_PACKS if os.path.isdir(os.path.join(folder, name))]


def enabled_graphic_packs(cemu_data_dir: Optional[str] = None) -> set[str]:
    """Dossiers des graphic packs cochés dans Cemu (lus dans settings.xml ; vide si illisible)."""
    path = os.path.join(cemu_data_dir or default_cemu_data_dir(), "settings.xml")
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            text = handle.read()
    except OSError:
        return set()
    enabled = set()
    for match in re.finditer(r'<Entry\s+filename="graphicPacks/([^/"]+)/rules\.txt"([^>]*)>', text):
        if 'disabled="true"' not in match.group(2):
            enabled.add(match.group(1))
    return enabled


def final_pack_also_enabled(cemu_data_dir: Optional[str] = None) -> bool:
    """BÊTA : vrai si le pack de la version finale est coché en même temps que le pack bêta."""
    enabled = enabled_graphic_packs(cemu_data_dir)
    return FINAL_GRAPHIC_PACK_FOLDER in enabled and GRAPHIC_PACK_FOLDER in enabled
