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
# En réalité STATE_ONION_BITS est le haut d'un ensemble de 64 drapeaux (mots big-endian état+0xA4 et état+0xA8).
# Types 0 et 1 (bits 0x01, 0x02) : inconnus. Type 4 = Pikmin BLANCS (bit 0x10) : absents de l'histoire, en sortir
# un fait planter le jeu → jamais lu ni donné (absent de ONION_SLOTS).
ONION_SLOTS = {
    2: ("Blue", 0x04),      # ✅ trouvé par élimination le 2026-10-01 (colonne bleue) ; sortis normalement le lendemain
    3: ("Red", 0x08),       # ✅ (présent dès le départ)
    5: ("Yellow", 0x20),    # ✅ jour 8
    6: ("Winged", 0x40),    # ✅ forcé le 2026-10-01 : Pikmin roses sortis et normaux
    7: ("Rock", 0x80),      # ✅ jour 2
}
RED_SLOT = 3
WHITE_TYPE = 4                  # ⛔ ne jamais écrire ce type (plantage)
# Bits vus seulement en les forçant (pas encore par la découverte normale dans l'histoire).
ONION_SLOTS_UNVERIFIED = {2, 6}

# Paramètres de partie nommés (« SingleGameParams ») : noms dans les données du jeu (0x1033F40C…), relevés dans
# la fonction de sauvegarde 0x0300A2xx–0x0300ACxx (base r27 = état+0x14, déduite de DopingNum = sprays).
STATE_UNITE_ONYON = 0x908        # 🔶 u8 « UniteOnyon » : Oignons FUSIONNÉS (même codage que STATE_ONION_BITS).
#                                   Découvert sans être fusionné → scène de fusion à l'atterrissage suivant.
STATE_OPEN_AREA_FLAG = 0x909     # ✅ u8 « OpenAreaFlag » : zones ouvertes (bit n = zone n). 0x07 au jour 13 ;
#                                   0x0F forcé le 2026-10-01 → la 4ᵉ zone apparaît sur la carte, le vaisseau s'y pose.
#                                   Sauvegardes de l'utilisateur : 0x03 aux jours 2–7, 0x07 à partir du jour 8.
STATE_SEEN_AREA_FLAG = 0x90A     # 🔶 u8 « SeenAreaFlag » : zones déjà vues. 0x05 au jour 2 (zone 2 vue avant
#                                   d'être ouverte), 0x07 aux jours 3–14, 0x0F au jour 15 (après la pose en zone 4).
STATE_AREA_FLAG_90B = 0x90B      # ❓ u8 sans nom connu : égal à SeenAreaFlag dans toutes les sauvegardes (jours 2–15).
# Zones : nom de chaque bit, relevé en jeu par élimination avec l'utilisateur (TODO: à trouver pour les autres).
# ✅ La carte montre toutes les zones jusqu'à la plus haute ouverte (2026-10-02) : 0x0B montre aussi Distant
# Tundra, 0x03 la cache. Pour fermer des zones, il faut donc partir du haut (Formidable Oak, puis Twilight River…).
AREA_BITS = {
    0: "Tropical Wilds",    # 🔶 curseur 0 en y atterrissant (jour 16)
    1: "Garden of Hope",    # 🔶 par élimination
    2: "Distant Tundra",    # ✅ 0x03 (zones 2–4 fermées) → absente de la carte du jour 19
    3: "Twilight River",    # ✅ 2026-10-02 : bit fermé → zone absente de la carte ; rouvert → de retour
    4: "Formidable Oak",    # ✅ 2026-10-02 : bit 0x10 forcé → 5ᵉ zone sur la carte du jour 19 (pas encore visitée)
}
# 🔶 u32 zone sous le curseur de la carte (SelectedAreaID ?) : bouge avec le curseur (0 Tropical Wilds,
# 2 Distant Tundra, 3 Twilight River, 2026-10-02) ; +0x594 = zone de la dernière journée jouée (?).
STATE_CURRENT_AREA = 0x590
# 🔶 u32 × 5 : dernier jour joué dans chaque zone (-1 = jamais), zone n à +0x98C + 4n. Au jour 18 :
# [16, 15, 17, 14, -1] → 5 zones, la 5ᵉ (bit 0x10) jamais visitée.
STATE_AREA_LAST_DAY = 0x98C
AREA_COUNT = 5
# ⚠ Sortir des Pikmin de l'Oignon recalcule OpenAreaFlag : il remplit les zones sous la plus haute ouverte au
# chargement de la journée (0x0B au jour 17 → 0x0F, bit 4 forcé en pleine journée effacé). Avec 0x03 (jour 19),
# rien n'est rouvert ✅ → verrouiller des zones en partant du haut marche sans patch.

