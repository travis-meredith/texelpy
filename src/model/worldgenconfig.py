import random
from collections import namedtuple
from typing import Callable, Protocol, TypeAlias

from blocks import BlockProtocol
from blocks.blocks import (AIR, APPLE_LEAVES, BERRY_BUSH, CLAY,  # type: ignore
                           CORNFLOWER, DIRT, GRASS, LEAVES, POPPY, STONE,
                           TALL_GRASS, Log, Sand, Water)

TileProvider: TypeAlias = Callable[[], BlockProtocol]

TileProviders = namedtuple("TileProviders",
                           [
                               "water_tile_provider",
                               "subaqua_tile_provider",
                               "water_feature_tile_provider",
                               "log_tile_provider",
                               "leaves_tile_provider",
                               "foliage_tile_provider"
                           ])


class WorldGenerationConfigProtocol(Protocol):
    dims: tuple[int, int]
    height_base: int
    water_height: int

    water_feature_chance: float
    water_feature_min_radius: int
    water_feature_max_radius: int

    tree_feature_chance: float

    foliage_feature_chance: float

    scale_noise_function_input: float
    perlin_noise_poller_octaves: list[int]
    perlin_noise_poller_mux: list[float]
    scale_noise_function_output: float

    air_tile: BlockProtocol
    base_tile: BlockProtocol
    subterranean_tile: BlockProtocol
    surface_tile: BlockProtocol

    water_tile_provider: TileProvider
    subaqua_tile_provider: TileProvider
    water_feature_tile_provider: TileProvider

    log_tile_provider: TileProvider
    leaves_tile_provider: TileProvider

    foliage_tile_provider: TileProvider

    tile_providers: TileProviders

class DefaultWorldGenerationConfig(WorldGenerationConfigProtocol):
    dims = (16, 16)
    height_base = 40
    water_height = 40

    water_feature_chance = 0.01
    water_feature_min_radius = 3
    water_feature_max_radius = 6

    tree_feature_chance = 0.02

    foliage_feature_chance = 0.5

    scale_noise_function_input = 12 / 256
    perlin_noise_poller_octaves = [2, 4, 9, 13]
    perlin_noise_poller_mux = [0.75, 0.75, 0.25, 0.25]
    scale_noise_function_output = 24.

    air_tile = AIR
    base_tile = STONE
    subterranean_tile = DIRT
    surface_tile = GRASS

    water_tile_provider = Water
    subaqua_tile_provider = Sand
    water_feature_tile_provider = lambda: random.choice([CLAY, DIRT, STONE])
    log_tile_provider = Log
    leaves_tile_provider = lambda: random.choice([
        LEAVES, LEAVES, LEAVES, LEAVES,
        LEAVES, LEAVES, LEAVES, LEAVES,
        LEAVES, LEAVES, LEAVES, LEAVES,
        LEAVES, LEAVES, LEAVES, LEAVES,
        LEAVES, LEAVES, LEAVES, LEAVES,
        LEAVES, LEAVES, LEAVES, LEAVES,
        LEAVES, LEAVES, LEAVES, LEAVES,
        LEAVES, LEAVES, LEAVES, LEAVES,
        LEAVES, LEAVES, LEAVES, LEAVES,
        LEAVES, LEAVES, LEAVES, LEAVES,
        LEAVES, LEAVES, LEAVES, LEAVES,
        LEAVES, LEAVES, LEAVES, LEAVES,
        APPLE_LEAVES
    ])

    foliage_tile_provider = lambda: random.choice([
        TALL_GRASS, TALL_GRASS, TALL_GRASS, TALL_GRASS,
        TALL_GRASS, TALL_GRASS, TALL_GRASS, TALL_GRASS,
        TALL_GRASS, TALL_GRASS, TALL_GRASS, TALL_GRASS,
        TALL_GRASS, TALL_GRASS, TALL_GRASS, TALL_GRASS,
        TALL_GRASS, TALL_GRASS, TALL_GRASS, TALL_GRASS,
        TALL_GRASS, TALL_GRASS, TALL_GRASS, TALL_GRASS,
        TALL_GRASS, TALL_GRASS, TALL_GRASS, TALL_GRASS,
        TALL_GRASS, TALL_GRASS, TALL_GRASS, TALL_GRASS,
        TALL_GRASS, TALL_GRASS, TALL_GRASS, TALL_GRASS,
        TALL_GRASS, TALL_GRASS, TALL_GRASS, TALL_GRASS,
        TALL_GRASS, TALL_GRASS, TALL_GRASS, TALL_GRASS,
        TALL_GRASS, TALL_GRASS, TALL_GRASS, TALL_GRASS,
        TALL_GRASS, TALL_GRASS, TALL_GRASS, TALL_GRASS,
        TALL_GRASS, TALL_GRASS, TALL_GRASS, TALL_GRASS,
        TALL_GRASS, TALL_GRASS, TALL_GRASS, TALL_GRASS,
        TALL_GRASS, TALL_GRASS, TALL_GRASS, TALL_GRASS,
        TALL_GRASS, TALL_GRASS, TALL_GRASS, TALL_GRASS,
        TALL_GRASS, TALL_GRASS, TALL_GRASS, TALL_GRASS,
        TALL_GRASS, TALL_GRASS, TALL_GRASS, TALL_GRASS,
        TALL_GRASS, TALL_GRASS, TALL_GRASS, TALL_GRASS,
        CORNFLOWER, POPPY, BERRY_BUSH, CORNFLOWER,
        POPPY, POPPY
    ])

    tile_providers = TileProviders(water_tile_provider, subaqua_tile_provider, water_feature_tile_provider,
                                   log_tile_provider, leaves_tile_provider, foliage_tile_provider)

class HighFlatLandConfig(DefaultWorldGenerationConfig):

    height_base = 60
    water_height = 20
