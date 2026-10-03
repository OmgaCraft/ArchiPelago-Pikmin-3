"""
Types de fruits de Pikmin 3 (Wii U) et jus rapporté.

Source des valeurs : Pikipedia (page « Fruit »), extraction automatique.
Vérifié en jeu (jus observé au pressage) : Sunseed Berry 1.0, Face Wrinkler (citron) 1.5,
Zest Bomb 1.5, Fire-Breathing Feast 2.5. Les autres valeurs restent « à confirmer ».

Le jeu compte 66 fruits (dont certains en plusieurs morceaux, ex. Dawn/Dusk Pustules),
répartis sur 4 zones (aucun dans Formidable Oak), pour 30 types.
"""

TOTAL_FRUITS = 66

# Nom anglais du type -> jus en bouteilles (float)
FRUIT_JUICE = {
    "Astringent Clump": 2.0,
    "Blonde Impostor": 1.5,
    "Citrus Lump": 1.5,
    "Crimson Banquet": 3.0,
    "Crunchy Deluge": 2.0,
    "Cupid's Grenade": 0.5,
    "Dapper Blob": 1.0,
    "Dawn Pustules": 1.0,
    "Delectable Bouquet": 1.5,
    "Disguised Delicacy": 1.5,
    "Dusk Pustules": 1.0,
    "Face Wrinkler": 1.5,
    "Fire-Breathing Feast": 2.5,
    "Heroine's Tear": 2.5,
    "Insect Condo": 2.0,
    "Juicy Gaggle": 0.5,
    "Lesser Mock Bottom": 1.0,
    "Mock Bottom": 2.0,
    "Pocked Airhead": 2.5,
    "Portable Sunset": 2.0,
    "Scaly Custard": 1.5,
    "Searing Acidshock": 1.0,
    "Seed Hive": 2.5,
    "Slapstick Crescent": 2.5,
    "Stellar Extrusion": 2.0,
    "Sunseed Berry": 1.0,
    "Tremendous Sniffer": 2.0,
    "Velvety Dreamdrop": 1.0,
    "Wayward Moon": 3.0,
    "Zest Bomb": 1.5,
}

# Correspondance bit du champ de fruits -> fruit observé (à compléter au fil du jeu).
# Numéro de bit = octet * 8 + bit (bit 0 = 0x01), à partir de STATE_FRUIT_BITS.
# Sert à la documentation et aux futurs checks nommés ; la V1 compte simplement les bits.
OBSERVED_FRUIT_BITS = {
    87: "Pocked Airhead (jour 12)",
    160: "Sunseed Berry (1)",
    161: "Sunseed Berry (2)",
    170: "Face Wrinkler",
    171: "Zest Bomb",
    176: "Fire-Breathing Feast (butin de boss)",
    258: "Dusk Pustules (fruit en morceaux)",
    259: "? (jour 8, +1.0)",
    267: "Velvety Dreamdrop",
    268: "Dapper Blob",
    270: "Citrus Lump",
    271: "Dawn Pustules (fruit en morceaux)",
    276: "? (jour 11, +3.0, mangue)",
    278: "Cupid's Grenade (1)",
    279: "Cupid's Grenade (2)",
}
