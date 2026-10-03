# Pikmin 3 Archipelago

Intégration [Archipelago](https://archipelago.gg) pour **Pikmin 3** (Wii U, version originale) émulé par **Cemu**.

- **APWorld** « Pikmin 3 » : [worlds/pikmin3](worlds/pikmin3) (version 1.0.0).
- **Client** Python qui lit et écrit la mémoire de Cemu (inclus dans l'APWorld : *Pikmin 3 Client* dans le lanceur).
- **Graphic pack Cemu** pour les modifications du jeu (aucun fichier du jeu n'est modifié ni distribué).

## Télécharger et jouer

Le kit prêt à l'emploi est dans [dist/Pikmin_3_Archipelago.zip](dist/Pikmin_3_Archipelago.zip) (APWorld + YAML +
guide). Mode d'emploi complet : [GUIDE_FR.md](GUIDE_FR.md).

Version du jeu prise en charge : **Pikmin 3 (Europe), version du disque v1, sans mise à jour ni DLC**, sur Cemu 2.6
ou plus récent (Windows). Il te faut ta propre copie du jeu.

## Contenu du dépôt

| Dossier / fichier | Contenu |
|---|---|
| [worlds/pikmin3](worlds/pikmin3) | APWorld de la version finale (options, items, checks, logique, client, graphic pack, tests) |
| [dist](dist) | Kit construit (`pikmin3.apworld` + zip) |
| [yaml](yaml) | Fichier joueur d'exemple |
| [GUIDE_FR.md](GUIDE_FR.md) | Guide d'installation et de jeu |
| [docs/phase0](docs/phase0) | Recherche sur le jeu : adresses mémoire, patches, journaux (`findings.md`) |
| [docs/tests_solo_v1.md](docs/tests_solo_v1.md) | Fiche des tests en jeu |
| [tools](tools) | Outils de recherche et de test (lecture de la mémoire de Cemu, packs de test) |
| [beta](beta) | Version bêta séparée (« Pikmin 3 Beta ») qui sert à découvrir de nouvelles données |
| [COORDINATION.md](COORDINATION.md) | Suivi du projet : état des connaissances, décisions, reste à faire, journaux |

## Ce que fait la V1

- Objectif par défaut : battre le boss final **et** presser un nombre de fruits choisi.
- Checks : fruits pressés, Oignons, objets importants (dont le sauvetage de Louie), paliers de population, notes du
  GamePad (conseils, notes d'Olimar, Secret Memos en option).
- Items : le jus des fruits (les fruits pressés n'en donnent plus), limite de Pikmin progressive, zones progressives
  (Distant Tundra → Twilight River → Formidable Oak), types de Pikmin progressifs (option expérimentale), remplissage
  et piège.

L'état détaillé (vérifié en jeu ou non) est dans le [guide](GUIDE_FR.md#état-de-la-v1) et dans
[COORDINATION.md](COORDINATION.md).
