

from configparser import ConfigParser
from math import radians
from maths.bufferdomain import tex_coord

config = ConfigParser()
with open("./displaysettings.ini", "r") as config_file:
    config.read_file(config_file)

TEXTURE_PATH = "textures/textures.png"
TEXTURE_SIZE = 256, 256

UV_CREATURE = tex_coord(1, 3)

sr = config.getfloat("SKY_COLOUR", "Red", fallback=0.5)
sg = config.getfloat("SKY_COLOUR", "Green", fallback=0.69)
sb = config.getfloat("SKY_COLOUR", "Blue", fallback=1.)
sa = config.getfloat("SKY_COLOUR", "Alpha", fallback=1.)
SKY_COLOUR = sr, sg, sb, sa

# fov in radians
FOV = radians(config.getfloat("DEBUG_WINDOW", "FieldOfView", fallback=100.))

ZNEAR = config.getfloat("DEBUG_WINDOW", "ZNEAR", fallback=0.1)
ZFAR = config.getfloat("DEBUG_WINDOW", "ZFAR", fallback=600.)