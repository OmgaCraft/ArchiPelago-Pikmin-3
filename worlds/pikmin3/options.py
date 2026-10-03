from dataclasses import dataclass

from Options import Choice, DefaultOnToggle, OptionCounter, OptionGroup, PerGameCommonOptions, Range, Toggle

# Options de la V1. Seules les options réellement prises en charge par le client sont exposées.
# Prévu plus tard (recherche en cours, voir docs/phase0/findings.md) : missions, death link,
# pellet posies, cadavres d'ennemis, badges, types de Pikmin / Oignons en items.


class Goal(Choice):
    """
    Condition de victoire.
    final_boss : battre le boss final ET avoir pressé le nombre de fruits indiqué par « Fruits Required ».
    fruits : presser le nombre de fruits indiqué par « Fruits Required ».
    population : atteindre la population indiquée par « Population Required » (Oignons + terrain).
    """

    display_name = "Goal"
    option_fruits = 0
    option_population = 1
    option_final_boss = 2
    default = option_final_boss


class FruitsRequired(Range):
    """Nombre de fruits pressés (sur 66) nécessaires pour gagner, avec les objectifs « final_boss » et « fruits »."""

    display_name = "Fruits Required"
    range_start = 1
    range_end = 66
    default = 40


class PopulationRequired(Range):
    """Population de Pikmin (Oignons + terrain) nécessaire pour gagner, avec l'objectif « population »."""

    display_name = "Population Required"
    range_start = 50
    range_end = 1000
    default = 300


class PopulationMilestoneStep(Range):
    """Écart entre deux paliers de population (arrondi à la dizaine). Chaque palier est un check."""

    display_name = "Population Milestone Step"
    range_start = 10
    range_end = 200
    default = 50


class PopulationMilestoneMax(Range):
    """Dernier palier de population qui est un check (0 = aucun palier)."""

    display_name = "Population Milestone Max"
    range_start = 0
    range_end = 1000
    default = 250


class OnionChecks(DefaultOnToggle):
    """La découverte de chaque Oignon (sauf le rouge, présent dès le départ) est un check."""

    display_name = "Onion Checks"


class KeyItemChecks(DefaultOnToggle):
    """L'obtention des objets importants et améliorations connus (Data Glutton, Anti-Electrifier,
    Metal Suit Z, Dodge Whistle) et le sauvetage de Louie sont des checks."""

    display_name = "Key Item Checks"


class NoteChecks(DefaultOnToggle):
    """
    Les notes du GamePad sont des checks : « Tutorial Note N » (N notes de conseils, Pikmin-ology comprise) et
    « Olimar Note N » (N notes d'Olimar). Beaucoup de notes de conseils arrivent toutes seules au fil de l'histoire.
    """

    display_name = "Note Checks"


class TutorialNoteCount(Range):
    """Nombre de notes de conseils qui sont des checks (63 relevées sur une partie terminée)."""

    display_name = "Tutorial Note Count"
    range_start = 1
    range_end = 63
    default = 30


class OlimarNoteCount(Range):
    """Nombre de notes d'Olimar qui sont des checks (15 relevées sur une partie terminée)."""

    display_name = "Olimar Note Count"
    range_start = 1
    range_end = 15
    default = 8


class SecretMemoCount(Range):
    """
    Nombre de Secret Memos qui sont des checks (0 = aucun). Les guides en annoncent 10 (2 par zone) ;
    un seul a été vérifié en jeu, et leur emplacement n'est pas connu : ils demandent toutes les zones.
    """

    display_name = "Secret Memo Count"
    range_start = 0
    range_end = 10
    default = 0


class ProgressivePikminLimit(DefaultOnToggle):
    """
    [Expérimental] La limite de Pikmin sur le terrain commence basse et augmente avec les items
    « Progressive Pikmin Limit » jusqu'à 100. Nécessite le graphic pack Archipelago.
    """

    display_name = "Progressive Pikmin Limit"


