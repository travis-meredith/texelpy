
__all__ = ["perlin"]

# https://en.wikipedia.org/wiki/Perlin_noise
# implementation based on this

import math

from numbawrapper import njit  # type: ignore

from .types import Vector2  # type: ignore


@njit
def lerp(start: float, end: float, time: float) -> float:
    return (end - start) * time + start

@njit
def random_gradient_function(ix: int, iy: int) -> Vector2:
    w = 32
    s = 16
    a, b = ix, iy
    a *= 3284157443
    b ^= a << s | a >> w - s
    b *= 1911520717
    a ^= b << s | b >> w - s
    a *= 2048419325
    random = a * (math.pi / ~(~0 >> 1))
    return math.cos(random), math.sin(random)

@njit
def dot_grid_gradient(ix: int, iy: int, x: float, y: float) -> float:
    gradient = random_gradient_function(ix, iy)
    dx, dy = x - ix, y - iy
    return (dx * gradient[0] + dy * gradient[1])

@njit
def perlin(x: float, y: float) -> float:

    x0 = int(x)
    x1 = x0 + 1
    y0 = int(y)
    y1 = y0 + 1

    sx = x - x0
    sy = y - y0

    n0 = dot_grid_gradient(x0, y0, x, y)
    n1 = dot_grid_gradient(x1, y0, x, y)
    ix0 = lerp(n0, n1, sx)

    n0 = dot_grid_gradient(x0, y1, x, y)
    n1 = dot_grid_gradient(x1, y1, x, y)
    ix1 = lerp(n0, n1, sx)

    return lerp(ix0, ix1, sy)


