# Phase 0 — Résultats

Légende : ✅ vérifié · 📖 source externe (wiki/guide), à confirmer en jeu · ❓ à trouver

Voir aussi : [version_info.md](version_info.md) (version, émulateur, mémoire)
et [protocole_en_jeu.md](protocole_en_jeu.md) (marche à suivre en jeu).

---

## 0.B Contenu du jeu

### Fruits 📖
- **66 fruits** au total, répartis sur **4 zones** : Tropical Wilds, Garden of Hope,
  Distant Tundra, Twilight River. **Aucun fruit dans Formidable Oak.**
- **30 types** de fruit : certains types apparaissent plusieurs fois
  → l'ID d'un check doit identifier l'**exemplaire** (placement), pas le type.
- Les versions dorées n'existent qu'en Mission / Bingo Battle.
- Répartition par zone : TODO (les extractions de guides sont incohérentes ;
  à établir en jeu ou depuis les fichiers de carte).

Jus par type (Pikipedia, extraction automatique, **à vérifier**) :

| Type | Jus | Type | Jus | Type | Jus |
|---|---|---|---|---|---|
| Astringent Clump | 2.0 | Face Wrinkler | 1.5 | Portable Sunset | 2.0 |
| Blonde Impostor | 1.5 | Fire-Breathing Feast | 2.5 | Scaly Custard | 1.5 |
| Citrus Lump | 1.5 | Heroine's Tear | 2.5 | Searing Acidshock | 1.0 |
| Crimson Banquet | 3.0 | Insect Condo | 2.0 | Seed Hive | 2.5 |
| Crunchy Deluge | 2.0 | Juicy Gaggle | 0.5 | Slapstick Crescent | 2.5 |
| Cupid's Grenade | 0.5 | Lesser Mock Bottom | 1.0 | Stellar Extrusion | 2.0 |
| Dapper Blob | 1.0 | Mock Bottom | 2.0 | Sunseed Berry | 1.0 |
| Dawn Pustules | 1.0 | Pocked Airhead | 2.5 | Tremendous Sniffer | 2.0 |
| Delectable Bouquet | 1.5 | Dusk Pustules | 1.0 | Velvety Dreamdrop | 1.0 |
| Disguised Delicacy | 1.5 | Wayward Moon | 3.0 | Zest Bomb | 1.5 |

### Types de Pikmin, Oignons, capitaines 📖
- 5 types en Histoire : Rouge, Roche, Jaune, Ailé, Bleu. Ordre et zone de découverte : ❓
  (les sources consultées se contredisent).
- **Blancs et Violets : uniquement en Mission et Bingo Battle**, absents de l'Histoire.
- Capitaines : Alph, Brittany, Charlie ; Louie est sauvé du **Scornet Maestro** ;
  Olimar n'est jouable qu'en Mission. Moments où chacun rejoint le groupe : ❓

### Objets importants et boss 📖
| Élément | Détail |
|---|---|
| Data Glutton | Lâché par l'**Armored Mawdad**, débloque la **Distant Tundra** |
| Folded Data Glutton | Lâché par le **Sandbelching Meerslug**, agrandit la portée de communication |
| Cosmic Drive Key | Objet central de l'histoire (détenu par Olimar) |
| Boss | Armored Mawdad, Vehemoth Phosbat, Sandbelching Meerslug, Scornet Maestro, Quaggled Mireclops, **Plasm Wraith (final)** |

### Améliorations et capacités 📖
- **Dodge Whistle** : amélioration de combinaison trouvée dans la **Distant Tundra**,
  nécessaire pour esquiver. → check + item crédibles.
