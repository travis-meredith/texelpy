
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from blocks import BlockProtocol
from maths.types import ChunkLocation, Location

from model.worldgenconfig import WorldGenerationConfigProtocol


@dataclass(frozen=False)
class ChunkSource:
    blocks: list[BlockProtocol]
    models: list[None]

class ModelProtocol(Protocol):

    model: list[ChunkSource | None]

    def serialise(self) -> bytes: ...
    def deserialise(self, data: bytes): ...
    def generate(self, config: WorldGenerationConfigProtocol): ...
    def add_chunk(self, chunkloc: ChunkLocation, chunk: ChunkSource): ...
    def remove_chunk(self, chunkloc: ChunkLocation): ...
    def update_chunk(self, chunkloc: ChunkLocation): ...
    def get_block(self, pos: Location) -> BlockProtocol: ...
    def add_block(self, pos: Location, block: BlockProtocol, defer: bool = False): ...
    def remove_block(self, pos: Location): ...
