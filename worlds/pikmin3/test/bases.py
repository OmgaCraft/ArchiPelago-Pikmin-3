from test.bases import WorldTestBase

from ..world import Pikmin3World


class Pikmin3TestBase(WorldTestBase):
    game = "Pikmin 3"
    world: Pikmin3World