- **Anti-Electrifier** ✅ (vu en jeu, jour 9) : amélioration de combinaison **enterrée** dans la Distant Tundra (protège
  les capitaines de l'électricité). Il existe donc plusieurs améliorations → item « Suit Upgrade » crédible.
- Autres améliorations de combinaison : ❓ (liste complète à établir).
- Lock-on (ZL maintenu) et charge (liée au lock-on) : disponibles dès le début ? ❓

### Data Files 📖
- **Secret Files / Secret Memos : 10**, **2 par zone, Formidable Oak comprise**.
  Emplacements (Pikipedia) :
  - Tropical Wilds : petit bassin près du Calcified Crushblat ; souche creuse vers le Medusal Slurker.
  - Garden of Hope : grand ensemble de plateformes-ascenseurs ; boîte de conserve renversée sur le chemin du Quaggled Mireclops.
  - Distant Tundra : mur de neige près du site d'atterrissage ; grotte nécessitant des Pikmin Ailés.
  - Twilight River : souche sur la rivière vers le Scornet Maestro ; corniche près des Orange Bulborbs.
  - Formidable Oak : Spotcaps derrière un mur renforcé ; monticule de terre près des Candypop Buds.
- Autres catégories (Exploration Notes, fichiers d'Olimar…) : nombre et mode d'obtention ❓

### Mode Mission (sans DLC) 📖
- **Defeat Bosses! : 6 missions**, une par boss, débloquée en battant ce boss en Histoire.
- **Collect Treasure! et Battle Enemies!** : les étapes de la 1re rangée se débloquent
  en obtenant au moins le bronze à l'étape précédente. D'après Pikipedia, l'étape 6
  (Silver Lake) et l'étape 11 (Thirsty Desert) sont arrivées avec les mises à jour 1.2.0 et 1.3.0,
  et les étapes 7–15 sont en DLC payant.
- Nombre exact de missions jouables sur notre version (v1 du disque, sans mise à jour ni DLC) : ❓
  (hypothèse : 5 + 5 + 6 = 16). Les étapes gratuites des mises à jour 1.2.0 à 1.4.0 ne sont **pas** disponibles.
- Médailles : aucune, bronze, argent, or, platine. Seuils propres à chaque étape.

### Idées d'items proposées pendant la Phase 0
- **Limite de Pikmin progressive** (idée de l'utilisateur, 2026-09-28) : commencer avec une limite basse sur le terrain
  (ex. 25) et l'augmenter jusqu'à 100 par items « Progressive Pikmin Limit ». Faisabilité ❓ : la limite de 100 n'est
  comparée à aucune des 6 lectures du compteur du terrain (`+0xEE8` du gestionnaire, fonctions `0x02931290`,
  `0x0318B48C`, `0x03267F80`) → probablement un paramètre de jeu chargé au démarrage. À chercher.

- **Référence : mod « Pikmin 3 No Limits »** (Gunnadahun, v0.91, [GameBanana 435272](https://gamebanana.com/mods/435272),
  signalé par l'utilisateur) : rend **Pikmin 3 Deluxe** (Switch) non linéaire (toutes les zones sauf la finale dès le départ,
  fruits, Oignons et boss dans n'importe quel ordre). Mod de **fichiers de jeu modifiés** (archive de 778 Mo, licence
  CC BY-NC-ND 4.0) → non réutilisable tel quel (autre plateforme, et on ne distribue pas de fichiers modifiés), mais
  **preuve qu'un Pikmin 3 non linéaire est jouable**. Pour nous, les déblocages passeraient par les flags en mémoire
  (bits d'Oignons `+0xA4`, flags d'histoire…) et des patches de code.

- **Objets « paramètre » nommés** (34 270 objets, signature `1036F770 00000005 1036F740`, noms en clair via pointeurs) :
  statistiques en direct de la partie, ex. `FruitsMax` = 66, `FruitsNum` = 9, `FruitsTypeNum` = 8, `FruitsMaxInArea` = 16,
  `FruitsNumInArea`, `PikminAllInGround`, `DeadPikminNumTotal`… et paramètres de transport par objet
  (`mCarryMin`, `mCarryMax`, `mIncPikmins`) → **données de logique** (Pikmin nécessaires pour porter un fruit).
  **Aucun paramètre « limite de Pikmin »** trouvé. Script : scratchpad `scan_params.py` (à promouvoir dans tools/ si utile).

### Limite de Pikmin (option A) : ✅ validée en jeu (2026-09-29, pack final + boîte aux lettres)
**1er test (pack `PikminLimit30`) : patch appliqué mais sans effet** (99/100 Pikmin sortis) → les deux sites ci-dessous
ne sont pas ceux du menu de l'Oignon. Analyse complète des compteurs :
- `0x02E79280(mgr, &équipe)` → `mgr[+0xEE8 + (équipe+1)*4]` = **Pikmin sur le terrain** (tableau [total, équipe 0, équipe 1]).
- `0x02E79240(mgr, &équipe)` → terrain + `mgr[+0xEF4 + …]` = **terrain + pousses** (ce que compte la limite).
- **`0x02795378` = « terrain plein ? »** : total terrain + pousses (`0x02795308`), puis **`0x027953A4 : cmpwi r3, 100`**
  (mode ≠ 3) ou **`0x027953C0 : cmpwi r3, 50`** (mode 3 = **Bingo Battle**). **9 appelants** dans le code de l'Oignon
  (`0x0279F700`–`0x027AB48C`). → **c'est le point à patcher** (à confirmer en jeu).
- Mode `[0x103E4488]+0x44` : 0 = Histoire, 3 = Bingo (1–2 = Mission ?).
- **Pack final V1** (`worlds/pikmin3/graphic_pack/Pikmin3_Archipelago`, 2026-09-28) : les 3 sites lisent la limite dans la
  boîte aux lettres (`+0x10`, écrite par le client) : `0x027953A4` et `0x02853BE8` → `bla _apLimitCompare`
  (`cmpw r3, limite`), `0x02CD19A0` → `bla _apLimitLoadR30` (`r30 = limite`). Vérifié dans le désassemblage : les deux
  premières fonctions sauvegardent LR en prologue et le restaurent depuis la pile, r12 n'est plus lu après la comparaison ;
  la troisième (`0x02CD0B50`, énorme) appelle d'autres fonctions (LR sur la pile) et seul r30 est modifié.
  Sans client, la limite reste 100.
- **Test en jeu 2026-09-29 (jour 11) ✅** : limite 30 écrite avec `tools/mailbox_ctl.py` → sortie de l'Oignon bloquée à
  **30** sur le terrain ; limite passée à 40 **pendant la partie** → bloquée à **40**. Relevé : `mgr+0xEE8` (terrain).
  Reste à observer : comportement des graines quand le terrain est plein (elles doivent rester dans l'Oignon).

Anciens candidats (secondaires) :
Croisement « fonctions qui chargent le gestionnaire des Pikmin `[0x103E288C]` » × « constante 100 » :
- **`0x02853BA8`** = « limite atteinte ? » : `bl 0x02E79280` (nombre de Pikmin), puis, sauf si le mode
  (`[0x103E4488]+0x44`) vaut 3, **`0x02853BE8 : cmpwi r3, 100`** → renvoie 1 si ≥ 100. Seul appelant : `0x028546EC`
  (fonction `0x0285459C`, éjection des graines par l'Oignon ?).
- **`0x02CD19A0 : li r30, 100`** (ou `li r30, 50` dans un autre cas) puis `r30 = 100 − bl 0x02E79240` borné →
  **places disponibles** (menu de l'Oignon ?).
- Écartés : `0x02E2E538` (taille d'allocation), `0x03196640` (initialisation de paramètres).
- Pack de test : [tools/graphic_packs/P3AP_Phase0_PikminLimit30](../../tools/graphic_packs/P3AP_Phase0_PikminLimit30)
  (limite 100 → 30 aux deux endroits). Si concluant : patch final = lire la limite dans la boîte aux lettres (code cave).

### À vérifier en jeu ❓
- Pellet Posies : nombre, repousse ou non.
- Ennemis : réapparition, définition d'un check de cadavre.
- Inventaire : ✅ Ultra-Spicy Spray = compteur `+0x598`. **Bomb Rock : pas de compteur** (jour 12, 2026-09-30,
  21:51:10) : un Pikmin ramasse la bombe dans un monticule (scène d'introduction, drapeau `0x34A4FE29` `0x3F` → `0x7F`)
  et devient un type à part dans le sélecteur d'équipe → item « Bomb Rock » hors V1. La Mine existe-t-elle en Histoire ?
- Fin du jus : que propose exactement le jeu (reprise à un jour précédent ?).
- KO d'un capitaine : conséquence exacte (pour le death link).
- Dangers existants réutilisables comme pièges.

---

## 0.C Mémoire

Voir [version_info.md](version_info.md#mémoire-premiers-constats). Adresses de jeu : aucune pour l'instant.

Notation : `[X] + 0xN` = lire le pointeur 32 bits à l'adresse fixe X, puis ajouter N.
Deux pointeurs fixes (données du RPX) mènent au même objet d'état :
`[0x103E448C]` (= `0x34A4D75C` le 2026-09-27) et `[0x103E4488]` (= `0x34A4D728`, soit 0x34 de moins).

| Donnée | Adresse Wii U / chaîne de pointeurs | Type | Stable après zone / jour / rechargement / redémarrage | Statut |
|---|---|---|---|---|
| Pikmin Rouges dans l'Oignon | `[0x103E448C] + 0xF0` (vu à `0x34A4D84C`) | u32 | Suivie 21 → 7 → 21 → 0 → 30 ; bilan jour 2 : 30 dans l'Oignon + 10 enterrés = 40 Rouges | ✅ trouvée |
| Pikmin Rocs dans l'Oignon | `+0x120` / `+0x124` : [19, 3] au bilan → [3, 0] après en avoir sorti 19 (menu : 3 dans l'Oignon) | u32 | Tableau [type][maturité] ; pas de 12 octets (Roc = index 4) ou 16 (index 3) | ✅ Roc ; 🔶 disposition des autres types |
| Inconnus | `+0xC4` : 1 → 3 ; `+0xC8` : 0 → 2 → 37 → 45 (pas le nombre de capitaines) | u32 | | ❓ |
| Oignon Rouge après la nuit du jour 3 | `[30, 0, 10]` : les 10 Rouges arrachés le matin rangés à `+0xF8` | u32 | Ordre des stades de maturité à confirmer | 🔶 |
| Pikmin enterrés (pousses) | Non trouvés. **Proposition : ne pas les compter** dans la population tant qu'ils ne sont pas arrachés | | | décision à valider |
| **Jour courant** | `[0x103E448C] + 0x48` (vu à `0x34A4D7A4`) | u32 | 2 → 3 dès la fin de la journée (avant le bilan) | ✅ trouvé |
| Consommation de jus | Bilan jour 2 : 3.0 → 2.0 ; jour 3 : 2.0 + 1.5 (citron) − 1 = 2.5 → **1 bouteille par nuit** (2 capitaines). Le bilan n'affiche que les bouteilles pleines (×2 pour 2.5) | | | ✅ |
| **Jus** | `[0x103E448C] + 0x50` (vu à `0x34A4D7AC`) | f32 (bouteilles) | 2.0 → 3.0 après la fraise (Sunseed Berry, +1) | ✅ trouvé |
| **Nombre de fruits pressés** | `[0x103E448C] + 0x54` | u32 | 0 → 1 (fraise) → 2 (citron, pressé le soir) | ✅ trouvé |
| **Flags des fruits pressés** | **Corrigé le 2026-09-30** : champ de bits **`[0x103E448C] + 0x5C` à `+0x83`** (40 octets, 320 bits = sans doute 5 blocs de 64 bits, un par zone). Numéro de bit = (octet − `0x5C`) × 8 + bit (bit 0 = 0x01). Le **Pocked Airhead** (jour 12, +2.5) a allumé `+0x66` bit 7 (n° 87) : le client qui lisait depuis `+0x70` comptait 14 au lieu du « ×15 » du bilan. Vérifié hors jeu sur les sauvegardes `single2.sav`…`single13.sav` (début = objet d'état, **octet 0 du fichier = `état+0x40`**, identique au moins jusqu'à `+0xA4` ; plus loin la disposition diffère) : nombre de bits = fruits du bilan à chaque jour, `+0x84`–`+0x9F` toujours à 0 | bits | Posé au **pressage** | ✅ |
| Correspondance bit ↔ fruit (au fil du jeu) | Voir `worlds/pikmin3/data/fruits.py` (`OBSERVED_FRUIT_BITS`, numéros depuis `+0x5C`) : 160–161 fraises, 170 citron, 171 Zest Bomb, 176 fruit du boss du jour 7, 87 Pocked Airhead, 258–279 fruits des jours 8–11 | | | 🔶 à compléter |
| Journal des fruits pressés (hypothèse) | Liste d'entrées `06 00 00 XX` qui s'allonge d'une entrée par fruit pressé : `0x34A4DDD0` (jour 7, XX = `0x15`), puis `0x34A4DDD4`… `0x34A4DDE0` (jour 9 : `0x08`, ?, `0x03`, `0x1F`) → XX = **numéro de type du fruit** ? | | | 🔶 |
| **Fruit en plusieurs morceaux** | Jour 9, 21:01:14 : **1er morceau d'un raisin** (Juicy Gaggle ?, ramassé à l'endroit où Charlie disparaît, Distant Tundra) → compteur de types 7 → 8, **aucun bit de fruit** ; changements `+0x623` (→ `0x11`), `+0x734` (→ `0x40`), `+0x73C`–`+0x747` = suivi probable des morceaux. Le bit du fruit s'allumera sans doute au dernier morceau | | À vérifier quand tous les morceaux seront ramenés | 🔶 décision AP : 1 check par morceau ou par fruit complet |
| Moment du pressage | **Tous les fruits ramenés sont pressés à la fin de la journée** (sauf la toute première fraise du tutoriel). Séquence jour 7 : 3.0 → 4.0 → 5.0 → 5.5 (+2.5 par bouteilles entières puis le reste), puis −1 la nuit. Si le jus avait une fraction (2.5), il est d'abord arrondi à l'entier inférieur | | | ✅ |
| Fruit en attente de pressage | octet `+0x19C` : 0 → 1 au ramassage du citron → 0 après pressage | u8 (compteur ?) | | 🔶 |
| Octets déjà non nuls (inconnus) | `+0xA4` = 0x08, `+0xB0` = 1, `+0xC4` = 1 | | Présents avant la fraise | ❓ (Oignons ? zones ?) |
| Valeurs voisines inconnues | `+0x4C` = 31 → 41 → 49 (augmente dans la journée, pas en lien direct avec la population) ; `+0x58` = 8 ; objet au vtable présumé `0x1033FC38` à `+0x44` | u32 | | ❓ |
| Pikmin dans l'équipe (HUD) | `0x34E93CEC`, `0x34E93CF0`, `0x34E97E4C`, `0x34E9CE5C` (objets d'interface) | u32 | Suivent le changement de capitaine | ✅ inutile pour AP |
| **Pikmin sur le terrain** | **`[0x103E288C] + 0xEE8`** (objet recréé chaque jour : `0x3EC83FF0` au jour 2, `0x3EC7BFF0` au jour 3) | u32 | 54 → 62 (jour 2) ; 29 au jour 3 via le même pointeur | ✅ trouvé |
| Pikmin dans les équipes (tous capitaines ?) | `[0x103E288C] + 0xED8` | u32 | 39 (jour 2, Alph) ; 29 = 10 + 19 (jour 3, Alph + Brittany) | 🔶 |
| (écarté) | `0x3EC845F8` : tableau figé `[34, 4, 17, 0, 0, 13, 0, 6, 6, 0]` = `[0x103E288C] + 0x608` de la veille, données d'un ancien bloc | | | ❌ |
| **Population** | Somme des Oignons + terrain : 30 + 3 + 29 = **62** = bilan (40 Rouges + 22 Rocs) | | Jour 3 | ✅ calcul validé |
| Pikmin sur le terrain (HUD) | `0x3B7C7464` / `0x3B7C7468` (objet d'interface, = 54) | u32 | | ✅ secours possible |
| **Oignons / types découverts (bits)** | octet `[0x103E448C] + 0xA4` : `0x08` (départ) → `0x88` (Rocs, jour 2) → **`0xA8`** (Oignon jaune trouvé et levé, jour 8, Distant Tundra) | u8 bitfield | Journal : seuls 2 octets changent à la découverte | ✅ `0x80` = Roc, `0x20` = Jaune ; `0x08` = Rouge probable |
| **Notes (tutoriels / fichiers)** — probablement un **gestionnaire de flags général** | Objet `0x34A4FF18` (vtable `0x10345EE8`) suivi de **jusqu'à 7 ensembles de 256 bits** (8 mots chacun, `0x34A4FF1C`–`0x34A4FFFB`) puis un petit compteur (`0x34A4FFFC`, octet `0x34A4FFFF`) : **A** `0x34A4FF1C` (= `0x00FEA49F`…), **B** `0x34A4FF3C` (= `0x20080002`…), **C** `0x34A4FF5C` (= `0x011B87EF`…), **D** `0x34A4FF7C` (1ʳᵉ note d'Olimar : octet `0x34A4FF7F` = `0x20`, jour 9, 20:45:17). Copie quasi identique après `0x34A50034` (sauvegarde précédente ?). Peut contenir aussi les **flags d'histoire** (à vérifier) | bitsets | Jour 8 : A bits 20, 22 (document jaune = 2 tutoriels), A bit 21 (lecture au KopPad 19:29:24 du document « vidéo » ramassé à 19:27:23, qui avait allumé C bit 8), A bit 23 (19:30:27), **B bit 19** (tutoriel, 19:35:45) | ✅ emplacement ; 🔶 sens de A/B/C (obtenu, lu, catégorie ?) |
| Indicateur « nouvelle note » | octet `0x34A4FFFF` : passe à 2 ou 6 au ramassage d'un document (19:27:23), revient à 0 à la lecture | u8 | | 🔶 |
| **Étapes d'histoire (jour 11, 2026-09-29)** | Sauvetage de **Charlie** (scène « Look at the Wii U GamePad », 18:43:16) : **`0x34A4FFBF` `0x01` → `0x03`** (bit 0 allumé au Data Glutton, bit 1 à Charlie) et `0x34A4FFFF` `0x06` → `0x05` (compteur qui descend). Boss vaincu (18:41:41) : `0x34A4FDC9` `0x23` → `0x63`, état `+0x8E2` `0xC0` → `0xD0`. Début de la fin de journée : `0x34A4FD33` `0x00` → `0x08`. **Aucune zone débloquée** par Charlie (objectif suivant : chercher Olimar, boss « ver » dans la zone de départ d'Alph) → `0x34A4FFBF` = étapes d'histoire, pas directement les zones | bits | Journal `docs/phase0/logs/state_journal_2026-09-29.log` | 🔶 option B : capter le prochain vrai déblocage de zone |
| **Ordre de la fin de journée (jour 11 → 12)** | 18:47:35 le **jour passe à 12 dès le début** de la fin de journée ; 18:48:25–18:48:40 pressage (jus 9 → 12, bit du fruit `+0x7E` `0xC0` → `0xD0`, sortes 10 → 11) ; 18:48:51 bouteille de la nuit (12 → 11) ; ~18:49:57 sauvegarde (`gen11.sav`, `single12.sav`) et arrivée sur la planète (pointeur des Pikmin nul un instant). Conséquence client : l'index « début du jour » est noté avant la sauvegarde → en cas de rechargement, les items reçus pendant le bilan seraient redonnés en double (sens sans perte) | | Journal + relevé du 2026-09-29 | ✅ |
| Compteur lié aux notes ? | octet `0x34A4FF5E` (dans `0x34A4FF5C` = `0x011B87EF`) : `0x86` → `0x87` au ramassage ; `0x34A50000` : 21 → 23 | | | ❓ |
| Statistiques d'ennemis (hypothèse) | Paires de compteurs à 0x1C d'écart dans l'objet d'état : `+0x213`/`+0x22F`, `+0x3E7`/`+0x403`, `+0x54F`/`+0x56B` (0 → 1), `+0x573`/`+0x58F` (3 → 4) pendant un combat (jour 8, 19:31:27) ; `+0x8E0` : `0x07` → `0x0F` pendant un autre combat (19:33:26) | u8/u32 | Captures : combats en cours | 🔶 piste pour « cadavres d'ennemis » |
| **Objets importants / améliorations (bits)** | mot `[0x103E448C] + 0x58` (octet `+0x5B`) : `0x08` (dès le jour 2) → `0x0A` (entre jours 3 et 7 : **Data Glutton** probable) → `0x1A` (jour 9, 20:56:36 : **Anti-Electrifier**) → **`0x9A`** (jour 10, 21:15:35 : **Dodge Whistle**) → **`0xDA`** (jour 13, 2026-10-01 19:48:53 : **Metal Suit Z**, annoncé par l'utilisateur) → **`0xDB`** (jour 23, 2026-10-03 11:26:41 : **Louie** récupéré à Garden of Hope) | u32 bitfield | Journal : seul changement de l'objet d'état à chaque fois | ✅ Louie = `0x01`, Anti-Electrifier = `0x10`, Metal Suit Z = `0x40`, Dodge Whistle = `0x80` ; 🔶 `0x02`, `0x08` |
| **Sprays (Ultra-Spicy Nectar)** | mot `[0x103E448C] + 0x598` : 0 → 1 à la fabrication (jour 10, 21:20:30) | u32 | | ✅ |
| **Baies ultra-épicées** | mot `[0x103E448C] + 0x59C` : 1 → 8 au fil des baies, **remis à 0** quand le spray est fabriqué (8 baies = 1 spray) | u32 | | ✅ |
| **Objet des flags d'histoire (hypothèse)** | Objet à `0x34A4FD64` (vtable `0x1033B578`) suivi d'ensembles de 256 bits (pas de 0x20) jusqu'à ~`0x34A4FEE7` : mots non nuls vus à `0x34A4FD88`, `0x34A4FDA8`, `0x34A4FDC8`, `0x34A4FE28`/`FE2C`/`FE34`, `0x34A4FEC8`/`FECC` | bitsets | **Candidats « Distant Tundra débloquée »** (changés entre jour 3 et ramassage du Data Glutton) : `0x34A4FE37` (`0x02`→`0x0B`), `0x34A4FECB` (`0x00`→`0x10`), `0x34A4FFBF` (`0x00`→`0x01`, objet des notes, ensemble F). À l'arrivée dans la zone (jour 8) : `0x34A4FE2A` bit 4, `0x34A4FDCB` bit 7 | 🔶 option B : à tester |
| Flags d'événements (hors objet d'état) | Octets qui gagnent des bits aux événements d'histoire : `0x34A4FE29` (`0x01`→`0x05`→`0x07`→`0x0F`), `0x34A4FE2A` (`0x12`→`0x92`), `0x34A4FECB` (`0x10`→`0x12`→`0x52`), `0x34A4FECC` (`0x0E`→`0x0F`), `0x34A4FDC8`… | bits | **Piste pour l'option B** (déblocage des zones) : guetter le changement au prochain déblocage de zone | 🔶 |
| Fiche d'objet (ensemble de notes C ?) | `0x34A4FF5D` : `0x1B` → `0x5B` 24 s après l'Anti-Electrifier (+ badge `0x34A4FFFF` = 2) | bit | | 🔶 ensemble C = objets/trésors ? |
| Indicateur Oignon jaune (2ᵉ octet) | octet `[0x103E448C] + 0xBB` : `0x00` → **`0x08`** au même moment | u8 | Rôle exact ❓ (Oignon présent dans la zone ? levé ?) | 🔶 |
| Nombre de types (hypothèse) | `[0x103E448C] + 0xC0` : 0 → 2 à l'obtention des Roc | u32 | | 🔶 |
| Nombre total de Pikmin | **N'existe pas en mémoire** : aucune adresse n'a suivi 25 → 40. À calculer : Oignons + terrain | | | ✅ conclu |
| Flags des fruits | Voir « Flag de fruit (hypothèse) » ci-dessus | | | 🔶 |
| Flags des Oignons | TODO | | | ❓ |
| Mode courant (menu / Histoire / Mission / chargement) | TODO | | | ❓ |
| Zone courante | TODO | | | ❓ |
| Objets importants, Dodge Whistle, Data Files | TODO | | | ❓ |
| Bombes, sprays | TODO | | | ❓ |
| Points de vie des capitaines | TODO | | | ❓ |
| Résultats des missions | TODO | | | ❓ |
| Octets libres dans la sauvegarde | TODO | | | ❓ |

### Test de redémarrage (jour 4) ✅
Après fermeture complète de Cemu et rechargement de la sauvegarde (nouvelle base `0x239F4560000`) :
- `[0x103E448C]` = `0x34A4D75C` (même adresse qu'avant) : jour 4, jus 2.5, 2 fruits, bits `01 04`, Oignons identiques.
- `[0x103E288C]` = `0x3EC7BFF0` une fois les Pikmin sortis : équipes 15 / terrain 15 (8 Rouges + 7 Rocs), population 62.
- ⚠️ Pendant l'atterrissage, `[0x103E288C]` pointe provisoirement vers un autre objet (`0x3FE5F81C`, valeurs à 0) :
  le client devra valider l'état avant de lire (mode de jeu, valeurs plausibles).
- L'octet `+0x19C` vaut 1 après chargement sans fruit en attente → ce n'est pas « fruit en attente » (❓).
- Le jeu sort d'abord les Pikmin les plus mûrs → ordre des stades [feuille, bouton, fleur] probable.

### Fichiers de sauvegarde (`mlc01\usr\save\00050000\1012be00\user\80000001\`)
Copie de sécurité : `backups\save_1012be00_2026-09-27_2224` (avant le test d'écriture du jus).

| Fichier | Taille | Hypothèse |
|---|---|---|
| `single2.sav`, `single3.sav`, `single4.sav` | 4 995 o | **Une sauvegarde par jour** (reprise à un jour précédent). Petite : probablement l'objet d'état |
| `gen0.sav` … `gen3.sav` | 131 080 o | Données générales (rotation ?) |
| `radar0.sav` … `radar2.sav` | 590 344 o | Cartes / radar |
| `config.sav`, `password.sav`, `photo.sav`, `playreport.sav` | | Options, photos, statistiques |

À étudier plus tard : octets libres pour stocker l'index des objets AP reçus et l'identifiant de la seed.

## 0.D Patches
Pack de test : [tools/graphic_packs/P3AP_Phase0_Test](../../tools/graphic_packs/P3AP_Phase0_Test)
(copié dans `%APPDATA%\Cemu\graphicPacks\P3AP_Phase0_Test`). Il ne modifie aucun code :
il réserve une code cave de 0x40 octets signée `P3AP` `MBOX`.

| Test | Résultat |
|---|---|
| `moduleMatches = 0x838BE11A` accepté | ✅ log : `Applying patch group 'P3AP_Phase0_EUR_v1' (Codecave: 01800000-01800040)` |
| Boîte aux lettres retrouvée par le client | ✅ à **`0x01800000`** (début de la zone des code caves, adresse donnée par le log). Si d'autres packs avec code cave sont actifs, elle est plus loin : le client V1 cherche la signature dans les 64 Kio suivants |
| Écriture / relecture par le client | ✅ 12345 écrit à `+0x0C`, relu 1,5 s plus tard, remis à 0 |
| Routine « fruit pressé → jus + flag » | 🔶 en cours (voir « Analyse du code » ci-dessous) |
| Fonction appelée à chaque image (lecture de la boîte aux lettres par le jeu) | ❓ |
| Blocage lock-on / charge / esquive | ❓ |
| Apparition d'ennemi / objet (pièges) | ❓ recherche longue |

### Analyse du code (statique)
- Code copié depuis la mémoire : `0x02000000`–`0x0EE00000` (le RPX + d'autres modules). Désassemblage avec capstone
  (les instructions « paired singles » de l'Espresso sont mal décodées, ex. `psq_st` affiché `vmhaddshs`).
- **Le pointeur global réellement utilisé par le code est `0x103E4488`** (889 `lwz …, 0x4488(r)`), et non `0x103E448C` (3 accès).
  Il pointe vers `0x34A4D728`. Vus depuis cette base : jour `+0x7C`, jus `+0x84`, fruits `+0x88`, bits fruits `+0xA4`,
  Oignon Rouge `+0x124`, sous-objet d'état (vtable `0x1033FC38`) à `+0x78`.
- Presque aucun accès direct à ces champs juste après le chargement du pointeur → indirection supplémentaire
  (méthodes du sous-objet ?). Fausses pistes écartées : `0x02F0AEA0` (animation), `0x031C2924` (rectangle).
- `r2` (SDA2) = `0x10008000` pour tous les threads ; `r13` non renseigné dans les contextes.
- Suite : analyse dynamique avec le stub GDB de Cemu (points d'arrêt en écriture) → [tools/gdb_watch.py](../../tools/gdb_watch.py).

### Analyse du code (dynamique, stub GDB de Cemu)
Particularités du stub constatées (Cemu 2.6) :
- **Conflit de port** : Razer Synapse (`RzSDKServer`) écoute sur `127.0.0.1:1337`, Cemu sur `0.0.0.0:1337` → se connecter à **`127.0.0.2`**.
- **`c` ne relance que le thread par défaut** (le jeu reste figé) → utiliser **`vCont;c`**.
- **Une seule surveillance mémoire** à la fois (`Z2` suivant → `E01`).
- **Aucune reconnexion possible** pendant une même partie : après déconnexion, le stub reste bloqué (`CloseWait`).
  → une seule connexion par lancement : [tools/gdb_session.py](../../tools/gdb_session.py) (session persistante)
  pilotée par [tools/gdb_ctl.py](../../tools/gdb_ctl.py).
- **PC imprécis** sur les arrêts mémoire (défaut connu) : tombe sur des têtes de boucle sans rapport. Le LR est plus parlant ;
  la session remonte aussi la pile (LR sauvegardés).
- ⚠️ **Plantage de Cemu** (2026-09-28, 18:21) au premier arrêt quand la session lisait pile et registre flottant **via le stub**
  (lecture à une adresse invalide probable). Correctif : mémoire lue directement dans le processus (memory_probe),
  stub réservé aux registres entiers et aux points d'arrêt ; surveillance posée seulement après le chargement de la sauvegarde.

- ⚠️ **Les surveillances mémoire de Cemu sont inutilisables pour trouver l'écrivain** : l'arrêt est traité en différé,
  PC **et pile** appartiennent au thread qui tourne à ce moment-là (ex. système d'animation `FLVI`/`FLVC` de l'interface).
  → utiliser des **points d'arrêt d'exécution** (précis) sur des fonctions candidates.
- ⚠️ **Registres lus sur le mauvais thread** : `p` lit le thread « général » (sélectionné par `Hg`), pas celui de l'arrêt.
  Tous les PC/LR/piles relevés jusqu'au 2026-09-28 19:16 venaient donc d'un autre thread (d'où la pile « en attente »
  `0x0309AC88`…). Correctif : `Hg<thread de l'arrêt>` avant de lire les registres (gdb_session.py). Le PC est `srr0`
  du contexte du thread, donc juste une fois le bon thread sélectionné (à vérifier).

### Fonctions du jus (analyse statique, 2026-09-28) ✅
Classe de l'objet d'état (`[0x103E4488]` = `0x34A4D728`), méthodes vers `0x03011xxx`–`0x03013xxx` :
- `+0x44` = **mode de jeu** (0 = Histoire ; 1–2 = Mission/Bingo ? → données à `+0x2E20`). Toutes les méthodes testent ce mode.
- `+0x48` = **sous-objet Histoire** (`0x34A4D770`) ; vu de lui : jus `+0x3C`, jour `+0x34`, `+0x40` = ex-« inconnu 0x4C ».

| Adresse | Rôle |
|---|---|
| `0x03012A9C` | `GameData::getJuice()` → `+0x84` si mode 0 (30 appelants) |
| `0x03012ADC` | `GameData::addJuice(f1)` → saute vers `0x03008868` si mode 0 |
| `0x03012AFC` | `GameData::setJuice(f1)` → saute vers `0x03007FA8` si mode 0 |
| `0x03012C28` | `GameData::getFruitTypeCount()` → `+0x88` |
| **`0x03008868`** | `Story::addJuice(f1)` : `jus += f1`, appel `0x03173D2C`, plafonné par la constante `0x1033F388` |
| **`0x03007FA8`** | `Story::setJuice(f1)` : `jus = f1`, même traitement |
| `0x03008270` | copie complète de l'état Histoire (chargement de sauvegarde) |

Appelants : `addJuice` ← `0x02C5583C`, `0x02C55A4C`, `0x02DB6640` (×3) ; `setJuice` ← `0x02C5679C`, `0x02C57434` ;
`Story::setJuice` direct ← `0x030089E0`, `0x03008BA8` (méthodes internes : nuit ?). Les fonctions `0x02C55xxx`–`0x02C57xxx`
lisent aussi le jus → probablement la séquence de pressage. **À confirmer par points d'arrêt d'exécution.**

### Pressage des fruits : confirmé par points d'arrêt d'exécution (jour 8, 19:42) ✅
Module du pressoir `0x02C55xxx`–`0x02C57xxx`, piloté par la séquence de fin de journée `0x02DB6640`.

| Étape | Fonction | Appel exact | Effet |
|---|---|---|---|
| 1. Arrondi | `0x02C5679C` | `0x02C568FC` : `bl setJuice` (f1 = partie entière) ; stocke la fraction dans le pressoir `+0x574` | 4.5 → 4.0 |
| 2. Bouteilles | `0x02C55A4C` | `0x02C55A78` : `bl addJuice` avec f1 = `[0x102AC174]` = **1.0** | +1 par bouteille |
| 3. Reste | `0x02C5583C` | `0x02C55868` : `bl addJuice` avec f1 = pressoir `+0x574`, une fois (drapeau `+0x570`) | +0.5 |
| (autre) | `0x02C57434` | `0x02C576D4` : `bl setJuice` avec f1 = `[r30+4]` (valeur préparée) | nuit ou initialisation ? ❓ |

Plafond du jus : `[0x1033F388]` = **99.0**. Les points d'arrêt logiciels du stub ne se déclenchent **qu'une fois** (non réarmés).

**Patch de test (0.E n°4)** : [tools/graphic_packs/P3AP_Phase0_NoFruitJuice](../../tools/graphic_packs/P3AP_Phase0_NoFruitJuice)
→ `nop` sur `0x02C568FC`, `0x02C55A78`, `0x02C55868`. À valider en jeu.

Écritures du jus (`0x34A4D7AC`) observées par surveillance mémoire (journal : `logs/gdb_watch_fruit.log`) — PC/piles non fiables :

| Moment | Jus | PC rapporté | LR |
|---|---|---|---|
| Démarrage | 0 → 3.0 | `0x00E02234` (copie mémoire) | `0x031BE040` |
| Chargement de la sauvegarde | 3.0 → 2.5 | `0x00E02234` (copie mémoire) | `0x031BE040` |
| Pressage d'un fruit (+1) | 2.5 → 2.0 → 3.0 → 3.5 (3 écritures en ~18 s) | `0x02EE24A0`, `0x0309AC90`, `0x02FEF154` | —, `0x0309AC88` (retour d'un `bctrl` virtuel à `0x0309AC84`), `0x02FEF318` |
| Ensuite (fin de journée ?) | 3.5 → 2.5 | `0x031CFEF0` | `0x031CFF2C` |

## 0.E Tests décisifs
| Test | Statut |
|---|---|
| Trouver Cemu et la base mémoire sans dépendance externe | ✅ (`memory_probe.py info`, recoupé avec `log.txt`) |
| Lire et écrire la mémoire Wii U (big-endian) | ✅ (testé sur une zone vide, valeur remise à 0 ; `0x02000000` = `nop` / `blr` PowerPC) |
| Lire le jus en direct | ✅ `[0x103E448C] + 0x50` |
| Ajouter du jus, visible en jeu et conservé à la sauvegarde | ✅ pris en compte : 2.5 → 3.5 écrit au jour 4 ; bilan ×3 avant de boire, ×2 après ; 2.5 en mémoire au jour 5. ⚠️ Le HUD de la journée n'est pas rafraîchi (relu en début de journée) ; les bouteilles dessinées au bilan suivent une liste séparée (1 bouteille par fruit, cosmétique). Conservation après rechargement : ❓ |
| Détecter un fruit ramené | ✅ compteur `+0x54` et bits `+0x70…` (pressage) |
| Communication client ↔ graphic pack | ✅ boîte aux lettres à `0x01800000` |
| Patch supprimant le jus d'un fruit | ✅ **validé** (jour 9 → 10, 21:00–21:01) avec [P3AP_Phase0_NoFruitJuice](../../tools/graphic_packs/P3AP_Phase0_NoFruitJuice) : 4 fruits pressés, jus resté à 4.5 pendant tout le pressage, puis 4.5 → 3.5 (nuit) ; compteur de types 4 → 8 ; bits de fruits allumés pour 3 d'entre eux (`+0x7D` `0x08`, `+0x7E` `0x40`, `+0x7D` `0x40`). L'animation remplit des bouteilles (cosmétique) |

---

## Sources
- Pikipedia : [Pikmin 3](https://www.pikminwiki.com/Pikmin_3), [Fruit](https://www.pikminwiki.com/Fruit),
  [Dodge](https://www.pikminwiki.com/Dodge), [Secret File](https://www.pikminwiki.com/Secret_File),
  [Mission Mode](https://www.pikminwiki.com/Mission_Mode)
- Fandom : [Data Glutton](https://pikmin.fandom.com/wiki/Data_Glutton), [Folded Data Glutton](https://pikmin.fandom.com/wiki/Folded_Data_Glutton)
- Game8 : [Différences Wii U / Deluxe](https://game8.co/games/Pikmin3Deluxe/archives/305646)
- [Pikmin Technical Knowledge Base](https://pikmintkb.com/) (formats de fichiers, pour plus tard)
