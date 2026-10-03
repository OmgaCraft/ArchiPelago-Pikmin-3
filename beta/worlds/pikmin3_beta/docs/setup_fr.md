# Guide d'installation de Pikmin 3 Beta (Cemu)

## Logiciels nécessaires

- [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases) 0.6.7 ou plus récent
- [Cemu](https://cemu.info/) 2.6 ou plus récent, sous **Windows**
- **Pikmin 3 (Europe)**, version 1 (version du disque, **sans mise à jour**), copié depuis ta propre Wii U
- Le fichier `pikmin3_beta.apworld`

## Installation

1. Double-clique sur `pikmin3_beta.apworld` (ou *Install APWorld* dans le lanceur Archipelago).
   Il peut rester installé à côté de `pikmin3.apworld` (version finale) : ce sont deux jeux différents.
2. Ouvre le **Pikmin 3 Beta Client** depuis le lanceur et tape `/install_pack`.
3. Dans Cemu : clic droit sur Pikmin 3 > *Modifier les graphic packs*, coche **Pikmin 3 > Mods > Archipelago Beta**
   et **décoche Pikmin 3 > Mods > Archipelago** (les deux modifient le même code du jeu).
4. **Sauvegarde ta partie** (`mlc01\usr\save\00050000\1012be00`).

## Jouer

1. Lance Pikmin 3 dans Cemu et charge ta partie en mode **Histoire**.
2. Lance le Pikmin 3 Beta Client et connecte-toi au serveur.
3. Commandes : `/cemu`, `/state`, `/resync_day`, et pour la bêta `/note <texte>` (ce que tu viens de faire) et
   `/decouvertes` (derniers changements en mémoire). Le journal des découvertes marche aussi sans serveur.

Le journal complet est écrit dans `Archipelago\logs\Pikmin3Beta_decouvertes.txt`.
