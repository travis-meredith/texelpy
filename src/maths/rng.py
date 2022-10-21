

import random
from typing import TypeVar

from .types import Location

T = TypeVar("T")

def prob(chance: float) -> bool:
    "shorthand for random.random() < chance"
    return random.random() < chance

def choice(seq: list[T], loc: Location) -> T:
    "return seeded random.choice (uses tile location as a seed)"
    r = random.getstate()
    random.seed((loc[0] * 83) + (loc[1] * 41) + (loc[2] * 23))
    choice = random.choice(seq)
    random.setstate(r)
    return choice

def random_rgb() -> tuple[int, int, int]:
    "return random rgb colour"
    return (
        random.randint(0, 255), 
        random.randint(0, 255), 
        random.randint(0, 255)
        )

def random_rgba() -> tuple[int, int, int, int]:
    "return random rgba colour"
    return (
        random.randint(0, 255),
        random.randint(0, 255), 
        random.randint(0, 255), 
        random.randint(0, 255)
        )
