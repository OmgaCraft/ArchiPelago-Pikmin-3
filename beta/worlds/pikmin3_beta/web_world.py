from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld

from .data.game_info import GAME_NAME
from .options import option_groups


class Pikmin3BetaWebWorld(WebWorld):
    game = GAME_NAME
    theme = "grassFlowers"

    setup_en = Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up the Pikmin 3 beta (Cemu) for Archipelago.",
        "English",
        "setup_en.md",
        "setup/en",
        ["2dcraft2"],
    )
    setup_fr = Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up the Pikmin 3 beta (Cemu) for Archipelago.",
        "French",
        "setup_fr.md",
        "setup/fr",
        ["2dcraft2"],
    )
    tutorials = [setup_en, setup_fr]
    option_groups = option_groups
