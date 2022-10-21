from __future__ import annotations

from maths.types import Location

from .inventory import Inventory, Tools


class Creature:

    """
    Underlying Creature object. Should not be exposed directly to AI scripts
        colour:     list[int]   16-int with creature colour (for rendering)
        loc:        Location    location of creature
        energy:     int         energy of creature
        inventory:  Inventory   access to items of creature
        tools:      Tools       <unused>
    """

    # render
    colour: list[int]

    # stats
    loc: Location
    energy: int

    # items
    inventory: Inventory
    tools: Tools # TODO: tools required for <ModelAPIProtocol>.try_mine

    # resettable
    moves: int

    def __init__(self, 
            loc: Location, 
            energy: int = 40,
            colour: tuple[int, int, int] = (0, 0, 0)
            ):

        self.colour = list((colour[0], colour[1], colour[2], 255) * 4)

        self.loc = loc
        self.energy = energy

        self.moves = 1

        self.inventory = Inventory()
        self.tools = Tools()

    def clear(self) -> bool:
        "reset Creature after a tick; return whether creature should be killed or not"

        self.moves = 1
        return self.energy <= 0

