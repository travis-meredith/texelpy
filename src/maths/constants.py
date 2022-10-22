
from configparser import ConfigParser

from .bufferdomain import l, ls16

config = ConfigParser()
with open("./advancedsettings.ini", "r") as config_file:
    config.read_file(config_file)


V_UP = (0, 1, 0)
V_DOWN = (0, -1, 0)
V_FRONT = (0, 0, 1)
V_BACK = (0, 0, -1)
V_LEFT = (1, 0, 0)
V_RIGHT = (-1, 0, 0)
V_TABLE = [V_UP, V_DOWN, V_FRONT, V_BACK, V_LEFT, V_RIGHT]

DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]

CHUNK_RADIUS: int = config.getint("MODEL", "ChunkSize", fallback=16)
CHUNK_BUFFER_RADIUS: int = config.getint("MODEL", "ChunkBufferSize", fallback=128)

CHUNK_AREA: int = CHUNK_RADIUS ** 2
CHUNK_SIZE: int = CHUNK_RADIUS ** 3

CHUNK_BUFFER_AREA: int = CHUNK_BUFFER_RADIUS ** 2
CHUNK_BUFFER_SIZE: int = CHUNK_BUFFER_RADIUS ** 3

n = config.getfloat("BLOCK", "BlockVertexSize", fallback=0.5)
m = config.getfloat("BLOCK", "FluidVertexSize", fallback=0.35)

T, B, L, R, F, B = (
    config.getfloat("COLOUR_SCALE", "Top", fallback=0.9),
    config.getfloat("COLOUR_SCALE", "Bottom", fallback=0.5),
    config.getfloat("COLOUR_SCALE", "Left", fallback=0.8),
    config.getfloat("COLOUR_SCALE", "Right", fallback=0.55),
    config.getfloat("COLOUR_SCALE", "Front", fallback=0.65),
    config.getfloat("COLOUR_SCALE", "Back", fallback=0.7)
)

class Colour:
    """Vertex Colour Data"""
    TOP = ls16(l(T))
    BOTTOM = ls16(l(B))
    LEFT = ls16(l(L))
    RIGHT = ls16(l(R))
    FRONT = ls16(l(F))
    BACK = ls16(l(B))

class Vertex:
    """Vertex Position Data"""
    TOP = [
        -n, +n, -n,
        -n, +n, +n,
        +n, +n, +n,
        +n, +n, -n
    ]
    TOP_FLUID = [
        -n, +m, -n,
        -n, +m, +n,
        +n, +m, +n,
        +n, +m, -n
    ]
    BOT = [
        -n, -n, -n,
        n, -n, -n,
        n, -n, n,
        -n, -n, n
    ]
    FRONT = [
        -n, -n, n,
        n, -n, n,
        n, n, n,
        -n, n, n
    ]
    BACK = [
        n, -n, -n,
        -n, -n, -n,
        -n, n, -n,
        n, n, -n
    ]
    LEFT = [
        n, -n, n,
        n, -n, -n,
        n, n, -n,
        n, n, n
    ]
    RIGHT = [
        -n, -n, -n,
        -n, -n, n,
        -n, n, n,
        -n, n, -n
    ]

class Normal:
    """Vertex Normal Data"""
    TOP = [
        0, 1, 0,
        0, 1, 0,
        0, 1, 0,
        0, 1, 0
    ]
    BOTTOM = [
        0, -1, 0,
        0, -1, 0,
        0, -1, 0,
        0, -1, 0,
    ]
    FRONT = [
        0, 0, 1,
        0, 0, 1,
        0, 0, 1,
        0, 0, 1,
    ]
    BACK = [
        0, 0, -1,
        0, 0, -1,
        0, 0, -1,
        0, 0, -1
    ]
    LEFT = [
        1, 0, 0,
        1, 0, 0,
        1, 0, 0,
        1, 0, 0,
    ]
    RIGHT=  [
        -1, 0, 0,
        -1, 0, 0,
        -1, 0, 0,
        -1, 0, 0,
    ]
    
