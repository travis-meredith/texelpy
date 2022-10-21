


import math
from math import cos, radians, sin
from typing import Generator

from numbawrapper import njit  # type: ignore

from maths.constants import (CHUNK_AREA, CHUNK_BUFFER_AREA,
                             CHUNK_BUFFER_RADIUS, CHUNK_RADIUS)
from maths.types import ChunkLocation, Location


def get_sphere_blocks(centre: tuple[int, int, int], radius: float, scalex: float = 1, scaley: float = 1, scalez: float = 1) -> Generator[tuple[int, int, int], None, None]:
    """yield locations of blocks about sphere defined at `centre` of 
    `radius` that exist within the sphere"""
    candidates = []

    diameter = math.ceil(radius * 2)

    bx, by, bz = math.ceil(-diameter * scalex), math.ceil(-diameter * scaley), math.ceil(-diameter * scalez)
    mx, my, mz = math.ceil(+diameter * scalex), math.ceil(+diameter * scaley), math.ceil(+diameter * scalez)

    r2 = radius * radius

    # bounding box locations
    for x in range(bx, mx):
        for y in range(by, my):
            for z in range(bz, mz):
                candidates.append((x, y, z))

    # filter out blocks that are outside of the circle
    for x, y, z in candidates:
        if (x * x) / scalex + (y * y) / scaley + (z * z) / scalez < r2:
            yield (centre[0] + x, centre[1] + y, centre[2] + z)

def get_raycast_discrete_block_hits(
        origin: list[float] ,
        rotation: list[float], 
        max_distance: int = 8
        ) -> Generator[tuple[int, int, int], None, None]:
    """yield locations of blocks that would be hit by a raycast 
    of `origin`, `rotation`, and `max_distance` given"""
    m = 128
    im = 1 / m 
    x, y, z = origin
    rx, ry = -radians(rotation[0]), radians(rotation[1])
    dx, dy, dz = cos(ry) * sin(rx), sin(ry), cos(ry) * cos(rx)
    #dx, dy, dz = get_sight_vector(rotation)
    last = round(origin[0]), round(origin[1]), round(origin[2])
    yield last
    for _ in range(max_distance * m):
        key = (round(x), round(y), round(z))
        if key != last:
            yield key
        x, y, z = x + dx * im, y + dy * im, z + dz * im

@njit
def get_chunk_id(chunkloc: ChunkLocation) -> int:
    "return corresponding chunk_id for a given ChunkLocation"
    return (
        (chunkloc[0] % CHUNK_BUFFER_RADIUS) * CHUNK_BUFFER_AREA 
        + (chunkloc[1] % CHUNK_BUFFER_RADIUS) * CHUNK_BUFFER_RADIUS 
        + (chunkloc[2] % CHUNK_BUFFER_RADIUS)
        )

@njit
def get_chunk_id_xyz(x: int, y: int, z: int) -> int:
    "return corresponding chunk_id for a given set of positions on the axes"
    return (
        (x % CHUNK_BUFFER_RADIUS) * CHUNK_BUFFER_AREA 
        + (y % CHUNK_BUFFER_RADIUS) * CHUNK_BUFFER_RADIUS 
        + (z % CHUNK_BUFFER_RADIUS)
        )

@njit
def get_block_id(offset_pos: tuple[int, int, int]) -> int:
    """return corresponding block_id for a given 3-tuple int describing
    the block's offset from the chunk"""
    return offset_pos[0] * CHUNK_AREA + offset_pos[1] * CHUNK_RADIUS + offset_pos[2]

@njit
def get_block_id_xyz(ox, oy, oz) -> int:
    """return corresponding block_id for a given set of positions on the axes
    from a block's offset from the chunk"""
    return ox * CHUNK_AREA + oy * CHUNK_RADIUS + oz

@njit
def get_chunk_and_offsets(loc: Location) -> tuple[int, int, int, int, int, int]:
    return *divmod(loc[0], CHUNK_RADIUS), *divmod(loc[1], CHUNK_RADIUS), *divmod(loc[2], CHUNK_RADIUS)

