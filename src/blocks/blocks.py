
from .blockprotocol import Block, DrawStyle
from . import items
from .blockprotocol import TextureGroup as TG

class Air(Block):

    transparent = True
    textures = None
    passable = True

class Grass(Block):

    transparent = False
    textures = TG.from_all(1, 0, 0, 1, 0, 0)

class Sand(Block):
    
    transparent = False
    textures = TG.from_one(1, 1)

class Brick(Block):
    
    transparent = False
    textures = TG.from_one(2, 0)

class Stone(Block):
    
    transparent = False
    variants = [
        TG.from_one(5, 1),
        TG.from_one(6, 1)
    ]
    drop_item = items.STONE

class Dirt(Block):

    transparent = False
    textures = TG.from_one(0, 1)

class Log(Block):

    transparent = False
    textures = TG.from_all(4, 1, 4, 1, 3, 1)
    drop_item = items.LOG

class Leaves(Block):

    transparent = True
    variants = [TG.from_one(x, 0) for x in range(3, 7)]
    drop_item = items.LEAVES

class AppleLeaves(Block):

    transparent = True
    variants = [TG.from_one(x, 0) for x in range(7, 9)]
    drop_item = items.APPLE

class TallGrass(Block):

    transparent = True
    draw_style = DrawStyle.GRASS
    variants = [
        TG.from_one(1, 2),
        TG.from_one(3, 2),
        TG.from_one(3, 3)
    ]
    passable = True

class Poppy(Block):

    transparent = True
    draw_style = DrawStyle.GRASS
    variants = [
        TG.from_one(2, 2),
        TG.from_one(2, 3)
    ]
    passable = True


class Cornflower(Block):

    transparent = True
    draw_style = DrawStyle.GRASS
    variants = [
        TG.from_one(4, 2),
        TG.from_one(4, 3)
    ]
    passable = True

class Water(Block):

    transparent = True
    textures = TG.from_one(0, 2)
    draw_style = DrawStyle.FLUID

class Clay(Block):

    transparent = False
    variants = [
        TG.from_one(5, 2),
        TG.from_one(6, 2)
    ]

class BerryBush(Block):

    transparent = True
    textures = TG.from_one(1, 3)
    drop_item = items.BERRY

AIR = Air()
GRASS = Grass()
SAND = Sand()
BRICK = Brick()
STONE = Stone()
DIRT = Dirt()
CLAY = Clay()
LOG = Log()
LEAVES = Leaves()
TALL_GRASS = TallGrass()
POPPY = Poppy()
CORNFLOWER = Cornflower()
WATER = Water()
APPLE_LEAVES = AppleLeaves()
BERRY_BUSH = BerryBush()

items.LOG.place_block = LOG
items.LEAVES.place_block = LEAVES
items.STONE.place_block = STONE

