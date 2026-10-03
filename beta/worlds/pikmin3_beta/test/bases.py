from test.bases import WorldTestBase

from ..data.game_info import GAME_NAME
from ..world import Pikmin3BetaWorld


class Pikmin3TestBase(WorldTestBase):
    game = GAME_NAME
    world: Pikmin3BetaWorld
