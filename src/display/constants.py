

from math import radians
from maths.bufferdomain import tex_coord

TEXTURE_PATH = "textures/textures.png"
TEXTURE_SIZE = 256, 256

UV_CREATURE = tex_coord(1, 3)

SKY_COLOUR = 0.5, 0.69, 1., 1.

# fov in radians
FOV = radians(100.)

ZNEAR, ZFAR = 0.1, 600.