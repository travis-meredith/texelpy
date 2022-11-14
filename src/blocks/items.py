
from .blockprotocol import Item, ItemProtocol

class FoodProtocol(ItemProtocol):
    energy: int

class Stone(Item): pass
class Log(Item): pass
class Leaves(Item): pass
class Apple(FoodProtocol, Item): energy = 10
class Berry(FoodProtocol, Item): energy = 8

STONE = Stone()
LOG = Log()
LEAVES = Leaves()
APPLE = Apple()
BERRY = Berry()
