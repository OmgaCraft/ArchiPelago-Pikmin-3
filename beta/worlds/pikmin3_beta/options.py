from dataclasses import dataclass

from Options import Choice, DefaultOnToggle, OptionCounter, OptionGroup, PerGameCommonOptions, Range, Toggle

# Options de la BÊTA (jeu « Pikmin 3 Beta », séparé de la version finale « Pikmin 3 »).
# La bêta active aussi des checks et des items encore incertains, pour les vérifier en jouant :
# jours atteints, sortes de fruits, ensembles de notes A/B/C/D, étapes d'histoire, Pikmin d'autres couleurs, baies.
# Toujours prévu plus tard : missions, death link, pellet posies, cadavres d'ennemis, déblocage des zones.


class Goal(Choice):
    """
    Condition de victoire.
    fruits : presser le nombre de fruits indiqué par « Fruits Required ».
    population : atteindre la population indiquée par « Population Required » (Oignons + terrain).
    """

    display_name = "Goal"
    option_fruits = 0
    option_population = 1
    default = option_fruits


class FruitsRequired(Range):
    """Nombre de fruits pressés (sur 66) nécessaires pour gagner, avec l'objectif « fruits »."""

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
    Dodge Whistle) est un check."""

    display_name = "Key Item Checks"


class NoteChecks(DefaultOnToggle):
    """
    [Bêta] Les notes du GamePad sont des checks. Le jeu les range dans plusieurs ensembles dont le sens
    n'est pas encore sûr : chaque ensemble a son propre nombre de checks (0 = aucun).
    """

    display_name = "Note Checks"


class NotesACount(Range):
    """[Bêta] Checks « Notes A » (ensemble A : Pikmin-ology et tutoriels lus, 20 au jour 13)."""

    display_name = "Notes A Count"
    range_start = 0
    range_end = 40
    default = 10


class NotesBCount(Range):
    """[Bêta] Checks « Notes B » (ensemble B : tutoriels, 5 au jour 13)."""

    display_name = "Notes B Count"
    range_start = 0
    range_end = 40
    default = 3


class NotesCCount(Range):
    """[Bêta] Checks « Notes C » (ensemble C : documents ramassés et scènes vues, 22 au jour 13)."""

    display_name = "Notes C Count"
    range_start = 0
    range_end = 40
    default = 10


class OlimarNoteCount(Range):
    """Checks « Olimar Note » (ensemble D, vérifié en jeu)."""

    display_name = "Olimar Note Count"
    range_start = 0
    range_end = 40
    default = 2


class DayChecks(DefaultOnToggle):
    """[Bêta] Atteindre chaque jour (jour 2, jour 3…) est un check."""

    display_name = "Day Checks"


class DayCheckMax(Range):
    """[Bêta] Dernier jour qui est un check."""

    display_name = "Day Check Max"
    range_start = 2
    range_end = 60
    default = 20


class FruitKindChecks(DefaultOnToggle):
    """[Bêta] Chaque nouvelle sorte de fruit enregistrée dans le Fruit File est un check (30 sortes)."""

    display_name = "Fruit Kind Checks"


class FruitKindMax(Range):
    """[Bêta] Nombre de sortes de fruits qui sont des checks."""

    display_name = "Fruit Kind Max"
    range_start = 1
    range_end = 30
    default = 20


class StoryEventChecks(DefaultOnToggle):
    """[Bêta] Les étapes d'histoire (Data Glutton, sauvetage de Charlie…) sont des checks."""

    display_name = "Story Event Checks"


class StoryEventCount(Range):
    """[Bêta] Nombre d'étapes d'histoire qui sont des checks (seulement 2 observées pour l'instant)."""

    display_name = "Story Event Count"
    range_start = 1
    range_end = 10
    default = 2


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
    """Pourcentage des items de remplissage remplacés par des pièges (« Juice Leak Trap »)."""

    display_name = "Trap Percentage"
    range_start = 0
    range_end = 100
    default = 0


class FillerWeights(OptionCounter):
    """Poids relatifs des items de remplissage."""

    display_name = "Filler Weights"
    valid_keys = ["Juice Drop", "Extra Red Pikmin", "Extra Yellow Pikmin", "Extra Rock Pikmin",
                  "Extra Blue Pikmin", "Extra Winged Pikmin", "Ultra-Spicy Spray", "Ultra-Spicy Berry"]
    min = 0
    default = {
        "Juice Drop": 30, "Extra Red Pikmin": 15, "Extra Yellow Pikmin": 10, "Extra Rock Pikmin": 10,
        "Extra Blue Pikmin": 5, "Extra Winged Pikmin": 5, "Ultra-Spicy Spray": 15, "Ultra-Spicy Berry": 10,
    }


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
    notes_a_count: NotesACount
    notes_b_count: NotesBCount
    notes_c_count: NotesCCount
    olimar_note_count: OlimarNoteCount
    day_checks: DayChecks
    day_check_max: DayCheckMax
    fruit_kind_checks: FruitKindChecks
    fruit_kind_max: FruitKindMax
    story_event_checks: StoryEventChecks
    story_event_count: StoryEventCount
    progressive_pikmin_limit: ProgressivePikminLimit
    pikmin_limit_start: PikminLimitStart
    pikmin_limit_step: PikminLimitStep
    juice_mode: JuiceMode
    trap_percentage: TrapPercentage
    filler_weights: FillerWeights


option_groups = [
    OptionGroup("Goal", [Goal, FruitsRequired, PopulationRequired]),
    OptionGroup(
        "Checks",
        [PopulationMilestoneStep, PopulationMilestoneMax, OnionChecks, KeyItemChecks],
    ),
    OptionGroup(
        "Beta Checks",
        [NoteChecks, NotesACount, NotesBCount, NotesCCount, OlimarNoteCount, DayChecks, DayCheckMax,
         FruitKindChecks, FruitKindMax, StoryEventChecks, StoryEventCount],
    ),
    OptionGroup("Progression", [ProgressivePikminLimit, PikminLimitStart, PikminLimitStep]),
    OptionGroup("Items", [JuiceMode, TrapPercentage, FillerWeights]),
]
