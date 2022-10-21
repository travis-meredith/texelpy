
from __future__ import annotations

from typing import TypeVar

Number = TypeVar("Number", int, float)

Position = tuple[float, float, float]
Vector2 = tuple[float, float]

TextureGrid = tuple[Number, Number, Number, Number, Number, Number, Number, Number]

Direction = tuple[int, int]

Location = tuple[int, int, int]

# BlockProtocol
# 

# Chunk

# Chunk is a list of 16 * 16 * 16 (4096) Blocks
# Position 0, 0, 0 is index 0
# Position x, y, z is index x * 256 + y * 16 + z

ChunkLocation = tuple[int, int, int]

# Model

# Model is a list of 64 * 64 * 64 (262 144) chunks
# Chunk Position 0, 0, 0 is index 0
# Chunk Position x, y, z is index (x % 64) * 4096 + (y % 64) * 64 + (z % 64)
