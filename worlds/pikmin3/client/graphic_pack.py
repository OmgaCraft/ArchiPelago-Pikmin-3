"""
Installation du graphic pack Archipelago dans le dossier des graphic packs de Cemu.

Les fichiers sont lus depuis l'APWorld (dossier ou archive .apworld) via importlib.resources.
"""

from __future__ import annotations

import os
from importlib import resources
from typing import Optional

from ..data.game_info import GRAPHIC_PACK_FOLDER

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
