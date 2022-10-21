
from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

from ai.creature import Creature
from blocks import BlockProtocol
from blocks.blockprotocol import ItemProtocol
from blocks.items import FoodProtocol
from maths.types import Direction, Location
from model.modelprotocol import ModelProtocol

from .modelapiprotocol import ModelAPIProtocol

T = TypeVar("T", float, int)

@dataclass()
class Accessor(Generic[T]):
    """dataclass in T that provides static access to a value for decorator use"""
    get: Callable[[], T]
    set: Callable[[T], None]

def create_model_api(model: ModelProtocol, creature: Creature) -> ModelAPIProtocol:
    """create a class closure of ModelAPI (ModelAPIProtocol) with model and creature
    baked in"""

    def _get_energy() -> int: return creature.energy
    def _set_energy(set: int): creature.energy = set
    ENERGY = Accessor(_get_energy, _set_energy)

    def _get_moves() -> int: return creature.moves
    def _set_moves(moves: int): creature.moves = moves
    MOVES = Accessor(_get_moves, _set_moves)
    
    class ModelAPI(ModelAPIProtocol):

        @staticmethod
        def require(points: T, accessor: Accessor[T]):
            def inner(callable: Callable[..., bool]):
                def _inner(*args, **kwargs):
                    g = accessor.get()
                    if g < points:
                        # if unsufficient points;
                        # preempt function
                        return False
                    # capture function values
                    ret = callable(*args, **kwargs)
                    if ret is True:
                        accessor.set(g - points)
                    return ret
                return _inner
            return inner

        @staticmethod
        def distance(max_range: float):
            max_range2 = max_range * max_range
            def inner(callable: Callable[[Location,], bool]):
                def _inner(loc: Location, *args, **kwargs):
                    cx, cy, cz = creature.loc
                    lx, ly, lz = loc
                    x, y, z = (cx - lx), (cy - ly), (cz - lz)
                    if x * x + y * y + z * z > max_range2:
                        return False
                    return callable(loc, *args, **kwargs)
                return _inner
            return inner
    
        @staticmethod
        def get_loc() -> Location:
            return creature.loc

        @staticmethod
        def get_block(pos: Location) -> BlockProtocol:
            return model.get_block(pos)

        @staticmethod
        def get_block_xyz(x: int, y: int, z: int) -> BlockProtocol:
            return model.get_block((x, y, z))

        @staticmethod
        def has_inventory_space(quantity: int) -> bool:
            return creature.inventory.has_space(quantity)

        @staticmethod
        def get_inventory() -> dict[ItemProtocol, int]:
            return creature.inventory.as_dict()

        @staticmethod
        def get_tools() -> list[ItemProtocol]:
            return creature.tools.as_flat_list()

        @staticmethod
        @require(1, ENERGY)
        @require(1, MOVES)
        def try_walk(direction: Direction) -> bool:

            if direction not in ((0, 1), (1, 0), (-1, 0), (0, -1)):
                return False

            sx, sy, sz = ModelAPI.get_loc()
            tx, ty, tz = sx + direction[0], sy, sz + direction[1]
            get = ModelAPI.get_block_xyz

            # step down
            if (not get(tx, ty - 2, tz).passable) and get(tx, ty - 1, tz).passable and get(tx, ty, tz).passable:
                creature.loc = tx, ty - 1, tz
                return True

            # flat move
            if (not get(tx, ty - 1, tz).passable) and get(tx, ty, tz).passable and get(tx, ty + 1, tz).passable:
                creature.loc = tx, ty, tz
                return True

            # step up
            if (not get(tx, ty, tz).passable) and get(tx, ty + 1, tz).passable and get(tx, ty + 2, tz).passable:
                creature.loc = tx, ty + 1, tz
                return True

            return False

        @staticmethod
        @require(1, ENERGY)
        @distance(5)
        def try_mine(loc: Location) -> bool:
            
            if not creature.inventory.has_space():
                return False

            target_block = model.get_block(loc)
            if target_block.drop_item is None:
                return False

            model.remove_block(loc)
            creature.inventory.add(target_block.drop_item)
            return True

        @staticmethod
        def try_eat(food: FoodProtocol) -> bool:
            
            if not creature.inventory.has_item(food):
                return False

            creature.energy += food.energy
            creature.inventory.remove(food)
            return True

    return ModelAPI()
