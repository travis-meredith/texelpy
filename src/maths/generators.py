
from typing import Generator

from .types import Location


def xy_range(mx: int, my: int) -> Generator[tuple[int, int], None, None]:
    """equivalent to
    for x in range(mx):
        for y in range(my):
            ...
    """
    for x in range(mx):
        for y in range(my):
            yield x, y

def xyz_range(mx: int, my: int, mz: int) -> Generator[Location, None, None]:
    """equivalent to
    for x in range(mx):
        for y in range(my):
            for z in range(mz):
                ...
    """
    for x in range(mx):
        for y in range(my):
            for z in range(mz):
                yield x, y, z
