# Phase 0 — Version ciblée

Légende : ✅ vérifié sur la machine · 📖 source externe, à confirmer · ❓ à relever

## Jeu

| Élément | Valeur | Statut |
|---|---|---|
| Jeu | **Pikmin 3 (Europe) (EnFrDeEsIt)**, image disque | ✅ choix utilisateur (2026-09-27) |
| Ancienne cible | Pikmin 3 (USA) (EnFrEs) (Rev 1) : abandonnée après un échec de lancement, probablement la même clé de disque manquante (voir ci-dessous) | ✅ |
| Lancement EUR | Échec : « Could not decrypt title ». `keys.txt` (`%APPDATA%\Cemu\keys.txt`) ne contient que la clé d'exemple ; le `.wux` n'est accompagné d'aucune clé | ✅ bloquant |
| DLC | Aucun | ✅ choix utilisateur |
| Mise à jour installée | **Aucune** : pas de 2.0.0 disponible → on vise la version du disque (log : « Update: Not present », « DLC: Not present ») | ✅ |
| Title IDs Pikmin 3 | JPN `000500001012BC00` · USA `000500001012BD00` · **EUR `000500001012BE00`** | ✅ lus dans les profils fournis avec Cemu (`gameProfiles/default/*.ini`) |
| Titres associés (EUR) | DLC `0005000C1012BE00` · mise à jour `0005000E1012BE00` (format standard Wii U) | ✅ DLC (profil Cemu) · 📖 mise à jour |
| Dossier de sauvegarde (EUR) | `%APPDATA%\Cemu\mlc01\usr\save\00050000\1012be00` | ✅ créé au premier lancement |
| Image utilisée | `GamePath\Pikmin 3 (Europe) (En,Fr,De,Es,It).wux` | ✅ log |
| Version du titre | **v1** (`TitleVersion: v1`, `TitleRegion: EU`) | ✅ log |
| RPX hash (base = updated) | `3eabc0bb` | ✅ log |
| Module de code | **`carrot`**, checksum **`0x838be11a`** → valeur de `moduleMatches` pour `patches.txt` | ✅ log (à valider par un premier patch) |
| Langue de la console Cemu | Anglais (`console_language = 1` dans settings.xml). La garder fixe pendant la Phase 0 | ✅ |

### Mises à jour Wii U connues 📖 ([Pikipedia – Update](https://www.pikminwiki.com/Update))

| Version | Date | Contenu utile pour le projet |
|---|---|---|
| 1.1.0 | 2013-07-25 | SpotPass, Miiverse, records mondiaux |
| 1.2.0 | 2013-10-01 | Support DLC « Collect Treasure! » ; 1 étape **gratuite** (Tropical Forest Remix) |
| 1.3.0 | 2013-11-06 | Support DLC « Battle Enemies! » ; 1 étape **gratuite** (Tropical Wilds Remix) |
| 1.4.0 | 2013-12-02 | Étape **gratuite** Fortress of Festivity (dans les deux modes) ; correctif de réapparition du capitaine après une chute |
| **2.0.0** | 2014-05-29 | **Dernière version.** Contrôle au stylet, **accélération de l'animation des fruits**, bouton « Réessayer » en Mission, correctifs |

> Les patches (`patches.txt`) ne s'appliquent qu'au RPX dont la somme correspond.
> Tout le travail de patch vise donc **cette** version. Installer une mise à jour
> plus tard changerait le RPX et demanderait de refaire les patches.

## Émulateur et outils

| Élément | Valeur | Statut |
|---|---|---|
| Cemu | 2.6, `C:\Users\2dcra\Downloads\Cemu_2.6\Cemu.exe` | ✅ |
| Mode | Non portable : données dans `%APPDATA%\Cemu` (settings.xml, mlc01, graphicPacks) | ✅ |
| Dossier des jeux | `C:\Users\2dcra\Downloads\Cemu_2.6\GamePath` | ✅ (lu dans settings.xml) |
| `log.txt` | `%APPDATA%\Cemu\log.txt`, réécrit à chaque démarrage de Cemu. Contient `Init Wii U memory space (base: 0x…)` | ✅ |
| Stub GDB | Port 1337 configuré dans settings.xml (piste alternative, non utilisée) | ✅ |
| Python | `py -3.13` (3.13) ; `python` du PATH = 3.10, **non supporté** par Archipelago ≥ 0.6.4 | ✅ |

## Mémoire (premiers constats)

| Constat | Statut |
|---|---|
| Cemu réserve **exactement 4 Gio** (0x100000000) d'un seul bloc pour l'espace Wii U, dès le démarrage, même sans jeu lancé | ✅ |
| La base change à chaque lancement (observée : `0x22D96EA0000`) → la retrouver à chaque connexion | ✅ |
| Adresse hôte = base + adresse Wii U : lecture, écriture et relecture validées | ✅ |
| Sans jeu lancé, plages engagées : `0x0E000000–0x10000000` et `0xF8000000–0xFA000000` (32 Mio chacune) | ✅ |
| La base de `log.txt` et celle trouvée par la sonde sont identiques (`0x16B88410000` le 2026-09-27) | ✅ |
| D'autres grosses réservations existent (256 Gio, 4 Gio + 128 Kio) : ce ne sont pas la mémoire Wii U | ✅ |

Plages engagées avec Pikmin 3 lancé (sur l'écran de jeu) ✅ :

| Plage Wii U | Taille | Remarque |
|---|---|---|
| `0x00010000–0x00100000` | 0,94 Mio | |
| `0x00E00000–0x01000000` | 2 Mio | |
| `0x01800000–0x01C00000` | 4 Mio | |
| `0x02000000–0x50000000` | 1248 Mio | Code (`0x02000000`…) puis données et MEM2 (`0x10000000`…) |
| `0xE0000000–0xE4000000` | 64 Mio | |
| `0xE8000000–0xEA000000` | 32 Mio | |
| `0xF4000000–0xFA000000` | 96 Mio | Commence par MEM1 |
| `0xFFC00000…`, `0xFFFFF000…` | quelques Kio | |
