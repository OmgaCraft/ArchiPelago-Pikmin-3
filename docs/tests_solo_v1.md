# Tests en solo de la V1 (avant la bêta multiworld)

Outil : [tools/solo_test.py](../tools/solo_test.py). Il utilise le code du client
(`worlds/pikmin3/client/game_interface.py`), donc chaque test valide ce que fera le vrai client.

## Préparation

1. Sauvegarde de la partie (copie de `%APPDATA%\Cemu\mlc01\usr\save\00050000\1012be00` dans `backups/`).
2. Cemu : seul le pack **Mods > Archipelago** actif. Pikmin 3 Client **fermé** (il écrirait les mêmes valeurs).
3. Surveillance : `py -3.13 tools/solo_test.py watch` (affiche chaque changement de jour, jus, fruits, Oignons,
   objets, notes, population).

## Tests

| # | Test | Action | Résultat attendu | Statut |
|---|---|---|---|---|
| 1 | Limite de Pikmin | `limit 30`, sortir un maximum de Pikmin ; puis `limit 40` | Terrain bloqué à 30 puis 40 | ✅ 2026-09-29 |
| 2 | Oignon bleu | Le découvrir en jeu | `watch` : nouveau bit dans « Oignons découverts » (supposé `0x10`, emplacement 1) | |
| 3 | Oignon ailé (rose) | Le découvrir en jeu | Nouveau bit (supposé `0x40`, emplacement 3) | |
| 4 | Extra Red Pikmin (journée) | `pikmin 5` sur la planète | Menu de l'Oignon rouge : +5 tout de suite ; toujours là au jour suivant | ✅ jour 11 : +5 visibles, puis `set` 99 rouges / 100 rocs → bilan 100/100/100, conservés après la sauvegarde du jour 12 |
| 5 | Extra Red Pikmin (fin de journée) | `pikmin 5` pendant le bilan du jour | +5 conservés au jour suivant | |
| 6 | Fruits sans jus (pack final) | `nojuice on`, presser un fruit le soir | Jus inchangé au pressage (seule la bouteille de la nuit part) ; bit du fruit allumé (+1 fruit pressé) | |
| 7 | Item fruit | `juice 1.5` pendant la journée | Jus +1,5 à l'écran ; conservé après la nuit | |
| 8 | Piège | `juice -0.5` | Jus −0,5 (jamais sous 1) | |
| 9 | Spray | `spray 1` | +1 spray ultra-épicé, utilisable | |
| 10 | Compte des fruits | `status` le soir | « fruits pressés » = nombre de fruits pressés affiché par le jeu (13 attendu au jour 11 ; « types » = sortes différentes) | ✅ jour 11 : « ×14 » = 14 bits. ❌→✅ jour 12 : « ×15 » mais 14 lus (Pocked Airhead en `+0x66`, hors zone lue) → zone corrigée en `+0x5C`–`+0x83`, revérifiée sur les sauvegardes des jours 2 à 13. ✅ jour 17 : 1 fruit + 2 moitiés de kiwi → 20 → 22 (un fruit en morceaux compte une fois, complet) |
| 11 | Graines, terrain plein | `limit 30`, terrain plein, ramener une pastille ou un ennemi | Les graines restent dans l'Oignon | |
| 12 | Relance du jeu | Donner un item, quitter sans finir la journée, recharger | Item perdu (normal) : c'est ce que le client redonne tout seul | |

Remettre à la fin : `nojuice off` et `limit 100` (sinon le jeu reste modifié tant qu'il tourne).

## Notes

- Hors jeu : le début de `singleN.sav` (sauvegarde du début du jour N) reprend l'objet d'état à partir de
  `état+0x40` (octet 0 du fichier = `état+0x40`), au moins jusqu'à `+0xA4` (jour, jus, sortes, objets, fruits,
  Oignons découverts). Plus loin la disposition diffère (Pikmin des Oignons ailleurs). Script de revérification :
  scratchpad `verify_saves.py` (rejoue `read_snapshot` du client sur chaque jour).
- Notes de tutoriel : le client ne lit que l'ensemble B (`état+0x27E0`), mais « Pikmin-ology #7 » (jour 12) s'est
  rangé dans l'ensemble A (`état+0x27C0`) et la scène des Pellet Posies dans l'ensemble C (`état+0x2800`).
  À trancher avec les nombres affichés sur le GamePad (checks de notes désactivés par défaut en attendant).

- Le pointeur des Pikmin sur le terrain vaut 0 hors du terrain (vaisseau, bilan) : la population ne compte
  alors que les Oignons. Normal.
- Bit `0x08` des objets importants présent dès le départ : rôle inconnu, non utilisé comme check.
