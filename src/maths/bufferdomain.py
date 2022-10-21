
from .types import Number, TextureGrid
from functools import lru_cache

@lru_cache(maxsize=16)
def ls16(v):
    "return 16-int list of v (alpha channel is 255)"
    return [v, v, v, 255] * 4

@lru_cache(maxsize=16)
def l(a):
    return int(255 * a)

@lru_cache(maxsize=256)
def colour_data(a: float = 1) -> list[int]:
    result = []
    result.extend(ls16(l(0.9 * a)))
    result.extend(ls16(l(0.5)))
    result.extend(ls16(l(0.8)))
    result.extend(ls16(l(0.55)))
    result.extend(ls16(l(0.65)))
    result.extend(ls16(l(0.7)))
    return result

@lru_cache(maxsize=256)
def tex_coord(x: Number, y: Number, n: int=16) -> TextureGrid:
    """ Return the bounding vertices of the texture square.

    """
    m = 1.0 / n
    dx = x * m
    dy = y * m
    return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m
