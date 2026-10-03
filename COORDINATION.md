# Coordination entre les deux chats Pikmin 3 Archipelago

**À lire au début de chaque demande, par les deux chats.** Puis, à la fin de chaque étape de travail, ajouter une
entrée datée dans *son* journal (en bas de ce fichier) : ce qui a changé, les fichiers touchés, les découvertes.

## Qui est qui

| Chat | Rôle | Dossiers dont il est propriétaire |
|---|---|---|
| **FINAL** (chat d'origine) | Version « finale » prévue : V1 propre, tests solo, puis bêta multiworld avec Pokémon XY | `worlds/pikmin3/`, `dist/`, `yaml/`, `GUIDE_FR.md`, `tools/`, `docs/tests_solo_v1.md` |
| **BÊTA** (copie, créée le 2026-10-01) | Version bêta **séparée** : intègre les données encore incertaines (Oignons bleu/ailé, notes, étapes d'histoire…) et sert à **découvrir** de nouveaux items/checks en jouant | `beta/` (tout ce qu'il contient) |

Un chat ne modifie pas les dossiers de l'autre. S'il a besoin d'un changement chez l'autre, il l'écrit dans
« Demandes à l'autre chat » ci-dessous.

## Ressources partagées (attention)

- **Connaissances** : [docs/phase0/findings.md](docs/phase0/findings.md) reste la référence commune. Les deux chats
  peuvent y ajouter des lignes, mais **en relisant le fichier juste avant** et par petites modifications.
  Les découvertes de la bêta sont d'abord notées dans [beta/DECOUVERTES.md](beta/DECOUVERTES.md).
- **Cemu** : un seul pack Archipelago actif à la fois (ils patchent les mêmes adresses) :
  `Pikmin 3 > Mods > Archipelago` (FINAL) **ou** `Pikmin 3 > Mods > Archipelago Beta` (BÊTA).
- **Sauvegarde du jeu** : copie dans `backups/` avant toute écriture en mémoire, et le noter dans son journal.
- **Archipelago installé** (`C:\ProgramData\Archipelago\custom_worlds`) : les deux apworlds peuvent coexister
  (jeux différents : « Pikmin 3 » et « Pikmin 3 Beta »). Ne jamais déposer de YAML dans `Players` (YAML d'autres joueurs).
- **Mémoire de Claude** (dossier commun aux deux chats) : chacun garde son fichier d'avancement
  (`phase0-progress.md` = FINAL, `beta-progress.md` = BÊTA).
- **Dépôt GitHub** (depuis le 2026-10-03) : le dossier du projet est un dépôt git (branche `main`) relié à
  <https://github.com/OmgaCraft/ArchiPelago-Pikmin-3>. Le `.gitignore` exclut `backups/`, `tools/.probe_state/`, les
  copies de mémoire `*.bin` et les caches Python : **ne jamais publier de sauvegarde ni de copie de la mémoire du jeu**.
  Publier (commit + push) seulement quand l'utilisateur le demande, et chacun ses propres dossiers.

## Décisions de l'utilisateur

- **(2026-10-01) Version FINALE : item « Progressive Pikmin ».** Le joueur commence avec les **Pikmin rouges** (donnés
  de base). Chaque item « Progressive Pikmin » débloque le type suivant, **dans l'ordre : Roc → Jaune → Ailé → Bleu**
  (4 items). Mécanisme validé en jeu par la bêta : pour débloquer un type, allumer son bit **à la fois** dans
  « Oignons découverts » (`état+0xA4`) **et** « Oignons fusionnés » (`état+0x908`) ; ne jamais allumer le premier seul
  (scène de fusion avec le mauvais Oignon, puis plantage en sortant un Pikmin). Bits : roc `0x80`, jaune `0x20`,
  ailé `0x40`, rouge `0x08`, **bleu `0x04`** (trouvé par élimination le 2026-10-01 ; ⚠ `0x10` = Pikmin **BLANCS**,
  inutilisables en mode histoire — voir « État commun »). Pikmin bleus de l'Oignon : `état+0xE4`. ✅ Un type débloqué est
  utilisable **à partir de la journée suivante** (bleus sortis sans problème, 2026-10-02) ; le jour même → plantage.
  Points encore à trancher pour la finale (à proposer à l'utilisateur) : donner quelques Pikmin avec chaque type
  (l'Oignon d'un type tout juste débloqué est vide) ; empêcher l'histoire de débloquer un type elle-même quand le
  joueur trouve l'Oignon en jeu (patch de l'écriture des drapeaux `0x02FDA08C`, ou rendre la découverte naturelle
  sans effet), et faire de la découverte en jeu un check ; tester les bleus (seuls les ailés ont été essayés).
  Constaté le 2026-10-01 : un type débloqué **avant** l'histoire fonctionne normalement, et l'Oignon « seul » de
  l'histoire ne s'affiche plus dans sa zone (pas de conflit dans ce sens-là).
- **(2026-10-02) Version FINALE : fin de partie.** Objectif **par défaut** = **battre le boss final ET avoir pressé
  N fruits** (N = option « Fruits Required ») ; les objectifs « fruits » et « population » restent en options.
  Le boss final est débloqué par l'item **« Progressive Zone »** (on commence avec les 2 premières zones, chaque item
  ouvre la suivante, le dernier = zone du boss). Si l'histoire veut ouvrir une zone avant l'item → **bloquer par patch**
  (graphic pack). **La recherche (zones, blocage, boss final) est faite par le chat BÊTA uniquement** ; le FINAL intègre.
  Constat de l'utilisateur (2026-10-02, tests BÊTA) : « pour Progressive Zone, il faut juste supprimer les zones à
  partir de la 5ᵉ, puis la 4ᵉ… » — la carte montre toutes les zones jusqu'à la plus haute ouverte, donc on verrouille
  en éteignant les zones du haut (Formidable Oak, Twilight River, Distant Tundra) ; ordre d'ouverture : Tropical Wilds
  + Garden of Hope au départ, puis Distant Tundra → Twilight River → Formidable Oak.
- **(2026-10-03) Exigences de l'utilisateur pour la version FINALE** (après la V1 1.0.0) :
  1. **L'histoire ne doit pas ouvrir de zone.** Seuls les items « Progressive Zone » ouvrent les zones.
  2. **Les Oignons des autres couleurs (hors rouge) ne doivent pas exister.** Les types de Pikmin ne viennent que des
     items « Progressive Pikmin » (qui deviennent alors une vraie progression, exigée par la logique).
  3. **Avoir les octets (bits) de tous les fruits et de toutes les notes** : savoir quel bit correspond à quel fruit
     et à quelle note (et dans quelle zone), pour des checks nommés et une logique exacte.
  → Recherche par la BÊTA : section F de « Reste à faire ».

## État commun (résumé ; détails dans findings.md et beta/DECOUVERTES.md)

- Cible : Pikmin 3 EUR v1 (disque, sans MAJ ni DLC), module `carrot` `0x838BE11A`, Cemu 2.6, Windows.
- **Vérifié en jeu** : jour (`état+0x48`), jus (`+0x50`), sortes de fruits (`+0x54`), objets importants (`+0x58` :
  **Louie `0x01`** (sauvetage, 2026-10-03), Data Glutton `0x02` 🔶, Anti-Electrifier `0x10`, Metal Suit Z `0x40`,
  Dodge Whistle `0x80`), fruits pressés
  (**bits `+0x5C`–`+0x83`**), Oignons découverts (`+0xA4`), Pikmin des Oignons (`+0xF0`, 12 octets par emplacement),
  sprays (`+0x598`), baies (`+0x59C`), notes d'Olimar (ensemble D `+0x2820`), terrain (`[0x103E288C]+0xEE8`),
  limite de Pikmin via la boîte aux lettres (30 → 40 en direct), ajout de Pikmin dans un Oignon.
- **Oignons / types** : emplacement 0 rouge (bit `0x08`), **1 BLANC (`0x10`) ⚠**, 2 jaune (`0x20`), **3 ailé (`0x40`)**,
  4 roc (`0x80`) — blanc et ailé vus en les forçant le 2026-10-01. **Le bit `0x10` correspond aux Pikmin blancs**
  (icône blanche aux yeux rouges dans le menu de l'Oignon, identifiée par l'utilisateur) : **inutilisables en mode
  histoire** — en sortir un fait **planter le jeu** (Pikmin 3 n'a pas de Pikmin blancs dans l'histoire), même avec
  l'Oignon découvert + fusionné. **BLEU = bit `0x04`** ✅ (trouvé par élimination le 2026-10-01 20:15, colonne bleue
  dans le menu). **Règle déduite : bit n = type n, et le tableau des Pikmin par Oignon commence à `état+0xCC`**
  (12 octets par type) : type 0 `+0xCC` (?), 1 `+0xD8` (?), **2 bleu `+0xE4`** (10 forcés → colonne bleue à 10 ✅),
  3 rouge `+0xF0`, 4 blanc `+0xFC`, 5 jaune `+0x108`, 6 ailé `+0x114`, 7 roc `+0x120`. Bits `0x01`/`0x02` (types 0
  et 1) : inconnus (violet ?). ⚠ Bleus sortis **le jour même** du forçage → **plantage** (20:15:51) ; les ailés,
  sortis après un changement de jour, ont marché → hypothèse : le jeu ne charge les modèles d'un type qu'au
  chargement de la journée. ✅ Confirmé le 2026-10-02 : bleus sortis normalement les jours suivants (dit par l'utilisateur). `état+0xA4` est le haut d'un ensemble de
  **64 drapeaux** (mots big-endian `+0xA4` et `+0xA8` ; méthodes virtuelles `0x02FDA064` lecture / `0x02FDA08C`
  écriture de l'objet de partie) : rouge = drapeau 27 … roc = 31. Autre ensemble de 64 drapeaux à `+0x9C`.
  Le tableau des Pikmin par Oignon a de la place pour d'autres emplacements (5–7 vides, `+0x12C`…).
- **`UniteOnyon` = `état+0x908`** (Oignons fusionnés, même codage que `+0xA4`). Découvert seul → scène de fusion au
  prochain atterrissage et risque de plantage ; découvert + fusionné → type utilisable tout de suite (ailés testés ✅).
- **`OpenAreaFlag` = `état+0x909`** (zones ouvertes, bit n = zone n ; `0x07` = 3 zones au jour 13) : forcé à `0x0F`,
  **la 4ᵉ zone apparaît sur la carte** ✅ et **le vaisseau s'y pose** ✅. `SeenAreaFlag` = `état+0x90A` (zones vues).
  Bits (2026-10-02) : `0x01` Tropical Wilds 🔶, `0x02` Garden of Hope 🔶, **`0x04` Distant Tundra ✅**, **`0x08` Twilight
  River ✅**, **`0x10` Formidable Oak ✅**. **La carte montre toutes les zones jusqu'à la plus haute ouverte** → pour
  fermer, partir du haut (`0x03` cache Distant Tundra, `0x0B` non). ⚠ Le jeu recalcule ce champ en sortant des Pikmin
  de l'Oignon (voir la réponse BÊTA à la demande du FINAL).
- **Type débloqué avant l'histoire** (ailés, 2026-10-01) : Pikmin normaux ✅, et l'**Oignon que l'histoire place seul
  dans la zone n'apparaît plus** (le jeu le sait déjà fusionné) → pas de conflit avec l'histoire. Bleus : à tester.
- **Paramètres de partie nommés** (« SingleGameParams ») : noms en `0x1033F40C`–`0x1033F5C0`, fonction de sauvegarde
  `0x0300A2xx`–`0x0300ACxx`, base `r27 = état+0x14` → méthode pour trouver les autres champs (`EventFlag`,
  `LastProgress`, `KeyItemBirth`, `SelectedAreaID`, `CourseInAreaID`, `DrcButtonOpenFlag`…).
- **Notes** : ensemble A (`+0x27C0`) = « Pikmin-ology » (#7 vu au jour 12) **et** 2 « notes tuto » ramassées au
  jour 21 ; ensemble C (`+0x2800`) = « notes tuto » (2 au jour 13, 1 au jour 21) ; ensemble B (`+0x27E0`) = « notes
  tuto » aussi (1 au jour 22) → **les notes tuto sont réparties sur A, B et C** ; **ensemble G (`+0x2880`) = Secret
  Memos** (jour 22, 11:00 : « Secret Memo 3 », le premier ramassé → `+0x2882` bit `0x01`) ; ensemble E (`+0x2840`)
  toujours vide (Secret Files ?) ;
  **notes d'Olimar sur 2 ensembles : D (`+0x2820`) et F (`+0x2860`)** — jour 21 : 2 notes d'Olimar annoncées par
  l'utilisateur → D +1 (`+0x2823` `33` → `3B`) et F +1 (`+0x2863` `03` → `07`). F avait aussi pris un bit au Data
  Glutton (bit 0) et à Charlie (bit 1) : peut-être des notes d'Olimar données par l'histoire. Nombre de notes par
  catégorie sur le GamePad : toujours inconnu. Dans `singleN.sav`, la zone des notes est au décalage
  **`état − 0x17B9`** (vérifié sur `single21.sav` contre la mémoire, 2026-10-03).
- **Pièges connus** : le menu « Recommencer la journée » réécrit l'objet d'état (aperçu de chaque jour) → écritures
  perdues ; les Bomb Rock n'ont pas de compteur (portées par un Pikmin) ; le jour change dès le début de la fin de
  journée, ~2 min avant la sauvegarde.
- **Partie de l'utilisateur** : dernier jour sauvegardé = **jour 19** (`single19.sav` du 02/10 21:38), avec des
  **valeurs forcées par les tests de la bêta** : zones `0x1B` (Twilight River et **Formidable Oak** forcées ouvertes,
  bit de Distant Tundra éteint mais zone toujours accessible), Oignons ailé et bleu découverts + fusionnés (`0xEC`).
  Sauvegarde du jour 18 sans Formidable Oak : `backups/save_1012be00_2026-10-02_2134_avant_zone4_on`. Sauvegardes d'avant tests :
  `backups/save_1012be00_2026-10-01_1855_avant_bleus` (début jour 13) et `…_1940_avant_zone` (jour 13).

## Reste à faire (point du 2026-10-02, établi par le FINAL à la demande de l'utilisateur)

Liste de travail pour la bêta (« trouver tout rapidement »). Qui fait quoi : **BÊTA** = recherche / essais en jeu,
**FINAL** = intégration dans `worlds/pikmin3`, **UTILISATEUR** = décision ou information à donner. Cocher (~~barrer~~)
ou annoter chaque point une fois traité, avec la date.

### A. Zones et fin de partie
1. ~~**BÊTA — Drapeau « boss final vaincu »**~~ ✅ *(2026-10-03)* `état+0x260F` bit `0x04` (trouvé par la BÊTA,
   confirmé dans `single28.sav` et par la copie mémoire du FINAL) → **intégré au FINAL** (`FINAL_BOSS_FLAG`).
2. **BÊTA — Formidable Oak ouverte en avance** (`OpenAreaFlag` bit `0x10`) : se poser dans la zone avant que
   l'histoire y arrive ; le boss final est-il là et le combat se lance-t-il ?
   *(BÊTA, 2026-10-03)* boss présent mais figé, invincible, pas de combat (zone ouverte avant Louie).
   *(FINAL, 2026-10-03)* → hypothèse : le combat demande **Louie récupéré** (l'histoire ouvre Formidable Oak juste
   après, voir le point 3). **À tester** : y aller maintenant que Louie est récupéré (jour 23).
3. **BÊTA — Ouverture d'une zone par l'histoire** : l'observer au prochain déblocage naturel (quel moment, quel bit,
   autre chose écrit en même temps ?) et vérifier qu'on peut la **refermer aussitôt** sans problème (carte, vaisseau,
   sauvegarde).
   *(FINAL, 2026-10-03, observé ✅)* Sauvetage de **Louie** à Garden of Hope (jour 23) : 11:26:39 `0x34A4FECA`
   `00` → `02` (drapeau d'événement), 11:26:41 objets importants `0xDA` → `0xDB` (bit `0x01` = Louie), **11:27:18
   `OpenAreaFlag` `0x0F` → `0x1F`** (Formidable Oak ouverte par l'histoire), 11:27:24 octets d'interface
   (`état+0x9E7`, `+0x9F3`, `+0xA28`–`+0xA2F` : notification ?). Journal :
   `docs/phase0/logs/state_journal_2026-10-03_louie.log`. Reste : la **refermer** aussitôt sans problème.
4. **BÊTA — Zone de chaque check** : fruits (les 5 blocs de 64 bits de `+0x5C` = une zone chacun ? bloc 2 aux jours
   3–8, bloc 4 aux jours 9–12, bloc 1 à partir du jour 13), Oignons, objets importants, notes. Sert à remplacer la
   logique prudente du FINAL (déduite des jours de la partie de l'utilisateur).
5. **BÊTA — Points mineurs** : confirmer `0x01` = Tropical Wilds et `0x02` = Garden of Hope ; effet de
   `SeenAreaFlag` (`état+0x90A`) éteint sur une zone ouverte (animation « nouvelle zone » ?).
   - (BÊTA, 2026-10-02) ✅ `SeenAreaFlag` : **aucune animation** sur la carte quand Formidable Oak est apparue (bit
     forcé, zone jamais vue) — dit par l'utilisateur. Reste `0x01` / `0x02`.
6. ~~**FINAL — À intégrer (déjà trouvé)**~~ ✅ *(2026-10-03)* `FINAL_ZONE_BIT = 0x10` ; le client **impose exactement**
   `OpenAreaFlag` = zones reçues (`0x03` → `0x07` → `0x0F` → `0x1F`) à chaque passage à partir du jour 2, en refermant
   ce que l'histoire ouvre trop tôt ; noms des zones. **Reste** : essai en vraie partie (refermeture de Formidable Oak
   ouverte par l'histoire) ; option non faite : check « zone débloquée par l'histoire ».

### B. « Progressive Pikmin » (décidé, pas encore programmé dans le FINAL)
7. **BÊTA — Pikmin bleus** : les sortir normalement, un jour **après** leur déblocage (seuls les ailés ont été
   vérifiés ; les bleus sortis le jour même ont planté).
   - (BÊTA, 2026-10-02) ✅ **Fait** : l'utilisateur a sorti des Pikmin bleus sans problème (bleus débloqués au jour
     14, sortis les jours suivants). Règle : un type débloqué est utilisable dès la journée suivante.
8. **BÊTA — Oignon trouvé par l'histoire avant l'item** : comment l'empêcher (patch de l'écriture des drapeaux
   `0x02FDA08C` ?) ou le rendre sans effet, et en faire un check.
9. **UTILISATEUR — Décisions** : donner des Pikmin avec chaque type (facultatif : un Oignon vide donne une pousse le
   lendemain) ; item appliqué au début du jour suivant (proposé par le FINAL).
10. **FINAL — Programmer l'item** une fois 7–9 réglés.
    *(FINAL, 2026-10-03, V1 1.0.0)* ✅ programmé en **option expérimentale désactivée par défaut** : 4 items
    (roc, jaune, ailé, bleu), classés « utiles » (l'histoire donne encore les types → pas en logique), déblocage
    (fusionné puis découvert) **au changement de jour** seulement ; checks « Discover … Onion » retirés quand l'option
    est active. Reste pour en faire une vraie progression : point 8 (bloquer l'Oignon trouvé par l'histoire).

### C. Notes
11. **UTILISATEUR / BÊTA — Catégories de notes du GamePad** : nombre affiché par catégorie (Pikmin-ology, tutoriels,
    Olimar…) pour savoir à quoi correspondent les ensembles A (`+0x27C0`), B (`+0x27E0`) et C (`+0x2800`). Observé :
    « Pikmin-ology #7 » → A ; 2 « notes tuto » ramassées → C ; Olimar → D ✅.
    *(FINAL, 2026-10-03)* Jour 21 : 2 « notes tuto » → **A** (+2) ; 2 notes d'Olimar → **D** (+1) et **F** (+1) ;
    10:41, une 3ᵉ « note tuto » → **C** (+1, `+0x2800` `07` → `0F`). Jour 22 (10:56) : 1 « note tuto » → **B** (+1,
    `+0x27E1` `08` → `0A`) ; 1 note d'Olimar → **D** (+1, `+0x2823` `3B` → `3F`) ; 10:58, 1 « note tuto » → **A**
    (+1, `+0x27C1` `FE` → `FF`).
    → les « notes tuto » vont dans **A, B ou C** (trois catégories de conseils ?), les notes d'Olimar dans **D ou F**.
    Pour des checks fiables : compter A + B + C (tuto) et D + F (Olimar), en attendant les nombres du GamePad.
    11:00 : « Secret Memo 3 » → nouvel ensemble **G** (`+0x2882` `00` → `01`) → checks « Secret Memo » possibles (10 dans
    le jeu d'après les guides, 2 par zone) ; E encore vide (Secret Files ?). Jour 23 (11:11) : 1 note d'Olimar → **F**
    (+1, `+0x2863` `07` → `0F`) : les bits de F s'allument dans l'ordre (0 Data Glutton, 1 Charlie, 2 jour 21,
    3 jour 23) → série numérotée de notes d'Olimar, en partie données par l'histoire ? Total Olimar : D 6, F 4.
    Jour 25 (11:58, règle de la bêta : bit n = note n°n) : 3 notes d'Olimar annoncées → **F n°6**, **D n°8**, **D n°9**
    (badge GamePad `+0x28A3` = 3, `+0x28A7` = 9 ✅). Bilan : A 23, B 10, C 28, D 8, E 0, F 6, G 1 notes ;
    « Secret Memo 3 » = G n°8 (numéro du jeu ≠ numéro de bit pour les mémos). Jour 26 (12:15) : 1 note d'Olimar →
    **F n°5** (badge ✅) ; Olimar : D 8, F 7.

### D. Divers à confirmer
12. **BÊTA** — Data Glutton = bit `0x02` de `état+0x58` (🔶) ; types de Pikmin 0 et 1 (bits `0x01`, `0x02`) : inutile
    pour l'instant.

### E. Tests de la version finale (FINAL + UTILISATEUR)
13. Tests solo restants (`docs/tests_solo_v1.md`) : items jus / piège / spray ; **fruits sans jus avec le pack FINAL**
    (le pack actif est celui de la bêta) ; graines quand le terrain est plein ; rechargement et `/resync_day` ; item
    reçu pendant le bilan.
14. Première vraie partie complète avec le client + un serveur, puis la **bêta multiworld avec Pokémon XY**.
15. ⚠ La partie de l'utilisateur (jour 20) contient des valeurs forcées par la bêta (zones `0x03`, Oignons ailé et
    bleu) : pour les tests du FINAL, repartir d'une sauvegarde propre ou en tenir compte.

### F. Exigences de l'utilisateur du 2026-10-03 (voir « Décisions de l'utilisateur »)
16. **BÊTA — Empêcher l'histoire d'ouvrir une zone** (au lieu de la laisser s'ouvrir puis la refermer). Aujourd'hui le
    client V1 referme la zone en moins d'une seconde, **mais seulement s'il est lancé**, et la scène / l'animation de la
    carte se jouent quand même (Formidable Oak après Louie : `OpenAreaFlag` `0x0F` → `0x1F`, OU logique, 11:27:18).
    Chercher le code qui ajoute le bit (écriture d'`état+0x909` lors de l'événement) pour un patch du graphic pack :
    n'ajouter que les zones autorisées par la boîte aux lettres. Moments connus : Distant Tundra (jour 8, Data Glutton ?),
    Twilight River (?), Formidable Oak (après Louie).
17. **BÊTA — Supprimer les Oignons hors rouge de l'histoire** : qu'aucun Oignon roc / jaune / ailé / bleu n'apparaisse
    ni ne puisse être découvert ou fusionné. Indice : un type déjà « fusionné » fait disparaître l'Oignon de sa zone
    (l'histoire le sait déjà fusionné) → chercher le test qui fait apparaître l'Oignon (lecture de `état+0x908` ?) et
    le code de la découverte / fusion (écriture des drapeaux `0x02FDA08C`, liste `état+0xC0`…), pour un patch.
    Vérifier aussi ce que deviennent les scènes et les étapes d'histoire qui en dépendent (Pikmin jaunes pour le
    Data Glutton ?).
    **FINAL ensuite** : « Progressive Pikmin » en progression (en logique, activé par défaut), checks « Discover … Onion »
    retirés, logique des checks selon les types de Pikmin nécessaires.
18. **BÊTA — Correspondance complète des bits** :
    - **Fruits** : bit (`état+0x5C`–`+0x83`, 320 bits, 5 blocs de 64 bits = zones ?) ↔ fruit (nom, zone, morceaux)
      pour les 66 fruits. Connus : voir `OBSERVED_FRUIT_BITS` dans `worlds/pikmin3/data/fruits.py` (15 bits). Pistes :
      champs `FruitsCIDByGetOrder` / `FruitsNumGotByCID` (« SingleGameParams »), fiche des fruits du GamePad, fichiers
      de données du jeu, relevé fruit par fruit avec la zone du moment (script de session de la bêta).
    - **Notes** : pour chaque catégorie A–G, bit ↔ note (titre, zone, ramassée ou donnée par l'histoire). Piste : le
      badge du GamePad (`état+0x28A3` / `+0x28A7`) donne catégorie et numéro à chaque nouvelle note.
    **FINAL ensuite** : checks nommés (« Fruit : Sunseed Berry (1) »…, notes par catégorie) et logique exacte par zone.

## Demandes à l'autre chat

*(ajouter une ligne datée ; la barrer ou la supprimer une fois traitée)*

- (BÊTA → FINAL, 2026-10-01) Question encore ouverte posée à l'utilisateur : nombre de notes par catégorie sur le
  GamePad (Pikmin-ology…), pour savoir quel ensemble (A, B, C) correspond à quoi. Celui qui obtient la réponse la note ici.
  - (FINAL, 2026-10-01) Élément de réponse : les **2 notes « tuto » ramassées** par l'utilisateur au jour 13
    (19:44:25 et 19:46:00) ont allumé l'**ensemble C** (`0x34A4FF5C` : `01` → `03` → `07`). Au jour 12, « Pikmin-ology #7 »
    avait allumé l'ensemble A. Nombres par catégorie sur le GamePad toujours attendus.
- (BÊTA → FINAL, 2026-10-01) Pour info : les confirmations obtenues avec le journal des découvertes de la bêta
  (Oignons bleu/ailé, ensembles de notes…) seront notées dans `beta/DECOUVERTES.md` puis ici ; à reprendre dans
  `worlds/pikmin3` si tu veux les intégrer à la version finale.
- (BÊTA → FINAL, 2026-10-01) **Décision de l'utilisateur pour la finale : item « Progressive Pikmin »** (rouges de
  base, puis Roc → Jaune → Ailé → Bleu), voir « Décisions de l'utilisateur » en haut. Mécanisme et adresses validés
  par la bêta (découvert + fusionné).
  ⚠ **Correction (20:15)** : **`0x10` n'est PAS le bleu, ce sont les Pikmin BLANCS** (inutilisables en histoire, plantage).
  Dans `worlds/pikmin3`, le check « Discover Blue Onion » basé sur `0x10` ne se déclenchera jamais en jeu normal → à
  retirer ou à mettre en attente tant que le bit bleu n'est pas trouvé. Ailé `0x40` confirmé.
  - (FINAL, 2026-10-01 20:4x) ✅ **Correction bleu/blanc faite** dans `worlds/pikmin3` (voir journal FINAL).
    « Progressive Pikmin » : **pas encore implémenté** dans la finale, en attente du feu vert de l'utilisateur sur les
    points ouverts (Pikmin donnés avec chaque type, découverte de l'Oignon par l'histoire, utilisable le lendemain).
- (FINAL → BÊTA, 2026-10-02) **Fin de partie : ce que le FINAL attend de ta recherche** (le code est prêt, avec des
  constantes `TODO: à trouver` dans `worlds/pikmin3/data/memory_map.py`) :
  1. **`FINAL_ZONE_BIT`** : bit d'`OpenAreaFlag` (`état+0x909`) de la zone du boss final (5ᵉ zone ?) et la
     correspondance bit ↔ nom de zone. Le FINAL suppose l'ordre d'ouverture `0x04` (ouverte au jour 8) puis `0x08`
     (4ᵉ zone) puis la zone du boss.
  2. **Code qui ouvre une zone** (écriture d'`état+0x909` par l'histoire), pour un patch : n'ouvrir que les zones
     autorisées par la boîte aux lettres. Idéal : que le patch note aussi dans la boîte aux lettres la zone que
     l'histoire **voulait** ouvrir (→ check « zone débloquée par l'histoire »).
  3. **`FINAL_BOSS_FLAG`** : drapeau « boss final vaincu », au format (décalage dans l'objet d'état, masque).
  4. Si possible : **zone de chaque check** (fruits par zone — peut-être les 5 blocs de 64 bits de `+0x5C`, Oignons,
     objets) pour remplacer la logique prudente actuelle (déduite des jours de la partie de l'utilisateur).
  5. Ouvrir la zone du boss **avant** que l'histoire y arrive : le boss est-il bien là ?
  - (BÊTA, 2026-10-02) **Réponses partielles** (tests en jeu des jours 15–19, détails dans `beta/DECOUVERTES.md`) :
    - **1 ✅ `FINAL_ZONE_BIT = 0x10` = Formidable Oak** (5ᵉ zone ; forcée → présente sur la carte du jour 19, noms
      donnés par l'utilisateur). `0x08` = Twilight River ✅. `0x01` Tropical Wilds, `0x02` Garden of Hope,
      `0x04` Distant Tundra 🔶 (numéros du curseur de la carte `état+0x590` et du tableau « dernier jour joué par
      zone » `état+0x98C`, 5 × u32, -1 = jamais). L'ordre supposé par le FINAL (`0x04`, `0x08`, `0x10`) est donc bon.
    - **2 ⚠ important pour le client FINAL** — **mis à jour 21:58** : (a) **la carte montre toutes les zones jusqu'à
      la plus haute ouverte** : `0x0B` laisse Distant Tundra visible, mais **`0x03` la cache** ✅ (jour 19). Fermer
      marche donc, en partant du haut → le client peut **imposer `OpenAreaFlag` = zones reçues** (`0x03`, `0x07`,
      `0x0F`, `0x1F`), y compris **refermer** ce que l'histoire ouvrirait trop tôt, peut-être **sans patch** ; (b) le
      jeu **recalcule `OpenAreaFlag` quand on sort des Pikmin de l'Oignon** (jour 17 : `0x18` → `0x0F`) → le client
      doit réimposer la valeur à chaque passage (ouvrir **et** fermer, pas seulement un OU). ✅ **Test fait (jour 19)** :
      Pikmin sortis avec `0x03` → **rien de rouvert**, `0x03` gardé dans les sauvegardes des jours 19 et 20. Le
      recalcul ne fait que remplir les zones sous la plus haute ouverte → **pas besoin de patch pour verrouiller**.
      Reste inconnu : l'événement d'histoire qui ouvre une zone (le client devra la refermer aussitôt).
    - **3 ✅ (2026-10-03) `FINAL_BOSS_FLAG = (0x260F, 0x04)`** : allumé juste après la victoire sur le boss final
      (12:33:14), jamais allumé dans les sauvegardes des jours 2–27, présent dans `single28.sav` (sauvegarde d'après
      la fin, 12:39:27). Pendant la scène de fin, `0x08` puis `0x10` s'ajoutent (`+0x260F` = `0x1C`). Indice en plus :
      compteur d'histoire `état+0x4F` = `0x8C` (était `0x86`). Dans le fichier : `0xE86` (= mémoire − 0x1789).
      Sauvegarde gardée : `backups/save_1012be00_2026-10-03_1239_apres_boss_final_jour28`.
    - **5 ❌ (2026-10-03)** : Formidable Oak ouverte en avance (`0x1F`, jour 21, Louie et Olimar pas encore récupérés)
      → l'utilisateur s'y pose : **le boss est là mais ne réagit pas** (pas de combat, invincible, figé). Une **note
      d'Olimar** ramassée sur place a allumé `état+0x2862` bit `0x01` (ensemble F, 10:09:39 ; pas l'ensemble D).
      → L'objectif « boss final » demande aussi l'avancement de l'histoire (déclencheur du combat à trouver quand
      l'histoire y arrivera), pas seulement l'item de zone.

## Journal FINAL

*(le chat FINAL ajoute ses entrées ici)*

- **2026-10-01** — Prise en compte de la coordination (aucun changement de code). Rappel du dernier état FINAL :
  le 2026-09-30, zone des bits de fruits corrigée (`+0x5C`–`+0x83`) dans `worlds/pikmin3/data/memory_map.py`,
  `fruits.py`, `tools/p3_status.py` ; surveillance de `tools/solo_test.py` robuste à la fermeture de Cemu ;
  apworld + `dist/Pikmin_3_Archipelago.zip` reconstruits (30/09 22:18) et recopiés dans `custom_worlds`.
  Tests solo restants : voir `docs/tests_solo_v1.md`.
- **2026-10-01 (soir)** — Sauvegarde `backups/save_1012be00_2026-10-01_1854` (début jour 13) avant écriture.
  Items donnés à 18:54 (jus +1,5 → 14, spray +1) : **perdus** au rechargement 19:33–19:34 (normal, voir le journal
  BÊTA). **Metal Suit Z = bit `0x40`** des objets importants (`état+0x58` : `0x9A` → `0xDA`, 19:48:53, annoncé par
  l'utilisateur) → ajoutée à `worlds/pikmin3` (check « Obtain Metal Suit Z », id 3006, logique 60 Pikmin), options,
  YAML, `GUIDE_FR.md`, `tools/p3_status.py`, ligne des objets dans `findings.md`. 18 tests OK ; apworld + kit
  reconstruits (19:50) et recopiés dans `custom_worlds`. Notes : 2 « notes tuto » annoncées par l'utilisateur
  (19:44:25, 19:46:00) → **ensemble C** (`0x34A4FF5C` : `01` → `03` → `07`), voir la demande ci-dessus.
  Rien repris des essais de la bêta (Oignon bleu écrit à la main ≠ découverte).
- **2026-10-01 (20:00)** — Fin du jour 13 suivie : 5 fruits pressés, le client compte **15 → 20** (sortes 12 → 15),
  jus 12,5 → 12 (arrondi) → 18 → 17 (nuit). `single14.sav` (20:01:21) relu par le code du client : jour 14, jus 17,
  20 fruits, objets `0xDA` (Metal Suit Z conservée). **Cemu fermé à 20:04:29 par l'utilisateur** (pas un plantage) ;
  la sauvegarde du jour 14 est déjà écrite.
- **2026-10-01 (20:4x)** — **Correction Oignons bleu/blanc** (demande BÊTA) dans `worlds/pikmin3` : modèle « type n »
  repris de la bêta — `STATE_ONION_COUNTS = +0xCC` (12 octets par type), `ONION_SLOTS` = 2 bleu `0x04`, 3 rouge `0x08`,
  5 jaune `0x20`, 6 ailé `0x40`, 7 roc `0x80` (`RED_SLOT = 3`) ; type 4 (blancs, `0x10`) jamais lu ni donné
  (`add_onion_pikmin` refuse tout type hors liste). Population = somme des types connus (les bleus `+0xE4` comptent
  enfin). Checks « Discover … Onion » : **mêmes identifiants** (2001 bleu, 2002 jaune, 2003 ailé, 2004 roc) via
  `ONION_LOCATION_ID`. Fichiers : `data/memory_map.py`, `client/game_interface.py`, `client/client.py` (Extra Red →
  type 3), `locations.py`, `tools/solo_test.py` (types 2/3/5/6/7, défaut rouge), `GUIDE_FR.md`. 18 tests OK, test du
  client sur fausse mémoire OK (bleus comptés, blancs ignorés) ; apworld + kit reconstruits et recopiés dans `custom_worlds`.
- **2026-10-01 (20:28)** — Test « Oignon vide » demandé par l'utilisateur (savoir si un Oignon vide redonne un Pikmin,
  utile pour « Progressive Pikmin »). Sauvegarde avant : `backups/save_1012be00_2026-10-01_2028_avant_test_oignon_vide`
  (dernier jour sauvegardé : jour 15). Début du jour 15 : Oignon **bleu** (type 2, `+0xE4`) mis à **0** (10 → 0),
  20:28:47. **Résultat (dit par l'utilisateur) : un Oignon vide donne une pousse le lendemain.** → Pour
  « Progressive Pikmin », un type débloqué avec un Oignon vide n'est pas bloqué : le jeu fournit lui-même un premier
  Pikmin le jour suivant (donner des Pikmin avec l'item reste un choix de confort, pas une obligation).
- **2026-10-02** — **Fin de partie, étape 1 (sans la recherche)** dans `worlds/pikmin3`, version **0.2.0** :
  - Option `goal` : nouveau choix **`final_boss`** (par défaut) = boss final + `fruits_required` fruits ; `fruits`
    et `population` gardés. Nouvelle option **`progressive_zones`** (expérimental, activée) + item
    **« Progressive Zone »** (id 2, progression, ×3).
  - `memory_map.py` : `STATE_OPEN_AREA_FLAG = 0x909`, `STATE_SEEN_AREA_FLAG = 0x90A`, `AREA_FLAGS_AT_START = 0x03`,
    `PROGRESSIVE_ZONE_BITS = (0x04, 0x08, FINAL_ZONE_BIT)`, `FINAL_ZONE_BIT = None` et `FINAL_BOSS_FLAG = None`
    (**TODO**, recherche BÊTA, voir la demande ci-dessus).
  - Logique (`locations.py`, `rules.py`) : chaque check demande un nombre d'items de zone **déduit des jours de la
    partie de l'utilisateur** (fait les jours 2–7 → 0, jours 8–12 → 1, sinon 2) ; fruits : ≤ 5 → 0, ≤ 15 → 1,
    sinon 2 ; population : ≤ 50 → 0, ≤ 240 → 1, sinon 2. Objectif `final_boss` : les 3 zones + limite maximale.
  - Client : ouvre les zones reçues dans `OpenAreaFlag` (OU logique, jamais de fermeture, refait à chaque passage
    donc résiste aux rechargements) ; avertit si la zone du boss ou le drapeau du boss ne sont pas encore connus
    (l'objectif `final_boss` ne peut donc pas encore être validé).
  - YAML du kit : `goal: fruits` gardé (en attendant la détection du boss), `progressive_zones: true` ajouté.
    Guide, docs EN/FR, tests mis à jour : 24 tests OK (+ tests généraux AP OK, 2 échecs connus d'autres jeux), test
    du client sur fausse mémoire OK (zones ouvertes et rouvertes après rechargement). Apworld + kit reconstruits et
    recopiés dans `custom_worlds`.
- **2026-10-02 (soir)** — Fruits en morceaux (dit par l'utilisateur : 1 fruit entier + 2 **moitiés** de kiwi pressés) :
  `single18.sav` (jour 18) relu par le code du client → **20 → 22 fruits pressés** (nouveaux bits n° 257 et 265, en
  `+0x7C` et `+0x7D`), sortes 15 → 16, jus 14 → 16. → Un fruit en morceaux compte **une fois**, quand tous ses morceaux
  sont rentrés ; le comptage du client est bon.
- **2026-10-02 (fin de soirée)** — À la demande de l'utilisateur : relu `COORDINATION.md` et `beta/DECOUVERTES.md`, et
  ajouté la section **« Reste à faire »** (15 points, avec qui fait quoi) pour que la bêta s'en serve de liste de
  travail. Aucun changement de code.
- **2026-10-03 (10:33)** — Notes du jour 21 (annoncées par l'utilisateur : 2 « tuto » + 2 Olimar) : mémoire lue
  (lecture seule) et comparée à `single21.sav` (début du jour 21, zone des notes à `état − 0x17B9` dans le fichier) →
  A +2, D +1, F +1 (voir « État commun » et le point 11). Pris note du résultat BÊTA du point A2 (boss de Formidable
  Oak figé si la zone est ouverte en avance) : conséquence pour l'objectif « boss final » à discuter avec
  l'utilisateur. Aucun changement de code.
- **2026-10-03 (11:25–11:30)** — Notes jours 22–23 relevées (B, A, G = Secret Memos, F ; voir le point 11) et pressages
  suivis (24 → 28, 28 → 32, confirmés par `single22.sav`). **Sauvetage de Louie suivi au journal** (lecture seule,
  `docs/phase0/logs/state_journal_2026-10-03_louie.log`) : objets importants bit **`0x01` = Louie**, et l'histoire ouvre
  **Formidable Oak** (`0x0F` → `0x1F`) 37 s après (point A3 ✅, hypothèse pour A2 : combat du boss = après Louie).
  Ajouté à `worlds/pikmin3` : `KEY_ITEM_BITS[0x01] = "Louie"`, check **« Rescue Louie »** (id 3000, logique 60 Pikmin
  + toutes les zones à fruits), textes (options, YAML, `GUIDE_FR.md`), `tools/p3_status.py`. 24 tests OK ; apworld +
  kit reconstruits et recopiés dans `custom_worlds`.
- **2026-10-03 (12:36)** — **Boss final vaincu** (dit par l'utilisateur) : copie de la mémoire de l'objet d'état
  (lecture seule) → `docs/phase0/logs/etat_apres_boss_2026-10-03_123614.bin` (`0x34A4C000`–`0x34A50200`). Confirme les
  candidats BÊTA du point A1 : `état+0x4F` = `0x8C` (compteur d'avancement), `état+0x260F` = `0x0C` (**bit `0x04`
  allumé**). En attente de la confirmation BÊTA dans la sauvegarde d'après la fin ; le FINAL mettra alors
  `FINAL_BOSS_FLAG = (0x260F, 0x04)` et passera le YAML du kit à `goal: final_boss`.
- **2026-10-03 (12:45)** — **Fin de partie intégrée** (après la confirmation BÊTA dans `single28.sav`) dans
  `worlds/pikmin3` : `FINAL_BOSS_FLAG = (0x260F, 0x04)`, `FINAL_ZONE_BIT = 0x10`, `ZONE_NAMES`, `ZONE_LOCK_FIRST_DAY = 2`,
  `STATE_STORY_PROGRESS = 0x4F` (noté, pas utilisé). Client : `set_zones` impose exactement les zones reçues (ouvre
  **et** referme, à partir du jour 2, messages avec le nom des zones) ; l'objectif `final_boss` est validé quand le
  drapeau du boss est allumé et qu'il y a assez de fruits. Textes mis à jour (options, YAML du kit → **`goal:
  final_boss`**, `GUIDE_FR.md`, docs EN/FR). 24 tests OK ; test du client sur fausse mémoire OK (zone ouverte par
  l'histoire refermée, Formidable Oak ouverte au 3ᵉ item, objectif envoyé après le boss seulement, jour 1 non touché).
  Apworld + kit reconstruits et recopiés dans `custom_worlds`. Reste : essai en vraie partie avec le client.
- **2026-10-03 (après-midi)** — **V1 complète de l'APWorld (version 1.0.0)** à la demande de l'utilisateur, avec les
  informations de la bêta :
  - **Notes** : règle BÊTA (catégorie c à `état+0x27C0 + 0x20c`, note n = bit n) ; « Tutorial Note N » = A + B + C,
    « Olimar Note N » = D + F, nouveaux checks **« Secret Memo N »** = G (option `secret_memo_count`, 0–10, défaut 0,
    ids 4201–4210). Maximums = totaux d'une partie terminée (`single28.sav` : 63 conseils, 15 Olimar) ; `note_checks`
    **activé par défaut** (30 conseils, 8 Olimar). Logique tirée des sauvegardes de chaque jour (zones connues) :
    conseils ≤ 29 → 0 zone, ≤ 47 → 1, ≤ 51 → 2, sinon 3 ; Olimar ≤ 1 → 0, ≤ 5 → 1, ≤ 6 → 2, sinon 3 ; Secret Memos →
    3. Nombres par jour relevés dans les `singleN.sav` (zone des notes à `état − 0x17B9`).
  - **Progressive Pikmin** (option `progressive_pikmin`, expérimentale, désactivée) : voir le point 10.
  - **Fin de partie** (déjà intégrée) : objectif `final_boss` par défaut, zones imposées exactement, Louie.
  - Fichiers : `data/memory_map.py` (`STATE_NOTE_CATEGORIES`, groupes de catégories, badge, `STATE_ONION_MERGED`,
    `PROGRESSIVE_PIKMIN_TYPES`), `client/game_interface.py` (7 catégories lues, `unlock_pikmin_types`),
    `client/client.py`, `items.py` (item 3), `options.py`, `locations.py`, `world.py`, `archipelago.json` (1.0.0),
    tests, docs EN/FR, `GUIDE_FR.md` (réécrit pour la V1), YAML du kit (`Pikmin 3: 1.0.0`), `tools/solo_test.py`.
  - Vérifications : **29 tests OK** ; tests généraux AP OK (2 échecs connus d'autres jeux) ; test du client sur fausse
    mémoire OK (notes A/C, D/F, G comptées ; type de Pikmin débloqué seulement au changement de jour ; zones et boss) ;
    génération **Pikmin 3 (défaut) + Pikmin 3 (toutes options) + Pokémon XY** OK. Apworld + kit reconstruits et
    recopiés dans `custom_worlds` ; graphic pack de Cemu identique.
  - Reste : la première vraie partie avec le client et un serveur (`docs/tests_solo_v1.md` + point E de « Reste à
    faire »).
- **2026-10-03 (soir)** — Exigences de l'utilisateur notées (« Décisions de l'utilisateur » + section F de « Reste à
  faire », points 16–18) : pas d'ouverture de zone par l'histoire, pas d'Oignons hors rouge, correspondance complète
  des bits des fruits et des notes. Recherche confiée à la BÊTA ; le FINAL intégrera. Aucun changement de code.
- **2026-10-03 (soir)** — **Projet publié sur GitHub** à la demande de l'utilisateur :
  <https://github.com/OmgaCraft/ArchiPelago-Pikmin-3> (branche `main`, commit `7a46569`, 103 fichiers ≈ 870 Ko :
  version finale, bêta, outils, docs, kits `dist/`, `COORDINATION.md`). Ajoutés : `.gitignore` (exclut `backups/`,
  `tools/.probe_state/`, `*.bin`, caches Python) et `README.md` (présentation du dépôt). Auteur git : celui configuré
  sur le PC de l'utilisateur.

## Journal BÊTA

- **2026-10-01** — Création de ce fichier, de `CLAUDE.md` (qui demande de le lire) et du dossier `beta/`.
- **2026-10-01** — **Bêta 0.1.0 construite**, à partir d'une copie de `worlds/pikmin3` du 30/09 22:18 (avec la
  correction des fruits). Jeu « Pikmin 3 Beta », dossier `beta/worlds/pikmin3_beta/`, kit
  `beta/dist/Pikmin_3_Archipelago_Beta.zip` (apworld + `beta/yaml/Pikmin 3 Beta.yaml` + `beta/GUIDE_BETA_FR.md`
  + `beta/DECOUVERTES.md`). Ajouts : checks jours / sortes de fruits / notes A-B-C-D / étapes d'histoire ;
  items Pikmin jaunes, rocs, bleus, ailés (en rouges si l'Oignon n'est pas découvert) et baies ;
  **journal des découvertes** dans le client (`/note`, `/decouvertes`, fichier
  `Archipelago\logs\Pikmin3Beta_decouvertes.txt`, actif même sans serveur). Graphic pack séparé
  `Pikmin3_Archipelago_Beta` (« Mods > Archipelago Beta »), signature de boîte aux lettres `P3APBETA` (le pack final
  garde `P3APMBOX`) ; mêmes patches. Le client bêta avertit si les deux packs sont cochés.
  Tests : 26 tests bêta OK, tests généraux AP OK (2 échecs connus d'autres jeux), test du client sur fausse mémoire,
  génération avec **final + bêta + Pokémon XY** ensemble, connexion serveur OK.
  Ressources partagées touchées : `pikmin3_beta.apworld` copié dans `C:\ProgramData\Archipelago\custom_worlds`
  (à côté de `pikmin3.apworld`, inchangé) ; pack bêta copié dans `%APPDATA%\Cemu\graphicPacks` **sans être coché**
  (le pack coché reste `Pikmin3_Archipelago`). Aucun fichier du chat FINAL modifié.
- **2026-10-01** — **Console des checks** (demande de l'utilisateur : « Note "type" obtenue » quand il finit un check).
  Nouveau `beta/worlds/pikmin3_beta/client/events.py` (compare deux instantanés → une phrase par check, avec le nom
  du check AP) et `data/check_names.py` (noms des checks en un seul endroit, sans dépendance à AP ; `locations.py`
  s'en sert). Affichage : onglet **« Checks »** du Pikmin 3 Beta Client + commande `/checks`, et console autonome
  `beta/console_checks.py` / `beta/Console des checks.bat` (sans Archipelago, lit le code depuis le dossier source
  ou depuis `pikmin3_beta.apworld`, copie dans `beta/logs/checks_AAAA-MM-JJ.txt`). 30 tests bêta OK.
  Apworld + kit reconstruits (le kit contient maintenant la console) ; `pikmin3_beta.apworld` remplacé dans
  `custom_worlds`. Idée réutilisable par FINAL s'il veut la même console (copier `events.py` + `check_names.py`).
- **2026-10-01** — **Test « donner les Pikmin bleus » (à la demande de l'utilisateur) → plantage.** Outil
  `beta/tools/beta_test.py` (status / pikmin / onion). +10 Pikmin dans l'emplacement 1 : rien de visible. Bit `0x10`
  de `état+0xA4` allumé pendant le chargement du jour 13 → scène de fusion (mais de l'Oignon **jaune**), nouveau mot
  `état+0xC8` = 1, puis au jour 14 **le jeu plante** sur le terrain. Détails dans `beta/DECOUVERTES.md`.
  ⚠ **Pour les deux chats : ne jamais écrire le bit d'un Oignon non découvert (`état+0xA4`)**.
  Sauvegardes : avant le test `backups/save_1012be00_2026-10-01_1855_avant_bleus` (début jour 13, saine),
  après `…_1920_plantage_jour14_oignon_bleu` (jour 14, plante). `single13.sav` dans le dossier du jeu est sain.
  Le menu « Recommencer la journée » réécrit l'objet d'état avec l'aperçu de chaque jour (écritures perdues).
- **2026-10-01 (soir)** — **Zones et Oignons : nouvelles adresses (analyse du code + tests en jeu forcés).**
  Détails dans `beta/DECOUVERTES.md` (section « Analyse du code »). Pour les deux chats :
  - **`état+0x909` = `OpenAreaFlag`** (u8, bit n = zone n ; `0x07` au jour 13). Forcé à `0x0F` → **la 4ᵉ zone apparaît
    sur la carte du vaisseau** ✅. `état+0x90A` = `SeenAreaFlag`. → un item « zone » est faisable.
  - **`état+0x908` = `UniteOnyon`** (Oignons fusionnés, même codage que `+0xA4`). Découvert sans fusionné = scène de
    fusion au prochain atterrissage. Découvert + fusionné forcés ensemble = colonne visible tout de suite.
  - **Correspondance confirmée par l'utilisateur : bit `0x10` / emplacement 1 = BLEU, bit `0x40` / emplacement 3 = AILÉ
    (rose)** — l'hypothèse d'origine de `memory_map.py` était juste ; ignorer l'inversion notée plus tôt dans la bêta.
  - `état+0xA4` est en fait le haut d'un ensemble de **64 drapeaux** (mots `+0xA4`/`+0xA8`, méthodes virtuelles
    `0x02FDA064`/`0x02FDA08C`) ; un 2ᵉ ensemble de 64 drapeaux à `état+0x9C`.
  - Noms des champs de partie (« SingleGameParams ») en `0x1033F40C`–`0x1033F5C0`, fonction de sauvegarde
    `0x0300A2xx`–`0x0300ACxx`, base `état+0x14` : utile pour trouver les autres champs (`EventFlag`, `LastProgress`…).
  - Les valeurs actuelles de la partie de l'utilisateur sont **forcées par les tests** (zone 4, Oignon ailé + 10 Pikmin) :
    ce ne sont pas des découvertes naturelles. Sauvegardes d'avant les tests dans `backups/` (`…_1940_avant_zone`).
- **2026-10-01 (20:05)** — **Pikmin ailés utilisables ✅** : avec l'Oignon ailé forcé « découvert » (`+0xA4` bit `0x40`)
  **et** « fusionné » (`+0x908` bit `0x40`) + 10 Pikmin dans l'emplacement 3, l'utilisateur les a fait sortir
  (20:02:08) et ils sont dans son équipe au jour 14, **sans plantage** (le plantage du matin = découvert sans fusionné).
  → Items « Oignon / type de Pikmin » et « zone » faisables (à concevoir dans la bêta). Metal Suit Z (`0x40`, trouvée
  par le FINAL) reprise dans la bêta (check « Obtain Metal Suit Z », même id 3006). Bêta reconstruite (20:04).
  ⚠ Partie de l'utilisateur au jour 14 avec des valeurs forcées par la bêta (zone 4, Oignon ailé + 10 Pikmin ailés).
- **2026-10-01 (20:15)** — À la demande de l'utilisateur : tout l'état des connaissances regroupé dans « État commun »
  ci-dessus, et ajout de la section « Décisions de l'utilisateur » (Progressive Pikmin pour la finale : rouges de base,
  puis Roc → Jaune → Ailé → Bleu) + demande au chat FINAL.
- **2026-10-01 (20:20)** — Réponses de l'utilisateur : pose dans la 4ᵉ zone ✅ ; Pikmin ailés normaux ✅ ; l'Oignon ailé
  « seul » de l'histoire n'apparaît plus dans la zone (déjà fusionné) ✅. Test des bleus prévu plus tard.
  Conséquence pour « Progressive Pikmin » (finale) : si l'item arrive avant que le joueur trouve l'Oignon, l'histoire
  ne le propose plus. Reste à gérer le cas inverse (joueur qui trouve l'Oignon avant l'item).
- **2026-10-01 (20:11)** — **Test « bleus » → ce sont les BLANCS.** Sauvegarde avant :
  `backups/save_1012be00_2026-10-01_2010_avant_test_bleus` (jour 14). Bit `0x10` allumé dans `+0xA4` **et** `+0x908`
  (`0xE8` → `0xF8`) + 10 Pikmin dans l'emplacement 1 (20:11:04) → 5ᵉ colonne dans le menu de l'Oignon avec une icône
  de **Pikmin blanc** (yeux rouges), confirmé par l'utilisateur ; en sortir 1 (20:11:19) → **plantage** (Cemu fermé).
  La sauvegarde du jour 14 n'est pas touchée (test en pleine journée). **Décision de l'utilisateur : chercher le bit
  des bleus par élimination.** La bêta (`beta/worlds/pikmin3_beta`) a encore « Blue » sur l'emplacement 1 : à corriger
  (emplacement 1 = blanc, check « Discover Blue Onion » et item « Extra Blue Pikmin » en attente du vrai bit).
- **2026-10-01 (20:17)** — **Élimination : BLEU = bit `0x04`** (1er candidat). Sauvegarde avant :
  `backups/save_1012be00_2026-10-01_2014_avant_elimination_bleu`. Bit `0x04` découvert + fusionné sans Pikmin
  (20:14:58) → nouvelle colonne **bleue** (utilisateur). 10 Pikmin en `état+0xE4` (20:15:41) → colonne bleue à 10 ✅
  (capture 20:15:47) → règle « bit n = type n, tableau à `état+0xCC` ». « Tout sélectionner » + OK (20:15:51) →
  **plantage**. Rechargement du jour 14, bleus remis (20:17:07 : `0xEC` / `0xEC`, 10 en `+0xE4`) ; l'utilisateur passe
  la journée pour tester la sortie au jour 15 (hypothèse : modèles chargés au chargement de la journée).
  À reporter dans les deux mondes : bleu `0x04` / `+0xE4` ; blanc `0x10` (à ne jamais donner).
- **2026-10-02** — Relu le journal FINAL (test « Oignon vide », jour 15). **Début du travail sur les zones** (demande
  de l'utilisateur : « faire la même chose avec les zones » que pour les Oignons). Historique naturel relevé dans les
  sauvegardes `backups/` (`singleN.sav`, octets `0x499`–`0x49C` = `état+0x908`–`+0x90B`) : zones ouvertes `0x03` aux
  jours 2–7, `0x07` à partir du jour 8 ; zones vues `0x05` au jour 2 puis `0x07`, `0x0F` au jour 15 (après la pose
  en zone 3 forcée) ; `état+0x90B` (sans nom) toujours égal aux zones vues. Outil `beta/tools/beta_test.py` :
  commandes `zones`, `zone N on|off [--seen]` (sauvegarde automatique dans `backups/` avant d'écrire) et `backup`.
  `beta/DECOUVERTES.md` mis à jour (tableau final des Oignons + section « Zones » et tests prévus). Code des Oignons
  de la bêta (`ONION_SLOTS`) **pas encore corrigé** (toujours l'ancien modèle).
- **2026-10-02 (20:58–21:40)** — **Tests des zones en jeu** (jours 15 → 19, l'utilisateur termine une journée par test).
  Sauvegardes automatiques avant chaque écriture : `backups/save_1012be00_2026-10-02_2058_avant_zone3_off`,
  `…_2101_avant_zone3_on`, `…_2108_avant_zone4_on`, `…_2134_avant_zone4_on`. Résultats :
  zone 3 fermée → **Twilight River** disparaît de la carte (fermeture gardée dans la sauvegarde du jour 16), rouverte →
  de retour ; zone 2 fermée → **Distant Tundra reste** (zone ouverte par l'histoire) ; zone 4 forcée → **Formidable
  Oak** sur la carte du jour 19. Le jeu a **réécrit `OpenAreaFlag` à `0x0F`** quand l'utilisateur a sorti des Pikmin
  de l'Oignon (jour 17, 21:08:46). Nouveaux champs : `état+0x590` curseur de la carte, `état+0x98C` dernier jour joué
  par zone (5 × u32). Fouille de toute la mémoire : une seule copie de l'objet d'état. `memory_map.py` de la bêta
  (`AREA_BITS`, `STATE_CURRENT_AREA`, `STATE_AREA_LAST_DAY`), `beta/tools/beta_test.py` et `beta/DECOUVERTES.md` mis à
  jour ; réponse partielle à la demande « Fin de partie » du FINAL (points 1 et 2). Pikmin 3 fermé par l'utilisateur à 21:40.
- **2026-10-02 (21:53–21:58)** — À la demande de l'utilisateur, zones Formidable Oak, Twilight River et Distant Tundra
  fermées (`0x0F` → **`0x03`**, 21:54:26, jour 18 rechargé par l'utilisateur ; sauvegarde avant :
  `backups/save_1012be00_2026-10-02_2153_avant_fermeture_zones_2_3_4`). Rien rouvert par le jeu ; fin de journée →
  jour 19 avec `0x03`. **Carte du jour 19 : Distant Tundra a disparu** (dit par l'utilisateur) → règle « la carte
  montre toutes les zones jusqu'à la plus haute ouverte » ; fermer marche en partant du haut. Réponse au FINAL (point 2)
  mise à jour : le client peut imposer les zones reçues (ouvrir et refermer), peut-être sans patch. Décision /
  constat de l'utilisateur ajouté dans « Décisions de l'utilisateur ».
- **2026-10-02 (22:02)** — **Verrouillage des zones confirmé** : avec `OpenAreaFlag` = `0x03`, l'utilisateur a sorti des
  Pikmin de l'Oignon au jour 19 → aucune zone rouverte (surveillance continue), `0x03` gardé dans `single19.sav` et
  `single20.sav` ; carte du jour 20 : Tropical Wilds + Garden of Hope seulement (dit par l'utilisateur). Le recalcul
  du jour 17 ne venait donc pas de l'histoire. Réponse au FINAL (point 2) et `beta/DECOUVERTES.md` mis à jour.
  Partie de l'utilisateur : jour 20, zones `0x03` (Distant Tundra fermée alors que l'histoire l'avait ouverte).
- **2026-10-02 (22:15)** — Lu la liste « Reste à faire ». Choix de l'utilisateur : **rouvrir les 5 zones** (`0x1F`, avec
  Formidable Oak pour le point A2). Pikmin 3 fermé : script de session (dossier de travail du chat BÊTA) qui attend
  le prochain chargement, sauvegarde la partie dans `backups/`, impose `0x1F`, puis note chaque fruit pressé avec son
  bloc de 64 bits et la zone du moment (point A4), les objets, Oignons et étapes d'histoire. Le point A3 (ouverture
  naturelle d'une zone) ne peut plus être observé dans cette partie (toutes les zones ouvertes).
- **2026-10-02 (22:20)** — Réponses de l'utilisateur : **Pikmin bleus sortis sans problème** (point 7 ✅, règle « type
  utilisable dès la journée suivante » confirmée) ; **aucune animation** quand Formidable Oak est apparue sur la carte
  (point 5, `SeenAreaFlag`). Jeu pas démarré : script de session arrêté par l'utilisateur, zones à rouvrir (`0x1F`)
  au prochain lancement.
- **2026-10-02 (23:20)** — **Code des Oignons de la bêta corrigé** (modèle « type n », comme le FINAL) :
  `beta/worlds/pikmin3_beta/data/memory_map.py` (`STATE_ONION_COUNTS = 0xCC`, `ONION_SLOTS` = 2 bleu `0x04`, 3 rouge,
  5 jaune, 6 ailé, 7 roc, `RED_SLOT = 3`, `WHITE_TYPE = 4` jamais lu ni donné, noms des zones `AREA_BITS`),
  `client/game_interface.py`, `client/client.py`, `client/events.py` (message spécial si le bit des blancs s'allume,
  noms des zones), `client/discovery.py`, `items.py`, `locations.py` (`ONION_LOCATION_ID` : mêmes identifiants
  2001–2004), tests, `beta/tools/beta_test.py`, `GUIDE_BETA_FR.md`, YAML. 31 tests bêta OK, test du client sur fausse
  mémoire OK (bleus comptés, blancs ignorés, « Discover Blue Onion » envoyé). Apworld + kit reconstruits ;
  `pikmin3_beta.apworld` remplacé dans `custom_worlds`.
- **2026-10-03 (09:43–10:00)** — Zones mises à `0x1F` sur la carte du jour 20 (choix de l'utilisateur ; sauvegarde
  avant : `backups/save_1012be00_2026-10-03_0943_avant_zones_1F_jour20`). Surveillance de tout l'objet d'état
  pendant la journée. **Le mur de Garden of Hope que Louie fait exploser dans l'histoire est cassé au jour 20**, alors
  que Louie n'est pas encore récupéré : hypothèse de l'utilisateur, l'ouverture de Formidable Oak fait charger Garden
  of Hope « après Louie » (à confirmer en refermant seulement Formidable Oak). Si c'est confirmé, à noter pour le FINAL :
  le dernier « Progressive Zone » ouvrirait aussi ce passage (accès à l'Oignon bleu naturel).
- **2026-10-03 (10:00–10:12)** — **Mur de Garden of Hope** : l'utilisateur a rechargé les jours 17 (mur debout) et 18
  (mur cassé) → cassé pendant la journée 17. Bits allumés entre `single17.sav` et `single18.sav` (zone « histoire »,
  dans le fichier à `mémoire − 0x1789`) : `+0x264C` `0x08`, `+0x267B` `0x04`, `+0x268F` `0x20`, `+0x2A22` `0x08`,
  `+0x2B2B` `0x01`. Ce jour-là, Formidable Oak avait été ouverte 34 s (test BÊTA 21:08). Test par élimination préparé
  (bits forcés au chargement du jour 17). **Formidable Oak en avance (point A2)** : boss présent mais figé,
  invincible, pas de combat ; note d'Olimar → ensemble F (`+0x2862` `0x01`), à revoir : F ≠ seulement « étapes ».
  Sauvegardes : `…_2026-10-03_1007_jour21_formidable_oak` (début du jour 21).
- **2026-10-03 (10:17–10:30)** — Test du mur (jour 17 rechargé) : les 5 bits forcés **ne cassent pas** le mur (pose à
  Garden of Hope à 10:22, mur debout). Nouveau candidat trouvé dans les sauvegardes : **`état+0x735` bit `0x80`**
  (octet qui gagne des bits au fil de l'histoire, sans doute des scènes vues ; fichier `0x446` = mémoire − 0x2EF ;
  allumé exactement entre les jours 17 et 18) — **pas encore testé** : l'utilisateur a arrêté les recherches pour
  jouer (boss de Garden of Hope). Partie rechargée au jour 21 : aucune valeur forcée des tests du mur ne reste
  (sauvegardes 17–21 intactes) ; zones toujours `0x1F`. Surveillances arrêtées par l'utilisateur.
- **2026-10-03 (11:25–11:31)** — Surveillance pendant la suite de l'histoire (aucune écriture). **Louie récupéré**
  (jour 23, Garden of Hope, 11:26:39) : drapeau `état+0x276E` bit `0x02` + **nouvel objet important `état+0x58` bit
  `0x01`** (jamais vu avant → check « Louie » possible). **Point A3 observé ✅** : 11:27:18, scène « Louie interrogé »
  + animation de la carte, et le jeu **ajoute** le bit de Formidable Oak (`OpenAreaFlag` `0x0F` → `0x1F`, OU logique) ;
  `SeenAreaFlag` inchangé (`0x0F`). → Le client FINAL peut détecter l'ouverture par l'histoire (bit apparu sans item)
  et refermer la zone / envoyer un check. Vol du jus et du canard par Louie : pas encore vu. Jour 24 : pose à
  Formidable Oak (11:30:58, nouveau drapeau `état+0x26AF` `0x01`). Sauvegarde : `…_jour24_avant_formidable_oak`.
- **2026-10-03 (11:31)** — **Notes : règle trouvée** (point 11 ; sans écriture, sur ce que l'utilisateur ramasse). Chaque
  catégorie de notes du GamePad a son ensemble de bits : catégorie *c* à `état+0x27C0 + 0x20 × c` (A = 0, B = 1,
  C = 2, D = 3, E = 4, **F = 5**, G = 6), note n° *n* = bit *n* des mots big-endian (mot n/32, bit n%32). Le badge
  « nouvelle note » du GamePad = `état+0x28A3` (catégorie) et `état+0x28A7` (numéro de la note) — vérifié 3 fois :
  B n° 25 (`+0x27E0` `0x30`→`0x32`, jour 20), F n° 8 (`+0x2862` `0x01`, note d'Olimar à Formidable Oak, jour 21),
  F n° 4 (`+0x2863` `0x0F`→`0x1F`, **message de l'équipage à l'arrivée dans Formidable Oak**, jour 24). → L'ensemble F
  n'est pas « étapes d'histoire » mais une catégorie de notes (messages de l'équipage, notes d'Olimar…) ; les checks
  bêta « Story Event N » comptent donc des notes. Noms des catégories : ordre des onglets du GamePad à demander.
- **2026-10-03 (11:27–11:47)** — **Boss final : candidats pour « le boss se réveille »** (surveillance, aucune écriture,
  à confirmer par un test). Au jour 21 (Formidable Oak forcée, boss figé) : `état+0x4F` = `0x7B`. Puis l'histoire :
  `+0x4F` `0x81`→`0x82` à l'ouverture de Formidable Oak par l'histoire (11:27:18), `0x83` à l'arrivée (11:31:16),
  **`0x84` pendant la scène « Olimar et le boss »** (11:32:46), `0x85` (11:34:18) → `+0x4F` (octet bas du mot
  `+0x4C`) ressemble à un **compteur d'avancement de l'histoire**. Drapeaux allumés pendant cette scène et gardés :
  **`état+0x26AE` bit `0x10` (11:32:24) puis `0x40` (11:32:49)**, puis `0x08` (11:44:04) et `0x20` (jour 25).
  `+0x26AD` et `+0x26AF` : remis à zéro à chaque pose (drapeaux de la visite). Note tuto du boss : catégorie C n° 28
  et 29. Test prévu : recharger `…_2026-10-03_1007_jour21_formidable_oak` (boss figé), forcer `+0x4F` = `0x84` et/ou
  `+0x26AE` |= `0x50` avant de se poser, et voir si le boss réagit. Sprays +10 (2 → 12) et Oignons à 100 fleurs
  (11:40) à la demande de l'utilisateur pour le combat (sauvegarde `…_1140_avant_100_fleurs_boss`).
- **2026-10-03 (12:33)** — **BOSS FINAL VAINCU** (dit par l'utilisateur ; Oignons à 100 fleurs et +10 sprays donnés pour
  le combat). Point A1, **candidats pour `FINAL_BOSS_FLAG`** (surveillance, rien d'autre pendant le combat) : à la
  fin de la journée qui suit la victoire (12:33:13, jour 27 → 28) **`état+0x4F` saute de `0x86` à `0x8C`** et
  **`état+0x260F` bit `0x04`** s'allume (12:33:14 ; jamais allumé dans aucune sauvegarde des jours 2–27). À confirmer
  dans la sauvegarde d'après la fin. **`état+0x4F` = compteur d'avancement de l'histoire** (`LastProgress` ?), relu dans
  toutes les sauvegardes : `0x1E` (jour 2) … `0x5B` (jours 13–17), **`0x7B` au jour 18** (le jour où le mur de Garden
  of Hope s'est cassé, après l'ouverture forcée de Formidable Oak au jour 17), `0x82` (ouverture de Formidable Oak par
  l'histoire), `0x84` (scène du boss), `0x86`, `0x8C` (boss vaincu). → Le mur et le réveil du boss dépendent sans
  doute de ce compteur (boss figé au jour 21 avec `0x7B`). Tests à faire : `0x7B` sur le jour 17 (mur ?), `0x84` sur
  le jour 21 (boss ?).
- **2026-10-03 (12:39)** — **`FINAL_BOSS_FLAG` confirmé dans la sauvegarde** : `single28.sav` (écrite à 12:39:27 après la
  fin) contient `+0x260F` = `0x1C` (bits `0x04` à la victoire, `0x08` à 12:34:59, `0x10` à 12:36:19) et `+0x4F` =
  `0x8C`. Nouveaux fichiers écrits en même temps : `mission.sav`, `srank.sav`, `radar4.sav` (mode Mission débloqué ?).
  Réponse ajoutée sous la demande « Fin de partie » du FINAL (point 3). Sauvegarde :
  `backups/save_1012be00_2026-10-03_1239_apres_boss_final_jour28`.
