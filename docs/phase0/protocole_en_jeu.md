# Phase 0 — Marche à suivre en jeu

Objectif : trouver les premières adresses mémoire et vérifier qu'elles restent valables.
Toutes les commandes se lancent depuis le dossier du projet, **Cemu ouvert et le jeu lancé** :

```
py -3.13 tools/memory_probe.py <commande>
```

Les adresses affichées et saisies sont des adresses **Wii U** (ex. `0x1234ABCD`) :
l'outil ajoute lui-même la base de Cemu, qui change à chaque lancement.

> **Avant toute écriture en mémoire**, sauvegarde le dossier de sauvegarde du jeu (version EUR) :
> `%APPDATA%\Cemu\mlc01\usr\save\00050000\1012be00`

---

## Étape 0 — Relevés simples
1. Dans la liste des jeux de Cemu, vérifie que le **Title ID** est bien `000500001012BE00` (EUR)
   et note la **Version**.
2. Lance une nouvelle partie et joue jusqu'à diriger un capitaine avec quelques Pikmin.
3. Lance `info` puis `ranges` et garde le résultat. De nouvelles plages doivent
   apparaître par rapport à Cemu sans jeu (code du jeu, MEM2…).
4. Dis-moi quand le jeu a tourné une fois : je chercherai le fichier de log de Cemu
   pour la somme de contrôle du RPX.

## Étape 1 — Compteur de Pikmin (valeur exacte affichée)
1. Note le nombre de Pikmin affiché, par exemple 12.
2. `find 12 --type u32`
   (si 0 résultat : recommence avec `--type u16`, puis `--type u8`).
3. Change ce nombre en jeu (arrache ou lance un Pikmin), attends qu'il soit stable,
   puis `refine <nouveau nombre>`.
4. Répète l'étape 3 jusqu'à avoir moins d'une dizaine d'adresses.
5. Confirme en direct : `watch 0x<adresse> --type u32`.
   Plusieurs adresses peuvent rester (équipe, terrain, total, par type) : garde-les toutes.

## Étape 2 — Stabilité d'une adresse
Pour chaque adresse trouvée, refais `read 0x<adresse> --type <type>` après :
- un changement de zone ;
- une fin de journée ;
- un retour au titre puis le rechargement de la sauvegarde ;
- un redémarrage complet de Cemu.

Si l'adresse ne tient pas, il faut une chaîne de pointeurs :
`findptr 0x<adresse>` liste les valeurs qui pointent vers elle (ou juste avant).
On compare ces listes entre deux lancements pour trouver un pointeur fixe.

## Étape 3 — Jus
Le format du jus est inconnu (bouteilles en nombre flottant ? entier multiplié ?).
- Essaie d'abord `find` avec la valeur affichée : en `f32` (ex. `find 2.5 --type f32`),
  puis en entier ×10 ou ×2.
- Si rien ne marche, il faudra une recherche de valeur inconnue (augmente / diminue),
  que cet outil ne sait pas faire sur toute la mémoire. Utiliser alors le Memory Searcher
  intégré à Cemu (menu Outils), ou Cheat Engine avec des types big-endian et l'option
  MEM_MAPPED cochée dans les paramètres de recherche.

## Étape 4 — Flag d'un fruit collecté
Une fois le jus ou le compteur de jours trouvé, les données de sauvegarde sont
probablement à côté. On prend trois photos d'une zone autour de cette adresse
(ex. 0x20000 octets avant et après) :
1. `snapshot avant 0x<adresse - 0x20000> 0x40000` juste avant de ramener un fruit au vaisseau ;
2. `snapshot repos 0x<même adresse> 0x40000` quelques secondes plus tard, **sans rien faire** ;
3. ramène le fruit, puis `snapshot apres 0x<même adresse> 0x40000` ;
4. `diff avant apres --type u8 --noise repos` : seules les valeurs modifiées par le fruit restent.

Recommence avec un deuxième fruit pour confirmer le motif (un bit ou un octet par fruit ?).

---

## Ce que tu me renvoies
- Title ID et Version.
- La sortie de `info` et de `ranges`.
- Pour chaque adresse : ce qu'elle représente, son type, ses valeurs observées,
  et le résultat de chaque test de stabilité.

Tu peux coller les sorties telles quelles : je complèterai `findings.md`.
