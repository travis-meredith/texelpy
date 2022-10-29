
from .blockprotocol import BlockProtocol, DrawStyle, ItemProtocol
from . import items
from .blockprotocol import TextureGroup as TG
from dataclasses import dataclass

AIR = BlockProtocol(True, True, None, None, DrawStyle.BLOCK, None)
GRASS = BlockProtocol.from_solid(TG.from_all(1, 0, 0, 1, 0, 0))
SAND = BlockProtocol.from_solid(TG.from_one(1, 1))
BRICK = BlockProtocol.from_solid(TG.from_one(2, 0))
STONE = BlockProtocol.from_solid(TG.from_one(5, 1), items.STONE)
DIRT = BlockProtocol.from_solid(TG.from_one(0, 1))
LOG = BlockProtocol.from_solid(TG.from_all(4, 1, 4, 1, 3, 1), items.LEAVES)
LEAVES = BlockProtocol.from_default(True, False, None, [TG.from_one(x, 0) for x in range(3, 7)])
APPLE_LEAVES = BlockProtocol.from_default(True, False, None, [TG.from_one(x, 0) for x in range(7, 9)], drop_item=items.APPLE)
TALL_GRASS = BlockProtocol.from_grass(variants=[TG.from_one(1, 2), TG.from_one(3, 2), TG.from_one(3, 3)])
POPPY = BlockProtocol.from_grass(variants=[TG.from_one(2, x) for x in range(2, 4)])
CORNFLOWER = BlockProtocol.from_grass(variants=[TG.from_one(4, x) for x in range(2, 4)])
WATER = BlockProtocol.from_default(True, False, TG.from_one(0, 2), draw_style=DrawStyle.FLUID)
CLAY = BlockProtocol.from_solid(TG.from_one(5, 2))
BERRY_BUSH = BlockProtocol.from_default(True, False, TG.from_one(1, 3), drop_item=items.BERRY)
