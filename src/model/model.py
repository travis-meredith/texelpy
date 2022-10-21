from __future__ import annotations

import pickle
import random
from collections import deque
from dataclasses import dataclass
from typing import Callable, Generator, TypeVar

from ai.creature import Creature  # type: ignore
from blocks import BlockProtocol, DrawStyle
from blocks.blocks import AIR, DIRT, GRASS, SAND, STONE, TALL_GRASS
from display.constants import TEXTURE_PATH
from maths import choice
from maths.blocks import get_block_id_xyz, get_chunk_and_offsets, get_chunk_id
from maths.constants import (CHUNK_BUFFER_SIZE, CHUNK_RADIUS, CHUNK_SIZE,
                             Colour, Normal, Vertex)
from maths.generators import xy_range, xyz_range
from maths.types import ChunkLocation, Location
from pyglet import image  # type: ignore
from pyglet.gl import GL_QUADS  # type: ignore
from pyglet.graphics import Batch  # type: ignore
from pyglet.graphics import TextureGroup  # type: ignore
from pyglet.graphics.vertexdomain import VertexList  # type: ignore
from tqdm import tqdm  # type: ignore

import model.worldgen as worldgen
from model.modelprotocol import ChunkSource, ModelProtocol
from model.worldgenconfig import WorldGenerationConfigProtocol

from .worldgen import GenerateWorldResult

T = TypeVar("T")

@dataclass(frozen=False)
class CreatureWrapper:
    creature: Creature
    script: Callable[[], None]

