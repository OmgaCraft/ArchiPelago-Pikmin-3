"""
Identité de la version du jeu prise en charge.

Source : log.txt de Cemu 2.6 (voir docs/phase0/version_info.md).
Les patches du graphic pack ne s'appliquent qu'au module dont la somme correspond.
"""

# BÊTA : jeu distinct dans Archipelago, pour coexister avec la version finale (« Pikmin 3 »).
GAME_NAME = "Pikmin 3 Beta"
WORLD_VERSION = "0.1.0"

# Pikmin 3 (Europe) (EnFrDeEsIt), disque, sans mise à jour ni DLC.
TITLE_ID_EUR = 0x000500001012BE00
TITLE_VERSION_EUR = 1                  # « TitleVersion: v1 »
MODULE_NAME = "carrot"                 # nom interne du RPX
MODULE_CHECKSUM_EUR_V1 = 0x838BE11A    # valeur de « moduleMatches »
RPX_HASH_EUR_V1 = 0x3EABC0BB

# Autres régions connues (non prises en charge en V1).
TITLE_ID_USA = 0x000500001012BD00
TITLE_ID_JPN = 0x000500001012BC00

# Nom du dossier du graphic pack installé dans Cemu.
GRAPHIC_PACK_FOLDER = "Pikmin3_Archipelago_Beta"
# Pack de la version finale : il patche les mêmes adresses, il ne doit pas être actif en même temps.
FINAL_GRAPHIC_PACK_FOLDER = "Pikmin3_Archipelago"
