# Découvertes de la bêta

Ce que le journal des découvertes (`Archipelago\logs\Pikmin3Beta_decouvertes.txt`) a permis d'identifier.
Une fois confirmé, à reporter dans [docs/phase0/findings.md](../docs/phase0/findings.md) et à signaler au chat FINAL
dans [COORDINATION.md](../COORDINATION.md).

Légende : ✅ confirmé en jeu · 🔶 probable · ❓ à vérifier

## À confirmer en priorité

| Donnée | Hypothèse actuelle | Comment la confirmer | Statut |
|---|---|---|---|
| Oignon bleu | **bit `0x04`** (type 2), Pikmin à `état+0xE4` — forcé, colonne bleue vue | découverte naturelle dans l'histoire | 🔶 |
| Oignon ailé | **bit `0x40`** (type 6), Pikmin à `état+0x114` — forcé, Pikmin sortis et normaux | découverte naturelle dans l'histoire | ✅ |
| Bits `0x01` / `0x02` (types 0 et 1) | inconnus | élimination (prudence : `0x10` = blancs, plantage) | ❓ |
| Zones : quel bit = quelle zone | bit n = zone n (`état+0x909`) ; noms inconnus | tests par élimination (voir « Zones ») | ❓ |
| Data Glutton | bit `0x02` de `état+0x58` | revoir dans une partie neuve | 🔶 |
| Ensembles de notes A, B, C | A = Pikmin-ology lues, B = tutoriels, C = documents ramassés / scènes | comparer avec les catégories du GamePad | 🔶 |
| Étapes d'histoire | ensemble F (`état+0x2860`) : bit 0 Data Glutton, bit 1 Charlie | noter chaque nouvelle étape (`/note`) | 🔶 |
| Baies ultra-épicées | `état+0x59C` ; l'item « Ultra-Spicy Berry » ajoute 1 baie | vérifier à l'écran et à la fabrication du spray | ❓ |
| Déblocage naturel d'une zone par l'histoire | `OpenAreaFlag` (`état+0x909`) mis à jour par le jeu | `/note nouvelle zone` au prochain déblocage | 🔶 |

## Oignons : état des connaissances (fin du 2026-10-01)