class PikminLimitStart(Range):
    """Limite de Pikmin sur le terrain au départ (si la limite progressive est activée)."""

    display_name = "Pikmin Limit Start"
    range_start = 10
    range_end = 90
    default = 30


class PikminLimitStep(Range):
    """Augmentation de la limite par item « Progressive Pikmin Limit »."""

    display_name = "Pikmin Limit Step"
    range_start = 5
    range_end = 50
    default = 10


class ProgressiveZones(DefaultOnToggle):
    """
    [Expérimental] On commence avec Tropical Wilds et Garden of Hope ; chaque item « Progressive Zone » ouvre la
    suivante : Distant Tundra, Twilight River puis Formidable Oak (zone du boss final). Les checks des zones suivantes
    demandent ces items. Si l'histoire ouvre une zone trop tôt, le client la referme jusqu'à l'item.
    """

    display_name = "Progressive Zones"


class ProgressivePikmin(Toggle):
    """
    [Expérimental] Ajoute 4 items « Progressive Pikmin » qui débloquent les types dans l'ordre : roc, jaune, ailé,
    bleu. Le type est débloqué à la fin de la journée où l'item arrive (plus tôt, le jeu plante) ; son Oignon est vide
    mais donne une pousse le lendemain. L'histoire débloque encore les types elle-même : ces items font gagner du
    temps mais ne sont pas exigés par la logique. Les checks « Discover … Onion » sont alors retirés.
    """

    display_name = "Progressive Pikmin"


class JuiceMode(Choice):
    """
    Gestion du jus (qui sert de temps de survie) :
    normal : consommation normale, un game over reste possible.
    safe : le client garde au moins 2 bouteilles le matin (pas de game over par manque de jus).
    no_consumption : le client rend la bouteille bue chaque nuit.
    """

    display_name = "Juice Mode"
    option_normal = 0
    option_safe = 1
    option_no_consumption = 2
    default = option_safe


class TrapPercentage(Range):
    """Pourcentage des items de remplissage remplacés par des pièges (V1 : « Juice Leak Trap »)."""

    display_name = "Trap Percentage"
    range_start = 0
    range_end = 100
    default = 0


class FillerWeights(OptionCounter):
    """Poids relatifs des items de remplissage."""

    display_name = "Filler Weights"
    valid_keys = ["Juice Drop", "Extra Red Pikmin", "Ultra-Spicy Spray"]
    min = 0
    default = {"Juice Drop": 40, "Extra Red Pikmin": 40, "Ultra-Spicy Spray": 20}


@dataclass
class Pikmin3Options(PerGameCommonOptions):
    goal: Goal
    fruits_required: FruitsRequired
    population_required: PopulationRequired
    population_milestone_step: PopulationMilestoneStep
    population_milestone_max: PopulationMilestoneMax
    onion_checks: OnionChecks
    key_item_checks: KeyItemChecks
    note_checks: NoteChecks
    tutorial_note_count: TutorialNoteCount
    olimar_note_count: OlimarNoteCount
    secret_memo_count: SecretMemoCount
    progressive_pikmin_limit: ProgressivePikminLimit
    pikmin_limit_start: PikminLimitStart
    pikmin_limit_step: PikminLimitStep
    progressive_zones: ProgressiveZones
    progressive_pikmin: ProgressivePikmin
    juice_mode: JuiceMode
    trap_percentage: TrapPercentage
    filler_weights: FillerWeights


option_groups = [
    OptionGroup("Goal", [Goal, FruitsRequired, PopulationRequired]),
    OptionGroup(
        "Checks",
        [PopulationMilestoneStep, PopulationMilestoneMax, OnionChecks, KeyItemChecks,
         NoteChecks, TutorialNoteCount, OlimarNoteCount, SecretMemoCount],
    ),
    OptionGroup("Progression", [ProgressivePikminLimit, PikminLimitStart, PikminLimitStep, ProgressiveZones,
                                ProgressivePikmin]),
    OptionGroup("Items", [JuiceMode, TrapPercentage, FillerWeights]),
]
