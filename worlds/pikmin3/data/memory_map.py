"""
Carte mémoire de Pikmin 3 EUR v1 (module « carrot », 0x838BE11A) sous Cemu.

Toutes les adresses sont des adresses Wii U (« guest »). Détails, preuves et historique :
docs/phase0/findings.md. Légende des commentaires :
    ✅ vérifié en jeu   🔶 très probable, à confirmer   ❓ TODO: à trouver
"""

# --------------------------------------------------------------------------
# Pointeurs fixes (données du RPX, identiques d'un lancement à l'autre)
# --------------------------------------------------------------------------

GAME_DATA_PTR = 0x103E4488       # ✅ objet de données de partie (utilisé partout par le code)
STATE_OBJECT_PTR = 0x103E448C    # ✅ même objet vu 0x34 plus loin ; base de nos décalages « état »
PIKMIN_MANAGER_PTR = 0x103E288C  # ✅ gestionnaire des Pikmin (⚠ pointe ailleurs pendant l'atterrissage)

# --------------------------------------------------------------------------
# Données de partie : base = [GAME_DATA_PTR]
# --------------------------------------------------------------------------

GAME_DATA_MODE = 0x44            # 🔶 u32 : 0 = Histoire, 3 = Bingo Battle, 1–2 = Mission (?)
MODE_STORY = 0

# --------------------------------------------------------------------------
# Objet d'état : base = [STATE_OBJECT_PTR] (vu à 0x34A4D75C, stable)
# --------------------------------------------------------------------------

STATE_DAY = 0x48                 # ✅ u32, jour courant
STATE_JUICE = 0x50               # ✅ f32, bouteilles de jus
STATE_FRUIT_TYPE_COUNT = 0x54    # ✅ u32, sortes de fruits enregistrées (Fruit File) : 11 sortes pour 14 fruits (jour 11)
STATE_KEY_ITEM_BITS = 0x58       # ✅ u32, objets importants / améliorations (voir KEY_ITEM_BITS)
# ✅ Champ de bits des fruits pressés (1 bit par fruit), +0x5C à +0x83 : 320 bits, sans doute 5 blocs de 64
# (un par zone). Vérifié sur toutes les sauvegardes des jours 2 à 13 (single*.sav) : le nombre de bits = « ×N »
# du bilan. Le Pocked Airhead (jour 12) est en +0x66 : lire seulement à partir de +0x70 en oubliait.
STATE_FRUIT_BITS = 0x5C
STATE_FRUIT_BITS_SIZE = 40
STATE_ONION_BITS = 0xA4          # ✅ u8, Oignons / types découverts : bit (1 << type) (voir ONION_SLOTS)
STATE_ONION_COUNTS = 0xCC        # ✅ u32[type][maturité], 12 octets par type : type n en +0xCC + 12 × n
ONION_SLOT_STRIDE = 12
ONION_MATURITIES = 3             # feuille, bouton, fleur
STATE_SPRAY_COUNT = 0x598        # ✅ u32, Ultra-Spicy Nectar (sprays)
STATE_BERRY_COUNT = 0x59C        # ✅ u32, baies ultra-épicées (8 baies = 1 spray)
# Pas de stock de bombes : une Bomb Rock est portée par un Pikmin (type à part dans le sélecteur d'équipe,
# vu en jeu le 2026-09-30). Un item « Bomb Rock » demanderait de faire apparaître des bombes en jeu.
STATE_BOMB_COUNT = None

# Types de Pikmin : numéro n -> (nom, bit dans STATE_ONION_BITS = 1 << n). Pikmin de l'Oignon en +0xCC + 12 × n.
# Règle établie le 2026-10-01 (chat BÊTA, colonnes vues dans le menu de l'Oignon, voir COORDINATION.md).
ONION_SLOTS = {
    2: ("Blue", 0x04),      # ✅ 2026-10-01, Pikmin en +0xE4
    3: ("Red", 0x08),       # ✅ présent dès le départ, Pikmin en +0xF0
    5: ("Yellow", 0x20),    # ✅ jour 8, Pikmin en +0x108
    6: ("Winged", 0x40),    # ✅ 2026-10-01, Pikmin en +0x114
    7: ("Rock", 0x80),      # ✅ jour 2, Pikmin en +0x120
}
RED_SLOT = 3
# Type 4 = Pikmin BLANCS (bit 0x10, +0xFC) : absents de l'histoire, en sortir fait planter le jeu → jamais lu ni donné.
# Types 0 et 1 (bits 0x01, 0x02) : inconnus.

