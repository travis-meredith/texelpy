
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Protocol

from maths.bufferdomain import tex_coord
from maths.types import TextureGrid

ENCODING = "utf-8"

@dataclass
class TextureGroup:
    """Dataclass providing <Model>.update_chunk access to 
    texture data"""

    top: TextureGrid
    bottom: TextureGrid
    side: TextureGrid

    @staticmethod
    def from_one(x, y) -> TextureGroup:
        "clone tex_coord in (x, y) to all fields"
        w = tex_coord(x, y)
        return TextureGroup(w, w, w)

    @staticmethod
    def from_all(a, b, c, d, e, f) -> TextureGroup:
        "map tex_coord"
        x, y, z = tex_coord(a, b), tex_coord(c, d), tex_coord(e, f)
        return TextureGroup(x, y, z)

class DrawStyle(Enum):
    "<Model>.update_chunk rendering type"
    BLOCK = 0
    GRASS = 1
    FLUID = 2

class BlockProtocol(Protocol):
    """Protocol for Block classes
    
    transparent: bool; should draw faces of tiles adjacent
    textures: TextureGroup; textures for drawing tile
    draw_style: DrawStyle: rules for drawing in <Model>.update_chunk
    variants: Optional[list[TextureGroup]]; list of rng allocated
                                            textures to use for update_chunk
    passable: bool; should creatures be allowed to pass through object
    drop_item: ItemProtocol; item dropped when mined
    """
    transparent: bool
    textures: TextureGroup
    draw_style: DrawStyle
    variants: list[TextureGroup] | None
    passable: bool
    drop_item: ItemProtocol | None

    _id: ClassVar[str]

    def __new__(cls) -> BlockProtocol: ...
    def __eq__(self, alt) -> bool: ...
    def to_id(self) -> str: ...

class Block(BlockProtocol):
    """Basic Block object definition"""
    transparent: bool = False
    textures: TextureGroup | None = None # type: ignore
    draw_style: DrawStyle = DrawStyle.BLOCK
    variants: list[TextureGroup] | None = None
    passable: bool = False
    drop_item: ItemProtocol | None = None
    
    _id: ClassVar[str] = "Block"

    def __new__(cls):
        cls._id = cls.__qualname__
        obj = Protocol.__new__(cls)
        return obj

    def __eq__(self, alt):
        return self._id == alt._id

    def __repr__(self) -> str:
        return f"Block.{self.to_id()}"

    def to_id(self) -> str:
        return self.__class__.__qualname__

BLOCK = Block()

class ItemProtocol:

    place_block: BlockProtocol

    _id: ClassVar[str]

    def __new__(cls): ...
    def to_id(self) -> str: ...

class Item(ItemProtocol):

    place_block: BlockProtocol = BLOCK

    _id: ClassVar[str] = "Item"

    def __new__(cls):
        cls._id = cls.__qualname__
        obj = Protocol.__new__(cls)
        return obj

    def __repr__(self) -> str:
        return f"Item.{self.to_id()}"

    def to_id(self) -> str:
        return self._id
