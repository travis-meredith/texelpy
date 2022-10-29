
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

TG = TextureGroup

class DrawStyle(Enum):
    "<Model>.update_chunk rendering type"
    BLOCK = 0
    GRASS = 1
    FLUID = 2

@dataclass
class BlockProtocol:

    transparent: bool
    passable: bool
    textures: TG | None
    variants: list[TG] | None
    draw_style: DrawStyle
    drop_item: ItemProtocol | None

    @staticmethod
    def from_default(
            transparent: bool = False,
            passable: bool = False,
            textures: TG | None = None,
            variants: list[TG] | None = None,
            draw_style: DrawStyle = DrawStyle.BLOCK,
            drop_item: ItemProtocol | None = None
            ):
        return BlockProtocol(transparent, passable, textures, variants, draw_style, drop_item)

    @staticmethod
    def from_solid(
            textures: TG,
            drop_item: ItemProtocol | None = None
            ):
        return BlockProtocol(False, False, textures, None, DrawStyle.BLOCK, drop_item)

    @staticmethod
    def from_grass(
            textures: TG | None = None,
            variants: list[TG] | None = None,
            drop_item: ItemProtocol | None = None
            ):
        return BlockProtocol(True, True, textures, variants, DrawStyle.GRASS, drop_item)


class ItemProtocol:

    place_block: BlockProtocol | None

    _id: ClassVar[str]

    def __new__(cls): ...
    def to_id(self) -> str: ...

class Item(ItemProtocol):

    place_block: BlockProtocol | None = None

    _id: ClassVar[str] = "Item"

    def __new__(cls):
        cls._id = cls.__qualname__
        obj = Protocol.__new__(cls)
        return obj

    def __repr__(self) -> str:
        return f"Item.{self.to_id()}"

    def to_id(self) -> str:
        return self._id