# « UniteOnyon » : Oignons fusionnés, même codage que STATE_ONION_BITS (chat BÊTA, 2026-10-01).
# Débloquer un type = allumer son bit dans STATE_ONION_BITS ET ici (jamais le premier seul : scène de fusion avec
# le mauvais Oignon puis plantage), et seulement pour la journée suivante (sorti le jour même → plantage ;
# débloqué la veille → normal, vérifié avec les ailés et les bleus). Un Oignon vide donne une pousse le lendemain.
STATE_ONION_MERGED = 0x908       # ✅
# Ordre des types débloqués par les items « Progressive Pikmin » (décision de l'utilisateur) : roc, jaune, ailé, bleu.
PROGRESSIVE_PIKMIN_TYPES = (7, 5, 6, 2)

# --------------------------------------------------------------------------
# Zones (champs « SingleGameParams » relevés par le chat BÊTA, voir COORDINATION.md)
# --------------------------------------------------------------------------
STATE_OPEN_AREA_FLAG = 0x909     # ✅ u8 « OpenAreaFlag » : bit n = zone n ouverte (forcé à 0x0F → 4ᵉ zone sur la carte)
STATE_SEEN_AREA_FLAG = 0x90A     # ✅ u8 « SeenAreaFlag » : zones déjà vues
# Bits des zones (tests du chat BÊTA, 2026-10-02) : 0x01 Tropical Wilds 🔶, 0x02 Garden of Hope 🔶,
# 0x04 Distant Tundra ✅, 0x08 Twilight River ✅, 0x10 Formidable Oak ✅ (zone du boss final, sans fruit).
# La carte montre toutes les zones jusqu'à la plus haute ouverte : on ferme en partant du haut. Le jeu remplit les
# zones sous la plus haute ouverte (sortie de Pikmin de l'Oignon) mais n'ouvre rien au-dessus (vérifié par la bêta).
AREA_FLAGS_AT_START = 0x03       # ✅ zones 0 et 1 ouvertes du jour 2 au jour 7 (sauvegardes single2…single7)
FINAL_ZONE_BIT = 0x10            # ✅ Formidable Oak (forcée → sur la carte du jour 19 ; ouverte par l'histoire après Louie)
# Bits ouverts dans l'ordre par les items « Progressive Zone » : les 3 zones qui suivent les 2 du départ.
PROGRESSIVE_ZONE_BITS = (
    0x04,                        # ✅ Distant Tundra (ouverte par l'histoire au jour 8)
    0x08,                        # ✅ Twilight River
    FINAL_ZONE_BIT,              # ✅ Formidable Oak
)
# Avant ce jour, le client ne touche pas aux zones (jour 1 : tutoriel, valeur d'origine inconnue).
ZONE_LOCK_FIRST_DAY = 2
ZONE_NAMES = {0x01: "Tropical Wilds", 0x02: "Garden of Hope", 0x04: "Distant Tundra", 0x08: "Twilight River",
              0x10: "Formidable Oak"}

# Victoire sur le boss final (objectif « final_boss ») : (décalage dans l'objet d'état, masque).
# ✅ bit 0x04 allumé à la victoire (2026-10-03 12:33:14, jamais vu dans les sauvegardes des jours 2–27) et présent dans
# single28.sav écrite après la fin (0x1C : bits 0x08 et 0x10 ajoutés pendant la fin). Vérifié par les chats BÊTA et FINAL.
FINAL_BOSS_FLAG = (0x260F, 0x04)
# Compteur d'avancement de l'histoire (octet bas de +0x4C) : 0x82 ouverture de Formidable Oak par l'histoire,
# 0x84 scène « Olimar et le boss » (le boss ne se bat qu'à partir de là), 0x8C boss vaincu. Pas encore utilisé.
STATE_STORY_PROGRESS = 0x4F

