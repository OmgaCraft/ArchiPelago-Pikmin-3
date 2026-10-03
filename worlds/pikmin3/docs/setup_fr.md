# Guide d'installation de Pikmin 3 (Cemu)

## Logiciels nécessaires

- [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases) 0.6.7 ou plus récent
- [Cemu](https://cemu.info/) 2.6 ou plus récent, sous **Windows**
- **Pikmin 3 (Europe)**, version 1 (version du disque, **sans mise à jour**), copié depuis ta propre Wii U
- Le fichier `pikmin3.apworld`

Les autres versions (USA, Japon, mise à jour 2.0.0, Pikmin 3 Deluxe) ne sont pas encore prises en charge : le code du
jeu est modifié à des adresses fixes qui ne correspondent qu'à l'exécutable européen v1.

## Installation

1. Double-clique sur `pikmin3.apworld` (ou utilise *Install APWorld* dans le lanceur Archipelago).
2. Ouvre le **Pikmin 3 Client** depuis le lanceur Archipelago et tape `/install_pack`.
   Le graphic pack *Archipelago* est copié dans `%APPDATA%\Cemu\graphicPacks\Pikmin3_Archipelago`.
   Si ton dossier de données Cemu est ailleurs, indique-le : `/install_pack D:\Cemu`.
3. Dans Cemu : clic droit sur Pikmin 3 > *Modifier les graphic packs*, puis active
   **Pikmin 3 > Mods > Archipelago**. Désactive tout autre mod qui modifie la limite de Pikmin ou le jus des fruits.
4. **Sauvegarde ta partie** (`mlc01\usr\save\00050000\1012be00`) avant ta première session Archipelago.

Le graphic pack ne fait rien tout seul : sans le client, le jeu se comporte normalement.

## Créer ton fichier d'options

Utilise la [page d'options du joueur](../player-options) pour créer ton fichier YAML, ou génère un modèle depuis le
lanceur (*Generate Template Options*).

## Jouer

1. Lance Pikmin 3 dans Cemu et charge ta partie en mode **Histoire** (les modes Mission et Bingo sont ignorés).
2. Lance le Pikmin 3 Client et connecte-toi au serveur (`/connect adresse:port`, puis ton nom de slot).
3. Le client trouve Cemu tout seul. `/cemu` affiche l'état de la connexion, `/state` ce que le client lit.

### Ce qui change dans le jeu

- Presser un fruit envoie un check mais **ne donne pas de jus**. Le jus arrive par les items « fruit » reçus.
- Avec *Progressive Pikmin Limit*, la limite de Pikmin sur le terrain commence basse et augmente à chaque item
  « Progressive Pikmin Limit ».
- Le *mode jus* te protège de la panne de jus : `safe` garde au moins 2 bouteilles, `no_consumption` rend la
  bouteille bue chaque nuit, `normal` ne change rien (tu peux perdre la partie).
- Objectif par défaut : battre le boss final de Formidable Oak **et** presser le nombre de fruits demandé.
- Avec *Progressive Zones*, tu commences avec Tropical Wilds et Garden of Hope ; chaque item « Progressive Zone »
  ouvre la zone suivante (Distant Tundra, Twilight River, Formidable Oak). Le client referme une zone que
  l'histoire ouvrirait trop tôt.
- Avec *Progressive Pikmin* (désactivé par défaut), 4 items débloquent les Pikmin roc, jaunes, ailés et bleus, à la
  fin de la journée où l'item arrive.

### Recharger un jour

Les items donnés pendant un jour sont perdus si tu recharges ce jour. Le client détecte quand le jeu a été relancé ou
quand tu reviens à un jour précédent, et redonne ces items. Si tu as rechargé un jour sans relancer le jeu (par exemple
*Recommencer la journée* depuis le menu pause), tape `/resync_day` une fois revenu sur la planète.

## Limites connues (version 1.0)

- Seule la version européenne v1 est prise en charge.
- Zones progressives et Progressive Pikmin (expérimentaux) : pas encore essayés dans une vraie partie avec le client.
- Objectif « boss final » : le boss ne se bat qu'une fois l'histoire assez avancée (après le sauvetage de Louie).
- La logique « check ↔ zone » est déduite d'une partie réelle (prudente, pas encore exacte).
- Pas encore de death link ni de checks du mode Mission.
