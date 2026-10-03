# Guide — Pikmin 3 Archipelago BÊTA (v0.1.0)

La bêta est un **jeu à part** dans Archipelago (« Pikmin 3 Beta »), séparé de la version finale (« Pikmin 3 »).
Elle contient tout ce que contient la version finale, plus des checks et des items **pas encore vérifiés**, et un
**journal des découvertes** qui note tout ce qui change dans la mémoire du jeu pendant que tu joues. Le but :
confirmer les données manquantes (Oignons bleu et ailé, notes…) et trouver de nouveaux items et checks.

## Ce qu'il te faut

| Élément | Détail |
|---|---|
| Archipelago | 0.6.7 (testé), Windows |
| Cemu | 2.6 ou plus récent |
| Jeu | Ta copie de **Pikmin 3 (Europe)**, version du disque (**v1, sans mise à jour ni DLC**) |

## Installation

1. Décompresse `Pikmin_3_Archipelago_Beta.zip` (dossier [`dist/`](dist)).
2. **APWorld** : double-clique sur `pikmin3_beta.apworld` (ou Launcher > « Install APWorld »). Il peut rester
   installé à côté de `pikmin3.apworld` : ce sont deux jeux différents.
3. **Graphic pack** : Launcher > **Pikmin 3 Beta Client**, puis `/install_pack`.
4. **Dans Cemu** : coche **Pikmin 3 > Mods > Archipelago Beta** et **décoche Pikmin 3 > Mods > Archipelago**
   (version finale). Les deux modifient le même code du jeu : un seul à la fois. Le client te prévient si les
   deux sont cochés.
5. **Sauvegarde ta partie** : copie `%APPDATA%\Cemu\mlc01\usr\save\00050000\1012be00` ailleurs.

## Jouer

1. **YAML** : copie `Pikmin 3 Beta.yaml` dans `C:\ProgramData\Archipelago\Players` et change `name`.
2. **Générer**, **héberger**, puis lance Pikmin 3 (mode Histoire) et le **Pikmin 3 Beta Client**.

### Commandes du client

| Commande | Effet |
|---|---|
| `/cemu` | État de la connexion à Cemu |
| `/state` | Jour, jus, fruits, sortes, population, Oignons, objets, notes par ensemble, étapes d'histoire, sprays, baies |
| `/install_pack` | (Ré)installe le graphic pack bêta dans Cemu |
| `/resync_day` | Redonne les items reçus depuis le début du jour en cours |
| `/checks` | **Bêta** : résumé de ce qui est accompli (fruits, Oignons, objets, notes par type, étapes d'histoire) |
| `/note <texte>` | **Bêta** : décrit ce que tu viens de faire (« Oignon bleu trouvé »). La note accompagne les découvertes des 3 minutes suivantes |
| `/decouvertes [n]` | **Bêta** : affiche les n derniers changements repérés en mémoire |

## La console des checks

Une ligne par check accompli, en français, au moment où ça arrive :

```
✔ Note « Pikmin-ology » obtenue (ensemble A, n°21) → check « Notes A #21 »
✔ Oignon bleu découvert (bit vu seulement en le forçant 🔶) → check « Discover Blue Onion »
✔ Fruit pressé (n°16) → check « Fruit 16 »
✔ Jour 14 atteint → check « Reach Day 14 »
• Spray ultra-épicé obtenu (total 1)
```

Deux façons de l'avoir :
- **Dans le Pikmin 3 Beta Client** : onglet **« Checks »** de la fenêtre. Connecté, chaque ligne dit si c'est un check
  de ta partie (« → check « … » ») ou non (« pas un check de cette partie ») ; hors connexion, elle s'affiche quand même.
- **Sans Archipelago** : double-clic sur **`beta/Console des checks.bat`** (fenêtre à part, il faut juste Cemu et le
  jeu). Une copie est gardée dans `beta/logs/checks_AAAA-MM-JJ.txt`.

Types de notes : « Pikmin-ology » (ensemble A), « Tutoriel » (B), « Document / scène » (C) — noms provisoires, à
confirmer —, et « Olimar » (D, vérifié).

## Le journal des découvertes

- Il tourne dès que le client voit ta partie, **même sans serveur Archipelago** : tu peux juste lancer le client
  pendant une partie normale.
- Chaque changement est écrit dans `C:\ProgramData\Archipelago\logs\Pikmin3Beta_decouvertes.txt` avec l'heure, le
  jour, la zone mémoire, les bits allumés ou éteints, le sens connu (✅ / 🔶 / ❓) et ta dernière note.
- Les valeurs qui bougent sans cesse (minuteurs…) sont écartées automatiquement.
- Le plus utile : taper `/note …` **juste avant** ou **juste après** un événement (nouvel Oignon, nouvelle zone,
  boss, objet). Ensuite, envoie le fichier du journal pour qu'on l'analyse ([DECOUVERTES.md](DECOUVERTES.md)).

## Ce qui est en plus par rapport à la version finale

| Ajout | Détail | Statut |
|---|---|---|
| Checks « Reach Day N » | atteindre le jour 2… `day_check_max` | ✅ lecture vérifiée |
| Checks « Fruit Kind N » | chaque nouvelle sorte de fruit (30) | ✅ lecture vérifiée |
| Checks « Notes A/B/C #N », « Olimar Note N » | un compteur par ensemble de notes du GamePad | 🔶 sens des ensembles A/B/C à confirmer |
| Checks « Story Event N » | étapes d'histoire (Data Glutton, Charlie…) | 🔶 2 étapes observées |
| Checks Oignon bleu / ailé | bleu = bit `0x04`, ailé = bit `0x40` (trouvés en les forçant) | 🔶 découverte naturelle pas encore observée |
| Items Extra Yellow / Rock Pikmin | +5 dans l'Oignon jaune / roc | 🔶 (même mécanisme que les rouges, vérifié) |
| Items Extra Blue / Winged Pikmin | +5 dans l'Oignon bleu / ailé, en rouges tant qu'il n'est pas découvert | 🔶 Pikmin bleus et ailés sortis sans problème |
| Item Ultra-Spicy Berry | +1 baie ultra-épicée | ❓ |
| Journal des découvertes | `/note`, `/decouvertes`, fichier texte | nouveau |
| Console des checks | onglet « Checks » du client, `/checks`, ou `Console des checks.bat` sans Archipelago | nouveau |

## Si ça coince

- `Graphic pack Archipelago Beta inactif` : coche le pack bêta (et pas le pack final), puis relance le jeu.
- Journal du client : `C:\ProgramData\Archipelago\logs\Pikmin3BetaClient.txt` ; journal des découvertes :
  `Pikmin3Beta_decouvertes.txt` dans le même dossier.