# Bits de STATE_KEY_ITEM_BITS : bit -> nom
KEY_ITEM_BITS = {
    0x01: "Louie",              # ✅ jour 23 (2026-10-03 11:26:41, 0xDA -> 0xDB, 2 s après le sauvetage de Louie)
    0x02: "Data Glutton",       # 🔶 apparu entre les jours 3 et 7
    0x10: "Anti-Electrifier",   # ✅ jour 9
    0x40: "Metal Suit Z",       # ✅ jour 13 (2026-10-01 19:48:53, 0x9A -> 0xDA)
    0x80: "Dodge Whistle",      # ✅ jour 10
    # 0x08 : présent dès le départ, rôle ❓
    # ❓ TODO: Folded Data Glutton, Cosmic Drive Key, autres améliorations
}

# --------------------------------------------------------------------------
# Notes (fichiers de données du GamePad)
# --------------------------------------------------------------------------
# Règle trouvée par le chat BÊTA (2026-10-03) : chaque catégorie de notes du GamePad a son ensemble de 256 bits,
# catégorie c à état+0x27C0 + 0x20 × c, note n° n = bit n des mots big-endian. Le badge « nouvelle note » du GamePad
# donne la catégorie (état+0x28A3) et le numéro (état+0x28A7) de la dernière note reçue.
STATE_NOTE_CATEGORIES = 0x27C0   # ✅
NOTES_SET_SIZE = 0x20
NOTE_CATEGORY_COUNT = 7          # A à G (E jamais vue allumée)
STATE_NOTE_BADGE_CATEGORY = 0x28A3  # ✅ u8 (information, pas utilisé par le client)
STATE_NOTE_BADGE_NUMBER = 0x28A7    # ✅ u8
# Regroupements observés (notes annoncées par l'utilisateur, jours 12–26) :
TUTORIAL_NOTE_CATEGORIES = (0, 1, 2)  # A, B, C : « notes tuto » (Pikmin-ology et autres conseils)
OLIMAR_NOTE_CATEGORIES = (3, 5)       # D, F : notes d'Olimar (F reçoit aussi des notes données par l'histoire)
SECRET_MEMO_CATEGORIES = (6,)         # G : Secret Memos (« Secret Memo 3 » = bit 8)

# --------------------------------------------------------------------------
# Gestionnaire des Pikmin : base = [PIKMIN_MANAGER_PTR]
# --------------------------------------------------------------------------

PIKMIN_FIELD_TOTAL = 0xEE8       # ✅ u32, Pikmin sur le terrain (tableau [total, équipe 0, équipe 1])
PIKMIN_SPROUTS_TOTAL = 0xEF4     # 🔶 u32, pousses (tableau parallèle)
FIELD_LIMIT_VANILLA = 100

# --------------------------------------------------------------------------
# Boîte aux lettres du graphic pack (code cave)
# --------------------------------------------------------------------------

MAILBOX_ADDRESS = 0x01800000     # ✅ début de la zone des code caves (log de Cemu)
# Zone fouillée si d'autres packs avec code cave sont actifs (la boîte aux lettres est alors plus loin).
MAILBOX_SEARCH_SIZE = 0x10000
MAILBOX_SIGNATURE = b"P3APMBOX"
MAILBOX_VERSION = 2
MAILBOX_VERSION_OFFSET = 0x08    # u32
MAILBOX_FLAGS_OFFSET = 0x0C      # u32 : bit 0 = supprimer le jus des fruits pressés
MAILBOX_FLAG_NO_FRUIT_JUICE = 0x1
MAILBOX_PIKMIN_LIMIT_OFFSET = 0x10  # u32 : limite de Pikmin sur le terrain (100 par défaut)
# u32 écrit par le client (jamais lu par le jeu). Le code cave est réinitialisé à 0 à chaque
# lancement du jeu : un marqueur à 0 signifie que la partie vient d'être rechargée depuis la sauvegarde.
MAILBOX_CLIENT_MARKER_OFFSET = 0x14
MAILBOX_CLIENT_MARKER = 0x41504F4B  # "APOK"

# Plafond du jus dans le jeu (constante lue à 0x1033F388).
JUICE_MAX = 99.0