⚠ Remplace les hypothèses « emplacement 0–4 » plus bas dans ce fichier (journal d'époque, gardé tel quel).

- **Règle : bit n = type n**, dans « découverts » (`état+0xA4`) comme dans « fusionnés » (`UniteOnyon`, `état+0x908`).
  Le tableau des Pikmin par Oignon commence à **`état+0xCC`**, 12 octets par type (feuille, bouton, fleur).

  | Bit | Type | Pikmin (feuilles) | Statut |
  |---|---|---|---|
  | `0x01` | 0 ? | `+0xCC` | ❓ jamais testé |
  | `0x02` | 1 ? | `+0xD8` | ❓ jamais testé |
  | `0x04` | **bleu** | `+0xE4` | ✅ colonne bleue (forcé le 2026-10-01 20:14) |
  | `0x08` | rouge | `+0xF0` | ✅ |
  | `0x10` | **blanc** | `+0xFC` | ⛔ plantage dès qu'un Pikmin blanc sort : **ne jamais donner** |
  | `0x20` | jaune | `+0x108` | ✅ |
  | `0x40` | **ailé** (rose) | `+0x114` | ✅ sortis et normaux |
  | `0x80` | roc | `+0x120` | ✅ |

- **Débloquer un type** = allumer son bit dans `+0xA4` **et** `+0x908`. `+0xA4` seul → scène de fusion avec le mauvais
  Oignon puis plantage. Un type forcé puis sorti **le jour même** a planté (blancs, bleus) ; forcé la veille, il marche
  (ailés). → donner le type pour la journée suivante.
- Un type débloqué **avant** l'histoire : l'Oignon « seul » de l'histoire ne s'affiche plus (pas de conflit).
- Un **Oignon vide** donne une pousse le lendemain (dit par l'utilisateur, 2026-10-01) : pas de blocage.
- Décision de l'utilisateur pour la finale : « Progressive Pikmin » rouges de base puis roc → jaune → ailé → bleu.

## Boss final : ce qui le réveille (2026-10-03, candidats à tester)

| Moment (jour 24) | Écrit par le jeu |
|---|---|
| Jour 21, Formidable Oak forcée, boss figé | `état+0x4F` = `0x7B` |
| Louie récupéré, Formidable Oak ouverte par l'histoire (11:27:18) | `+0x4F` `0x81` → `0x82`, `OpenAreaFlag` + `0x10` |
| Arrivée à Formidable Oak (11:31:16) | `+0x4F` → `0x83` |
| **Scène « Olimar et le boss »** (11:32:24–11:32:49) | **`+0x26AE` bit `0x10`, `+0x4F` → `0x84`, `+0x26AE` bit `0x40`** |
| Note tuto du boss (11:33:29) | notes C n° 28 et 29 ; `+0x4F` → `0x85` (11:34:18) |

- `+0x4F` (octet bas du mot `+0x4C`) : sans doute un **compteur d'avancement de l'histoire** 🔶.
- `+0x26AD` / `+0x26AF` : remis à zéro à chaque pose → drapeaux de la visite, pas l'histoire.
- Test : recharger `backups/save_1012be00_2026-10-03_1007_jour21_formidable_oak`, forcer `+0x4F` = `0x84` et/ou
  `+0x26AE` |= `0x50` avant de se poser, voir si le boss réagit.
- **Boss final vaincu (2026-10-03, jour 27)** : rien d'écrit pendant le combat ; à la fin de la journée (12:33:13)
  **`+0x4F` `0x86` → `0x8C`** et **`+0x260F` bit `0x04`** (jamais allumé dans les sauvegardes des jours 2–27).
  ✅ **`FINAL_BOSS_FLAG = (0x260F, 0x04)`** : présent dans `single28.sav` (après la fin, 12:39:27) ; la scène de fin
  ajoute `0x08` (12:34:59) et `0x10` (12:36:19) → `+0x260F` = `0x1C`. Fichier : `0xE86`. `+0x4F` = `0x8C`.
- **`+0x4F` dans toutes les sauvegardes** : `0x1E` (j2), `0x32` (j3–6), `0x3A`, `0x3C`, `0x46`, `0x50`, `0x58`,
  `0x5A`, `0x5B` (j13–17), **`0x7B` (j18 : mur de Garden of Hope cassé, après Formidable Oak forcée au jour 17)**,
  `0x82`, `0x85`, `0x86`, `0x8C`. → compteur d'avancement (`LastProgress` ?) qui commande sans doute le mur et le boss.

## Notes du GamePad : règle (2026-10-03)

- Catégorie *c* (onglet du GamePad) = ensemble de bits à `état+0x27C0 + 0x20 × c` : A = 0 (`+0x27C0`), B = 1, C = 2,
  D = 3, E = 4, **F = 5** (`+0x2860`), G = 6. Note n° *n* = bit *n* (mots big-endian de 32 bits, mot n/32, bit n%32).
- Badge « nouvelle note » : `état+0x28A3` = catégorie, `état+0x28A7` = numéro de la dernière note (copie en
  `+0x29BF` / `+0x29C3`). Copies des ensembles à +0x11C (`+0x28FC` pour B, `+0x297E` pour F) : notes lues ? 🔶
- Vérifié 3 fois : B n° 25 (jour 20), F n° 8 = note d'Olimar trouvée à Formidable Oak (jour 21), F n° 4 = message de
  l'équipage à l'arrivée dans Formidable Oak (jour 24). → F = une catégorie de notes, pas les « étapes d'histoire ».
- Reste : le nom de chaque catégorie (ordre des onglets du GamePad).

## Zones : ce qu'on sait (2026-10-02)

- `OpenAreaFlag` = `état+0x909` (bit n = zone n), `SeenAreaFlag` = `état+0x90A`, et `état+0x90B` (sans nom connu,
  toujours égal à `SeenAreaFlag` dans les sauvegardes). Dans la sauvegarde, les trois octets sont au décalage `0x49A`
  de `singleN.sav` (après `UniteOnyon` en `0x499`).
- **Historique naturel** (sauvegardes de l'utilisateur, `backups/`) :

  | Jour | Ouvertes | Vues | `+0x90B` | Remarque |
  |---|---|---|---|---|
  | 2 | `0x03` | `0x05` | `0x05` | zone 2 « vue » avant d'être ouverte |
  | 3–7 | `0x03` | `0x07` | `0x07` | |
  | 8–14 | `0x07` | `0x07` | `0x07` | zone 2 ouverte au jour 8 |
  | 14 (forcé) | `0x0F` | `0x07` | `0x07` | zone 3 forcée le 2026-10-01 19:40 |
  | 15 | `0x0F` | `0x0F` | `0x0F` | après la pose en zone 3 |

- Forcer un bit ouvre la zone : elle apparaît sur la carte ✅ et le vaisseau s'y pose ✅ (zone 3, 2026-10-01).
- **Bits ↔ zones (tests du 2026-10-02, jours 15–19)** :

  | Bit | Zone | Comment on le sait |
  |---|---|---|
  | `0x01` | Tropical Wilds | 🔶 curseur de la carte (`état+0x590`) = 0 en y allant |
  | `0x02` | Garden of Hope | 🔶 par élimination |
  | `0x04` | Distant Tundra | ✅ zones 2–4 fermées (`0x03`) → absente de la carte du jour 19 |
  | `0x08` | **Twilight River** | ✅ bit fermé → zone absente de la carte ; rouvert → de retour |
  | `0x10` | **Formidable Oak** (5ᵉ zone) | ✅ bit forcé → zone sur la carte du jour 19 |

- **Règle de la carte ✅ : elle montre toutes les zones jusqu'à la plus haute ouverte.** `0x0B` (Distant Tundra
  éteinte, Twilight River allumée) → Distant Tundra reste visible et accessible ; `0x03` (2026-10-02 21:54, jour 18,
  gardé au jour 19) → **Distant Tundra disparaît**. Fermer des zones marche donc, **à condition de partir du haut**
  (Formidable Oak, puis Twilight River, puis Distant Tundra) — conclusion de l'utilisateur pour « Progressive Zone ».
- **Le jeu recalcule `OpenAreaFlag`** : à 21:08:46 (jour 17), en **sortant des Pikmin de l'Oignon**, il a réécrit
  `0x18` → `0x0F` (zones 0–2 rouvertes, zone 4 forcée effacée). Une seule copie de l'objet d'état en mémoire (fouille
  complète). Sans sortie de Pikmin, la valeur forcée tient jusqu'à la sauvegarde (jour 19 : `0x1B`).
  ✅ **Ce recalcul ne vient pas de l'histoire** : avec `0x03`, Pikmin sortis au jour 19 → rien de rouvert, `0x03`
  gardé dans `single19.sav` et `single20.sav` (2026-10-02 22:02). Le recalcul remplit seulement les zones situées
  sous la plus haute ouverte au chargement de la journée (`0x0B` au jour 17 → `0x0F`). → **Verrouiller des zones
  marche sans patch** (reste à voir ce que fait l'événement d'histoire qui ouvre une zone : le client devra la refermer).
- **Mur de Garden of Hope** (celui que Louie fait exploser dans l'histoire après l'avoir récupéré, en volant la
  nourriture et le canard en plastique d'Olimar) : **trouvé cassé au jour 20** (2026-10-03), alors que l'utilisateur
  n'a pas encore récupéré Louie. Les 5 zones avaient été ouvertes (`0x1F`) sur la carte juste avant de se poser
  (09:43 → pose 09:46) ; aucun changement suspect pendant la journée. Hypothèse de l'utilisateur 🔶 : ouvrir Formidable
  Oak (bit `0x10`) fait charger Garden of Hope « après Louie ». Pas de point de comparaison (mur pas regardé au jour 19).
  **Rechargements faits par l'utilisateur : jour 17 → mur debout, jour 18 → mur cassé.** Bits allumés entre
  `single17.sav` et `single18.sav` : `+0x264C` `0x08`, `+0x267B` `0x04`, `+0x268F` `0x20`, `+0x2A22` `0x08`,
  `+0x2B2B` `0x01` (la zone « histoire » est dans le fichier à `mémoire − 0x1789`). Formidable Oak avait été ouverte
  34 s ce jour-là (21:08:12–21:08:46). Test : forcer ces 5 bits au chargement du jour 17, puis réduire.
- **Formidable Oak en avance** (jour 21, `0x1F`, Louie et Olimar pas encore récupérés) : **le boss est là mais ne réagit
  pas** (pas de combat, invincible, figé ; dit par l'utilisateur). Une **note d'Olimar** ramassée sur place a allumé
  `état+0x2862` bit `0x01` (10:09:39, copie en `+0x297E`) : l'ensemble F n'est donc pas seulement « étapes
  d'histoire » (les notes d'Olimar vues avant allumaient l'ensemble D).
  L'utilisateur pense aussi qu'une fois cassé, le mur le reste → refermer Formidable Oak ne prouverait rien. Test qui
  tranche : recharger `backups/save_1012be00_2026-10-03_0943_avant_zones_1F_jour20` (début du jour 20, `0x03`) et
  regarder le mur à Garden of Hope (debout → c'est bien Formidable Oak).
- Autres champs : `état+0x590` = zone sous le curseur de la carte (u32), `+0x594` = zone de la dernière journée (?),
  **`état+0x98C` = dernier jour joué par zone** (5 × u32, -1 = jamais) → le jeu a bien 5 zones.
- Fruits pressés par bloc de 64 bits (`+0x5C`, 5 blocs, peut-être un par zone 🔶) : bloc 2 aux jours 3–8, bloc 4 aux
  jours 9–12, bloc 1 à partir du jour 13. À rapprocher des zones visitées ces jours-là.
- **Tests à faire** (outil : `py -3.13 beta/tools/beta_test.py zones` / `zone N on|off`, sauvegarde automatique) :
  1. ~~Nom de chaque bit~~ ✅ (voir le tableau ci-dessus ; 0–2 encore 🔶).
  2. ~~Fermer une zone déjà ouverte par l'histoire~~ → impossible par le bit seul : il faut le code du recalcul.
  3. ~~Bit 4 (`0x10`)~~ ✅ Formidable Oak. Reste : s'y poser avant l'histoire (le boss est-il là ?).
  4. `SeenAreaFlag` éteint pour une zone ouverte : animation « nouvelle zone » sur la carte ?
  5. Trouver le code qui recalcule `OpenAreaFlag` (sortie de Pikmin de l'Oignon) et celui qui affiche la carte.

## Analyse du code (2026-10-01)

- **Drapeaux à `état+0xA4`** : en fait **64 drapeaux** (2 mots big-endian `état+0xA4` et `état+0xA8`), gérés par
  les méthodes virtuelles `0x02FDA064` (lecture) / `0x02FDA08C` (écriture) de l'objet de partie (table `0x1033C26C`,
  pointeur de table à `GameData+0x2AE0`) : drapeau n° *i* = bit `i & 31` du mot `i >> 5`. Rouge = 27, ailé = 28
  (test), jaune = 29, ? = 30 (test 2, « blanc » d'après l'utilisateur), roc = 31 → **bleu = 32 ou 33 ?** (mot `+0xA8`).
  Même mécanisme pour 64 autres drapeaux à `état+0x9C` (`0x02FD9FA4` / `0x02FD9FCC`), tous à 0 au jour 13.
- **Paramètres de partie nommés** (« SingleGameParams », noms en `0x1033F40C`–`0x1033F5C0`, sauvegarde en
  `0x0300A2xx`–`0x0300ACxx`, base `r27 = état+0x14` déduite de `DopingNum` = sprays `état+0x598`) :
  - `UniteOnyon` = **`état+0x908`** (u8) = **Oignons fusionnés** (`0xA8` = rouge, jaune, roc, même codage que `+0xA4`).
    Un Oignon « découvert » (`+0xA4`) mais pas « fusionné » (`+0x908`) déclenche la scène de fusion à l'atterrissage.
  - `OpenAreaFlag` = **`état+0x909`** (u8) = **zones ouvertes** : `0x07` au jour 13 (3 zones, bits 0–2).
  - `SeenAreaFlag` = **`état+0x90A`** (u8) = zones déjà vues : `0x07`.
  - Autres noms : `SelectedAreaID`, `CourseInAreaID`, `TsuyuNum`, `StolenEnergy`, `DivFruitsNum`, `KeyItemBirth`,
    `LastProgress`, `EventFlag`, `DrcButtonOpenFlag`, `PlayerJoinFlag`, `HasSubItem`, `StolenFridge`, `Fridge`,
    `FruitsCIDByGetOrder`, `FruitsNumGotByCID`, `DopingNum` (décalages à relever de la même façon).

## Journal des confirmations

- **2026-10-01 19:40:51, test de zone** (sauvegarde avant : `backups/save_1012be00_2026-10-01_1940_avant_zone`,
  jour 13) : `OpenAreaFlag` `0x07` → `0x0F` (4ᵉ zone ouverte), `SeenAreaFlag` laissé à `0x07`.
  **Résultat ✅ : la nouvelle zone apparaît sur la carte du vaisseau** (vu par l'utilisateur).
- **2026-10-01 19:43–19:57, Oignons découverts + fusionnés** (`état+0xA4` et `état+0x908` forcés ensemble, plus
  10 Pikmin dans l'emplacement) : la colonne apparaît **tout de suite** dans le menu de l'Oignon (sans atterrissage
  ni scène de fusion).
  - bit `0x10` / emplacement 1 → l'utilisateur voit des Pikmin **bleus** ;
  - bit `0x40` / emplacement 3 → Pikmin **roses (ailés)** (confirmé par l'utilisateur).
  → **Correspondance d'origine confirmée : emplacement 1 = bleu, emplacement 3 = ailé.** Les observations du
  test du matin (rose en emplacement 1) venaient sans doute d'un affichage trompeur pendant la scène de fusion.
  Sauvegardes : `backups/save_1012be00_2026-10-01_1958_test_rose` + image mémoire `beta/memoire/etat_2026-10-01_195820.bin`.
  - **20:02:08 ✅ : les 10 Pikmin ailés sortent de l'Oignon** (menu : 0 dans l'Oignon, 10 sur le terrain) et sont
    dans l'équipe au jour 14 (capture 20:02:30), **sans plantage**. → Avec « découvert » **et** « fusionné »
    (`+0xA4` et `+0x908`), un type de Pikmin pas encore débloqué par l'histoire devient utilisable. Le plantage du
    matin venait d'un Oignon découvert mais pas fusionné (scène de fusion avec le mauvais Oignon).
  - Jeu arrêté à la main par l'utilisateur à 20:04:29 (pas un plantage).
  - **Confirmé par l'utilisateur ✅** : le vaisseau **se pose dans la nouvelle zone** ; les **Pikmin ailés se comportent
    normalement** ; et l'**Oignon ailé « seul »** (celui que l'histoire place dans la zone avant sa fusion) **n'apparaît
    plus sur le terrain**, puisque le jeu le sait déjà fusionné → pas de conflit avec l'histoire.
  - À faire : même test avec les **bleus** (bit `0x10`, découvert + fusionné, 10 Pikmin dans l'emplacement 1).

*(une ligne par découverte : date, ce qui a été fait en jeu, ce que montre le journal, conclusion)*

- **2026-10-01, test « donner les Pikmin bleus »** (sauvegarde avant test :
  `backups/save_1012be00_2026-10-01_1855_avant_bleus`, début du jour 13).
  - 18:55 : +10 feuilles dans l'emplacement 1 (`état+0xFC`), bit `0x10` éteint → **rien de visible** en jeu.
  - 18:57 : bit `0x10` de `état+0xA4` allumé en pleine journée → **rien de visible** (pas d'Oignon, rien au menu).
  - 19:02–19:03 : « Recommencer la journée » : le menu de choix du jour **réécrit l'objet d'état avec l'aperçu de
    chaque jour** (jours 1 à 13 défilent) → une écriture faite à ce moment-là est perdue.
  - 19:03:59 : bit `0x10` + 10 feuilles réécrits **pendant le chargement du jour 13** (terrain = 0) → ça tient.
    À l'atterrissage, **scène de fusion d'Oignon, mais c'est l'Oignon jaune qui fusionne** (vu par l'utilisateur).
    En mémoire, nouveau mot **`état+0xC8` : 0 → 1** ; les mots voisins `+0xC0` = 2 (apparu avec les rocs) et
    `+0xC4` = 1 (apparu avec le jaune) → probablement une **liste des Oignons fusionnés** (à comprendre).
  - 19:04:40 : fin de journée → jour 14, le bit `0x10` et les 10 Pikmin de l'emplacement 1 sont toujours là.
  - `single14.sav` (sauvegarde du jour 14) contient bien `0xB8` et la nouvelle entrée de fusion (`+0xC8` = 1).
  - 19:19 : sur le terrain du jour 14, « il se passe un truc bizarre » puis **le jeu plante** (19:19:52, ~30 s après
    l'atterrissage). Sauvegarde qui plante gardée dans `backups/save_1012be00_2026-10-01_1920_plantage_jour14_oignon_bleu`.
  - **Conclusion ❌** : allumer le bit d'un Oignon pas encore trouvé dans l'histoire **fait planter le jeu** (le jeu
    croit avoir l'Oignon mais il n'existe pas encore). → Pas d'item « Oignon » par écriture de ce bit ; les items
    « Extra Blue/Winged Pikmin » ne doivent viser qu'un Oignon déjà découvert (c'est déjà le cas : repli sur le rouge).
    Le client ne doit **jamais** écrire `état+0xA4`.
  - **Rejeu du jour 14 filmé** (captures chaque seconde + mémoire, `crash_record/` du chat BÊTA) :
    19:23:55, menu « Call or Return Pikmin » : **4ᵉ colonne avec nos 10 Pikmin** ; 19:24:05, icônes **roses à ailes**
    → **l'emplacement 1 / bit `0x10` = Pikmin AILÉS** (pas bleus) 🔶 ; par élimination l'emplacement 3 / bit `0x40`
    serait les **bleus** ❓. 19:24:13 : « OK » pour sortir 1 Pikmin ailé → **plantage au moment où il doit apparaître**
    (le jeu n'a pas chargé les Pikmin ailés, qui ne sont pas encore débloqués dans l'histoire).