# Bits de STATE_KEY_ITEM_BITS : bit -> nom
KEY_ITEM_BITS = {
    0x02: "Data Glutton",       # 🔶 apparu entre les jours 3 et 7
    0x10: "Anti-Electrifier",   # ✅ jour 9
    0x40: "Metal Suit Z",       # ✅ jour 13 (2026-10-01, relevé par le chat FINAL : 0x9A -> 0xDA)
    0x80: "Dodge Whistle",      # ✅ jour 10
    # 0x08 : présent dès le départ, rôle ❓
    # ❓ TODO: Folded Data Glutton, Cosmic Drive Key, autres améliorations
}

# --------------------------------------------------------------------------
# Notes (fichiers de données du GamePad)
# --------------------------------------------------------------------------
# Objet « ensemble de flags » vu à 0x34A4FF18 (vtable 0x10345EE8), toujours dans le même bloc
# mémoire que l'objet d'état → adressé par décalage depuis l'objet d'état (🔶 à confirmer
# sur une partie neuve). Chaque ensemble fait 256 bits (0x20 octets).
STATE_NOTES_TUTORIAL = 0x27E0    # 🔶 ensemble B (0x34A4FF3C) : notes de tutoriel
STATE_NOTES_OLIMAR = 0x2820      # 🔶 ensemble D (0x34A4FF7C) : notes d'Olimar
NOTES_SET_SIZE = 0x20

# BÊTA : les ensembles de notes sont comptés séparément, car leur sens n'est pas encore sûr.
# A : « Pikmin-ology » (#7 vu le 2026-09-30) et tutoriels lus ; 20 bits au jour 13.
# B : tutoriels (1 au jour 8) ; 5 bits au jour 13. C'est le seul ensemble lu par le client FINAL.
# C : documents ramassés / scènes vues (Pellet Posies, Anti-Electrifier) ; 22 bits au jour 13.
# D : notes d'Olimar ✅ ; 3 bits au jour 13.
NOTE_SETS = {
    "A": 0x27C0,   # 🔶
    "B": 0x27E0,   # 🔶
    "C": 0x2800,   # 🔶
    "D": 0x2820,   # ✅ notes d'Olimar
}
# Ensemble F (0x34A4FFBC) : étapes d'histoire 🔶 (bit 0 au Data Glutton, bit 1 au sauvetage de Charlie).
STATE_STORY_FLAGS = 0x2860
# Octet 0x34A4FFFF : nombre de nouveautés non lues sur le GamePad (« badge ») 🔶, à ignorer dans les découvertes.
STATE_GAMEPAD_BADGE = 0x28A3

# BÊTA : zones surveillées par le journal des découvertes (décalages depuis l'objet d'état).
# Les octets qui bougent trop souvent (minuteurs, positions) sont écartés automatiquement par le client.
DISCOVERY_REGIONS = (
    ("sortes de fruits / objets importants", 0x54, 0x08),
    ("fruits pressés", 0x5C, 0x28),
    ("Oignons découverts et voisins", 0xA4, 0x28),
    ("inventaire (sprays, baies)", 0x598, 0x08),
    ("Oignons fusionnés / zones ouvertes / zones vues", 0x900, 0x10),
    ("drapeaux d'histoire / événements", 0x2600, 0x1A0),
    ("ensembles de notes (Z, A–G)", 0x27A0, 0x100),
)

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
# BÊTA : signature différente du pack FINAL (« P3APMBOX »), pour que chaque client ne reconnaisse que son pack.
MAILBOX_SIGNATURE = b"P3APBETA"
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
