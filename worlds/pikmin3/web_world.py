from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld

from .options import option_groups


class Pikmin3WebWorld(WebWorld):
    game = "Pikmin 3"
    theme = "grassFlowers"

    setup_en = Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Pikmin 3 (Cemu) for Archipelago.",
        "English",
        "setup_en.md",
        "setup/en",
        ["2dcraft2"],
    )
    setup_fr = Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Pikmin 3 (Cemu) for Archipelago.",
        "French",
        "setup_fr.md",
        "setup/fr",
        ["2dcraft2"],
    )
    tutorials = [setup_en, setup_fr]
    option_groups = option_groups