class Model(ModelProtocol):

    """ Base model for the block renderer and world state manager

    Can be loaded from a pickle string using <>.serialise
    Can be saved to a pickle string using <>.deserialise
    Can generate a new world using gen (supply Model with dims + mux first)
    """

    creatures: list[CreatureWrapper]
    chunk_queue: deque[Generator[None, None, None]]

    batch: Batch
    batch_fluid: Batch
    group: TextureGroup
    model: list[None | ChunkSource]
    displayed: list[None | VertexList]
    displayed_fluid: list[None | VertexList]
    dims: tuple[int, int]

    texturepath: str = TEXTURE_PATH

    def __init__(self):
        self.creatures = []
        self.chunk_queue = deque()
        self.model = [None for _ in range(CHUNK_BUFFER_SIZE)]
        self.batch = Batch()
        self.batch_fluid = Batch()
        self.group = TextureGroup(image.load(self.texturepath).get_texture())
        self.displayed = [None for _ in range(CHUNK_BUFFER_SIZE)]
        self.displayed_fluid = [None for _ in range(CHUNK_BUFFER_SIZE)]

    def serialise(self) -> bytes:
        "return a pickle-string of bytes with all the model's block data stored"
        return pickle.dumps({"model": self.model, "dims": self.dims})

    def deserialise(self, bytes: bytes):
        """load a pickle-string of bytes into the model's chunk data and dims data
        and update every chunk supplied"""

        source = pickle.loads(bytes)
        self.model = source["model"]
        self.dims = source["dims"]

        with tqdm(total=self.dims[0] * self.dims[1] * 20, desc="loading chunks") as progress_bar:
            for cx in range(self.dims[1]):
                for cz in range(self.dims[0]):
                    for cy in range(20):
                        self.update_chunk((cx, cy, cz))
                        progress_bar.update(1)

    def generate_spikey(self, _ = None):
        """spikey world generation
        sets <Model>.dims and updates all chunks"""
        self.dims = 10, 10
        for cx, cz in xy_range(10, 10):
            chunk = [AIR for _ in range(CHUNK_SIZE)]
            for ox, oz in xy_range(CHUNK_RADIUS, CHUNK_RADIUS):
                height = random.randint(CHUNK_RADIUS - 8, CHUNK_RADIUS)
                for y in range(height - 4):
                    chunk[get_block_id_xyz(ox, y, oz)] = SAND  # type: ignore
                for y in range(height - 4, height - 2):
                    chunk[get_block_id_xyz(ox, y, oz)] = DIRT  # type: ignore
                chunk[get_block_id_xyz(ox, height - 2, oz)] = GRASS  # type: ignore
                chunk[get_block_id_xyz(ox, height - 1, oz)] = TALL_GRASS  # type: ignore
            self.model[get_chunk_id((cx, 0, cz))] = ChunkSource(chunk, [])  # type: ignore
    
        for cx, cz in tqdm(xy_range(10, 10), total=100):
            self.update_chunk((cx, 0, cz))

    def generate_normal(self, config: WorldGenerationConfigProtocol):
        """standard world generation
        sets <Model>.dims and calls update_chunk on surface chunks
        """
        result: GenerateWorldResult = worldgen.generate_world(self, config)
        self.dims = result.mxz
        surface_chunks: set[ChunkLocation] = set()
        #for x, z in xy_range(self.dims[0] * CHUNK_RADIUS, self.dims[1] * CHUNK_RADIUS):
        #    y = result.height_map[(x, z)]
        #    cx, _, cy, _, cz, _ = get_chunk_and_offsets((x, y, z))
        #    surface_chunks.add((cx, cy, cz))
        for surface_tile in result.surface_tiles:
            cx, _, cy, _, cz, _ = get_chunk_and_offsets(surface_tile)
            for _cy in range(cy, cy + 3):
                surface_chunks.add((cx, _cy, cz))
        for surface_chunk in tqdm(surface_chunks, "updating surface chunks"):
            self.update_chunk(surface_chunk)

    def generate_cubes(self, _ = None):
        """cube world generation
        sets <Model>.dims and calls update chunk on all chunks
        """
        self.dims = (2, 2)
        lst: list[BlockProtocol] = [GRASS, STONE]
        l = 0
        for x in range(2):
            for y in range(2):
                for z in range(2):
                    chunk = [lst[l % 2] for _ in range(CHUNK_SIZE)]
                    l += 1
                    self.add_chunk((x, y, z), ChunkSource(chunk, []))
                    self.update_chunk((x, y, z))

    def generate(self, config: WorldGenerationConfigProtocol):
        "generate world using config"
        self.generate_normal(config)

    def add_chunk(self, chunkloc: ChunkLocation, chunk: ChunkSource):
        "add given chunk to chunkloc and immediately update"
        model_chunk_id = get_chunk_id(chunkloc)
        self.model[model_chunk_id] = chunk
        self.update_chunk(chunkloc)

    def remove_chunk(self, chunkloc: ChunkLocation):
        "remove given chunkloc and immediately delete display"
        model_chunk_id = get_chunk_id(chunkloc)
        chunk_option = self.displayed[model_chunk_id]
        if chunk_option is None:
            return
        chunk_option.delete()
        self.displayed[model_chunk_id] = None
        self.model[model_chunk_id] = None

    def update_chunk(self, chunkloc: ChunkLocation):
        "draw vertices at the given chunkloc"

        # identify chunk 
        model_chunk_id = get_chunk_id(chunkloc)
        chunk_source: ChunkSource | None = self.model[model_chunk_id]
        if chunk_source is None:
            # no need to update an unloaded chunk
            return
        chunk = chunk_source.blocks

        # assign base positions
        basex, basey, basez = chunkloc[0] * CHUNK_RADIUS, chunkloc[1] * CHUNK_RADIUS, chunkloc[2] * CHUNK_RADIUS
        
        # chunk boundries
        lim = CHUNK_RADIUS - 1
        blim = (self.dims[0] * CHUNK_RADIUS) - 1

        # draw closure data
        # these are going to be used by batch.add
        sidecount = 0
        vertices: list[float] = []
        texture_data: list[float] = []
        colour_data: list[int] = []
        normals: list[float] = []

        def draw(
                side: list[int], 
                dirs: list[float], 
                textures: list[float], 
                norms: list[float]
                ):
            nonlocal sidecount # immutable int -> nonlocal required
            vertices.extend([x+dirs[0],y+dirs[1],z+dirs[2], x+dirs[3],y+dirs[4],z+dirs[5], x+dirs[6],y+dirs[7],z+dirs[8], x+dirs[9],y+dirs[10],z+dirs[11]])
            texture_data.extend(textures)
            colour_data.extend(side)
            normals.extend(norms)
            sidecount += 1
        
        fluid_side_count = 0
        fluid_vertices: list[float] = []
        fluid_texture_data: list[float] = []
        fluid_colour_data: list[int] = []
        fluid_normals: list[float] = []


        def draw_fluid(textures: tuple[float, float, float, float, float, float, float, float]):
            nonlocal fluid_side_count # immutable int -> nonlocal required
            dirs = Vertex.TOP_FLUID
            fluid_vertices.extend([x+dirs[0],y+dirs[1],z+dirs[2], x+dirs[3],y+dirs[4],z+dirs[5], x+dirs[6],y+dirs[7],z+dirs[8], x+dirs[9],y+dirs[10],z+dirs[11]])
            fluid_texture_data.extend(textures)
            fluid_colour_data.extend(Colour.TOP)
            fluid_normals.extend(Normal.TOP)
            fluid_side_count += 1

        for ox, oy, oz in xyz_range(CHUNK_RADIUS, CHUNK_RADIUS, CHUNK_RADIUS):

            x, y, z = basex + ox, basey + oy, basez + oz

            candidate = chunk[get_block_id_xyz(ox, oy, oz)]

            # if variants is set, we'll use the seeded random choice generator to select a random texture to use
            texture = (choice(candidate.variants, (x, y, z)) if candidate.variants is not None else candidate.textures)

            if texture is not None:

                # block terrain renderer
                if candidate.draw_style == DrawStyle.BLOCK:

                    # for a side to get drawn here, the block adjacent to it
                    # must be transparent and not at the world's edge (o<n> == 0 / blim)
                    # each of the patterns below checks if the side adjacent tile *in the
                    # same chunk* and then checks across chunk boundries to utilise
                    # short circuit evaluation

                    # top
                    if oy == lim or chunk[get_block_id_xyz(ox, oy + 1, oz)].transparent:
                        if oy != lim or (oy == lim and self.get_block((x, y + 1, z)).transparent):
                            draw(Colour.TOP, Vertex.TOP, texture.top, Normal.TOP)  # type: ignore
                    # bottom
                    if oy == 0 or chunk[get_block_id_xyz(ox, oy - 1, oz)].transparent:
                        if oy != 0 or (oy == 0 and self.get_block((x, y - 1, z)).transparent) and y != 0:
                            draw(Colour.BOTTOM, Vertex.BOT, texture.bottom, Normal.BOTTOM)  # type: ignore
                    # front
                    if oz == lim or chunk[get_block_id_xyz(ox, oy, oz + 1)].transparent:
                        if z != blim and (oz != lim or (oz == lim and self.get_block((x, y, z + 1)).transparent)):
                            draw(Colour.FRONT, Vertex.FRONT, texture.side, Normal.FRONT)  # type: ignore

                    # back
                    if oz == 0 or chunk[get_block_id_xyz(ox, oy, oz - 1)].transparent:
                        if z != 0 and (oz != 0 or (oz == 0 and self.get_block((x, y, z - 1)).transparent)):
                            draw(Colour.BACK, Vertex.BACK, texture.side, Normal.BACK)  # type: ignore

                    # left
                    if ox == lim or chunk[get_block_id_xyz(ox + 1, oy, oz)].transparent:
                        if x != blim and (ox != lim or (ox == lim and self.get_block((x + 1, y, z)).transparent)):
                            draw(Colour.LEFT, Vertex.LEFT, texture.side, Normal.LEFT)  # type: ignore

                    # right
                    if ox == 0 or chunk[get_block_id_xyz(ox - 1, oy, oz)].transparent:
                        if x != 0 and (ox != 0 or (ox == 0 and self.get_block((x - 1, y, z)).transparent)):
                            draw(Colour.RIGHT, Vertex.RIGHT, texture.side, Normal.RIGHT)  # type: ignore

                # grass terrain renderer
                elif candidate.draw_style == DrawStyle.GRASS:
                    n = 0.5
                    m = 0.4

                    draw(Colour.LEFT, [m, n, m, -m, n, -m, -m, -n, -m, m, -n, m], texture.top, Normal.TOP)  # type: ignore
                    draw(Colour.LEFT, [-m, n, m, m, n, -m, m, -n, -m, -m, -n, m], texture.top, Normal.TOP)  # type: ignore
                    draw(Colour.LEFT, [-m, n, -m, m, n, m, m, -n, m, -m, -n, -m], texture.top, Normal.TOP)  # type: ignore
                    draw(Colour.LEFT, [m, n, -m, -m, n, m, -m, -n, m, m, -n, -m], texture.top, Normal.TOP)  # type: ignore

                # water renderer
                elif candidate.draw_style == DrawStyle.FLUID:
                    if oy == lim or chunk[get_block_id_xyz(ox, oy + 1, oz)].transparent:
                        above = self.get_block((x, y + 1, z))
                        if (oy != lim and above != candidate) or (oy == lim and above.transparent and above != candidate):
                            draw_fluid(texture.top)

        draw_data = self.batch.add(sidecount * 4, GL_QUADS, self.group,
            ('v3f/static', vertices),
            ('t2f/static', texture_data),
            ("c4B/static", colour_data),
            ("n3f/static", normals)
        )
        draw_data_fluid = self.batch_fluid.add(fluid_side_count * 4, GL_QUADS, self.group,
            ('v3f/static', fluid_vertices),
            ('t2f/static', fluid_texture_data),
            ("c4B/static", fluid_colour_data),
            ("n3f/static", fluid_normals)
        )

        current_display = self.displayed[model_chunk_id]
        current_fluid = self.displayed_fluid[model_chunk_id]
        self.displayed[model_chunk_id] = draw_data
        self.displayed_fluid[model_chunk_id] = draw_data_fluid

        if current_display is not None:
            current_display.delete()
        if current_fluid is not None:
            current_fluid.delete()

    def get_block(self, pos: Location) -> BlockProtocol:
        
        #cx, ox = divmod(pos[0], CHUNK_RADIUS)
        #cy, oy = divmod(pos[1], CHUNK_RADIUS)
        #cz, oz = divmod(pos[2], CHUNK_RADIUS)

        cx, ox, cy, oy, cz, oz = get_chunk_and_offsets(pos)

        chunkloc = (cx, cy, cz)

        model_chunk_id = get_chunk_id(chunkloc)
        chunk_source = self.model[model_chunk_id]

        if chunk_source is None:
            return AIR

        return chunk_source.blocks[get_block_id_xyz(ox, oy, oz)]

    def add_block(self, pos: Location, block: BlockProtocol, defer: bool=False):

        #cx, ox = divmod(pos[0], CHUNK_RADIUS)
        #cy, oy = divmod(pos[1], CHUNK_RADIUS)
        #cz, oz = divmod(pos[2], CHUNK_RADIUS)

        cx, ox, cy, oy, cz, oz = get_chunk_and_offsets(pos)

        chunkloc = (cx, cy, cz)

        model_chunk_id = get_chunk_id(chunkloc)
        chunk_source = self.model[model_chunk_id]

        if chunk_source is None:
            chunk: list[BlockProtocol] = [AIR for _ in range(CHUNK_SIZE)]
            self.model[model_chunk_id] = ChunkSource(chunk, [])
        else:
            chunk = chunk_source.blocks

        chunk[get_block_id_xyz(ox, oy, oz)] = block

        if defer:
            return

        self.update_chunk(chunkloc)
    
        # update adjacent chunks

        lim = CHUNK_RADIUS - 1

        if ox == 0:
            self.update_chunk((cx - 1, cy, cz))
        if ox == lim:
            self.update_chunk((cx + 1, cy, cz))

        if oy == 0:
            self.update_chunk((cx, cy - 1, cz))
        if oy == lim:
            self.update_chunk((cx, cy + 1, cz))

        if oz == 0:
            self.update_chunk((cx, cy, cz - 1))
        if oz == lim:
            self.update_chunk((cx, cy, cz + 1))

    def remove_block(self, pos):
        self.add_block(pos, AIR)
        
    def add_creature(self, creature: CreatureWrapper):
        self.creatures.append(creature)    

    def add_creatures(self, creatures: list[CreatureWrapper]):
        self.creatures.extend(creatures)    

    def surface_height(self, x: int, z: int) -> int:
        "return surface height at a specific x:z position"
        for y in range(192):
            if self.get_block((x, y, z)) == AIR:
                return y
        raise IndexError("No surface found")
