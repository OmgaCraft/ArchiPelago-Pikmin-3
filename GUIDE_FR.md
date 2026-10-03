# Guide — Pikmin 3 Archipelago (V1, version 1.0.0)

## Ce qu'il te faut

| Élément | Détail |
|---|---|
| Archipelago | 0.6.7 (testé), Windows |
| Cemu | 2.6 ou plus récent (testé avec 2.6) |
| Jeu | Ta propre copie de **Pikmin 3 (Europe)**, version du disque (**v1, sans mise à jour ni DLC**), TitleId `000500001012BE00` |

- Le jeu est modifié à des adresses fixes relevées sur cette version précise (module `carrot`, somme `0x838BE11A`).
  **USA, Japon, mise à jour 2.0.0, Pikmin 3 Deluxe : non pris en charge.**
- Le jeu original n'est jamais modifié : tout passe par un *graphic pack* de Cemu, activable et désactivable.

## Installation

1. Décompresse `Pikmin_3_Archipelago.zip` (dossier [`dist/`](dist)).
2. **APWorld** : double-clique sur `pikmin3.apworld`, ou Launcher Archipelago > « Install APWorld ».
   Tu peux aussi le copier à la main dans `C:\ProgramData\Archipelago\custom_worlds\`.
3. **Graphic pack** : Launcher > **Pikmin 3 Client**, puis tape `/install_pack`.
   Le pack est copié dans `%APPDATA%\Cemu\graphicPacks\Pikmin3_Archipelago`
   (autre dossier Cemu : `/install_pack D:\chemin\vers\Cemu`).
4. **Dans Cemu** : clic droit sur Pikmin 3 > *Edit graphic packs*, coche **Pikmin 3 > Mods > Archipelago**.
   Décoche tout autre mod qui touche à la limite de Pikmin ou au jus (ex. « No Limits », le pack « Archipelago Beta »).
5. **Sauvegarde ta partie** : copie `%APPDATA%\Cemu\mlc01\usr\save\00050000\1012be00` ailleurs.

Le pack seul ne fait rien : sans le client connecté, le jeu se comporte normalement.

## Jouer

1. **YAML** : copie `Pikmin 3.yaml` dans `C:\ProgramData\Archipelago\Players` et change `name`
   (un nom différent de ceux des autres fichiers de la partie).
2. **Générer** : lance `ArchipelagoGenerate.exe` (ou Launcher > Generate). La partie arrive dans
   `C:\ProgramData\Archipelago\output`.
3. **Héberger** : dépose le `.zip` sur [archipelago.gg](https://archipelago.gg/uploads), ou lance `ArchipelagoServer.exe`.
4. **Cemu** : lance Pikmin 3 et charge ta partie en mode **Histoire** (Mission et Bingo sont ignorés).
   Une **nouvelle partie** est conseillée : avec une partie commencée, tout ce qui est déjà fait part d'un coup.
5. **Client** : Launcher > **Pikmin 3 Client**, entre l'adresse du serveur, puis ton nom de slot.
   Le client trouve Cemu tout seul (message `Cemu : connecté` puis `Graphic pack Archipelago détecté`).

Les objets reçus arrivent dès que tu es dans une partie Histoire, jamais au menu.

### Commandes du client

| Commande | Effet |
|---|---|
| `/cemu` | État de la connexion à Cemu |
| `/state` | Ce que le client lit : jour, jus, fruits, population, notes, zones, boss, limite de Pikmin, items donnés |
| `/install_pack` | (Ré)installe le graphic pack dans Cemu |
| `/resync_day` | Redonne les items reçus depuis le début du jour en cours (voir plus bas) |

## Ce qui change en jeu

- **Objectif** (`goal`) : par défaut `final_boss` = battre le boss final de Formidable Oak **et** avoir pressé
  `fruits_required` fruits. Autres choix : `fruits` (seulement les fruits) ou `population`. Le boss final ne se bat
  qu'une fois l'histoire assez avancée (après le sauvetage de Louie et la scène « Olimar et le boss »).
- **Presser un fruit envoie un check mais ne donne plus de jus.** Le jus arrive par les items : chaque
  item porte le nom d'un fruit de Pikmin 3 et donne son jus (ex. Face Wrinkler = 1,5 bouteille).
- **Limite de Pikmin progressive** : au départ 30 Pikmin max sur le terrain (pousses comprises), +10 par
  item « Progressive Pikmin Limit », jusqu'à 100. L'Oignon refuse d'en sortir davantage.
- **Zones progressives** (expérimental, `progressive_zones`) : tu commences avec Tropical Wilds et Garden of Hope ;
  chaque item « Progressive Zone » ouvre la suivante sur la carte du vaisseau : Distant Tundra, Twilight River, puis
  Formidable Oak (zone du boss final). Si l'histoire ouvre une zone trop tôt, le client la referme jusqu'à l'item.
- **Progressive Pikmin** (expérimental, désactivé par défaut, `progressive_pikmin`) : 4 items qui débloquent les
  Pikmin roc, jaunes, ailés puis bleus. Le type arrive **à la fin de la journée** où l'item est reçu (plus tôt, le jeu
  plante) ; son Oignon est vide mais donne une pousse le lendemain. L'histoire débloque aussi les types : ces items
  font gagner du temps, sans être exigés par la logique (et les checks « Discover … Onion » sont alors retirés).
- **Mode jus** (`juice_mode`) : `safe` garde toujours au moins 2 bouteilles, `no_consumption` rend la
  bouteille bue chaque nuit, `normal` ne t'aide pas (panne de jus = fin de partie).
- **Checks** :
  - chaque fruit pressé (Fruit 1, Fruit 2… dans l'ordre ; un fruit en morceaux compte quand il est complet) ;
  - les Oignons découverts (bleu, jaune, ailé, roc) ;
  - les objets importants (Data Glutton, Anti-Electrifier, Metal Suit Z, Dodge Whistle) et le sauvetage de Louie ;
  - les paliers de population ;
  - les notes du GamePad : « Tutorial Note N » (notes de conseils, Pikmin-ology comprise ; beaucoup arrivent toutes
    seules au fil de l'histoire) et « Olimar Note N » ;
  - en option, les Secret Memos (`secret_memo_count`).
- **Remplissage** : Juice Drop (+0,5 bouteille), Extra Red Pikmin (+5 dans l'Oignon rouge),
  Ultra-Spicy Spray (+1 spray). Piège (option) : Juice Leak Trap (−0,5 bouteille, jamais sous 1).

### Logique

La liste exacte « check ↔ zone » n'est pas encore connue : chaque check demande un nombre d'items « Progressive
Zone » et de limite de Pikmin déduit d'une vraie partie (jour où il a été obtenu et zones ouvertes ce jour-là).
C'est prudent : un check fait avec peu de zones ne demande jamais plus.

### Recharger un jour

Les items donnés pendant une journée sont perdus si tu recharges ce jour. Le client s'en rend compte
quand le jeu a été relancé ou quand tu reviens à un jour précédent, et redonne ces items tout seul.
Si tu as fait *Recommencer la journée* depuis le menu pause (jeu non relancé), tape `/resync_day`
une fois revenu sur la planète.

## État de la V1

| Fonction | Statut |
|---|---|
| Lecture de la partie (jour, jus, fruits, Oignons, population, objets, notes) | ✅ vérifié en jeu |
| Nombre de fruits pressés (checks « Fruit N », fruits en morceaux compris) | ✅ vérifié en jeu (×14, ×15, ×20, ×22, ×28, ×32) |
| Notes : catégories du GamePad (conseils A/B/C, Olimar D/F, Secret Memos G) | ✅ vérifié en jeu (règle du badge du GamePad) |
| Objets importants, Louie | ✅ vérifié en jeu (Data Glutton 🔶) |
| Limite de Pikmin pilotée par la boîte aux lettres (30 → 40 en direct) | ✅ vérifié en jeu |
| Extra Red Pikmin donné en pleine journée | ✅ vérifié en jeu (visible, compté au bilan, conservé après la sauvegarde) |
| Zones : ouvrir / refermer (carte du vaisseau), ouverture par l'histoire | ✅ vérifié en jeu ; 🔶 refermeture par le client pas encore essayée en partie |
| Objectif « boss final » | ✅ drapeau de victoire vérifié dans la sauvegarde d'après la fin |
| Types de Pikmin débloqués (découvert + fusionné, la veille) | ✅ vérifié en jeu (ailés, bleus) ; 🔶 par le client pas encore essayé |
| Fruits sans jus | ✅ vérifié avec le pack de test ; 🔶 pack final pas encore essayé en partie |
| Items jus, piège, spray | 🔶 écritures vérifiées, effet en partie à confirmer |
| Partie complète avec le client et un serveur | 🔶 première vraie partie à faire |
| Death link, mode Mission | ❌ pas encore |

## Si ça coince

- `Cemu introuvable` : lance Cemu **et** le jeu avant (ou après) le client, il réessaie toutes les 5 s.
- `Graphic pack Archipelago inactif` : active le pack dans Cemu puis relance le jeu.
- Journal du client : `C:\ProgramData\Archipelago\logs\Pikmin3Client.txt` (à joindre pour un rapport de bug,
  avec le résultat de `/state`).
