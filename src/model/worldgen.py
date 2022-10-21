

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import cast

import numpy as np
import opensimplex  # type: ignore
from blocks.blocks import AIR, GRASS, SAND
from maths.blocks import (get_block_id_xyz, get_chunk_and_offsets,
                          get_chunk_id, get_chunk_id_xyz, get_sphere_blocks)
from maths.constants import CHUNK_AREA, CHUNK_RADIUS, CHUNK_SIZE
from maths.generators import xy_range, xyz_range
from maths.rng import prob
from maths.types import Location
from tqdm import tqdm  # type: ignore

from model.modelprotocol import ChunkSource, ModelProtocol  # type: ignore
from model.worldgenconfig import WorldGenerationConfigProtocol


@dataclass
class GenerateWorldResult:
    mxz: tuple[int, int] # <Model>.dims equivalent
    height_map: dict[tuple[int, int], int]
    surface_tiles: list[Location]

def generate_world(model: ModelProtocol, config: WorldGenerationConfigProtocol) -> GenerateWorldResult:
    "using supplied dims and mux, generate and render a new world"

    dims = config.dims
    height_base = config.height_base
    water_height = config.water_height

    water_feature_chance = config.water_feature_chance
    water_feature_min_radius = config.water_feature_min_radius
    water_feature_max_radius = config.water_feature_max_radius

    tree_feature_chance = config.tree_feature_chance

    foliage_feature_chance = config.foliage_feature_chance

    scale_noise_function_input = config.scale_noise_function_input
    perlin_noise_poller_octaves = config.perlin_noise_poller_octaves
    perlin_noise_poller_mux = config.perlin_noise_poller_mux
    scale_noise_function_output = config.scale_noise_function_output

    air_tile = config.air_tile
    base_tile = config.base_tile
    sub_terrainian_tile = config.subterranean_tile
    surface_tile = config.surface_tile

    water_tile_provider = config.tile_providers.water_tile_provider # type: ignore
    subaqua_tile_provider = config.tile_providers.subaqua_tile_provider # type: ignore
    water_feature_tile_provider = config.tile_providers.water_feature_tile_provider # type: ignore

    log_tile_provider = config.tile_providers.log_tile_provider # type: ignore
    leaves_tile_provider = config.tile_providers.leaves_tile_provider # type: ignore
    
    foliage_tile_provider = config.tile_providers.foliage_tile_provider # type: ignore

    chunkx, chunky, chunkz = dims[0], 12, dims[1]

    linspaces = [(
        np.linspace(0, chunkx * octave * scale_noise_function_input, chunkx * CHUNK_RADIUS), 
        np.linspace(0, chunkz * octave * scale_noise_function_input, chunkz * CHUNK_RADIUS)) 
        for octave in perlin_noise_poller_octaves
                ]

    opensimplex.seed(random.randint(0, 1_000_000))

    noises = [opensimplex.noise2array(ls0, ls1) for ls0, ls1 in tqdm(linspaces, "generating noise textures")]

    surface_tiles: list[Location] = []
    height_map: dict[tuple[int, int], int] = {}

    for chunkloc in tqdm(xyz_range(chunkx, chunky, chunkz), "chunk pregen", total=chunkx * chunky * chunkz): # type: ignore
        model.model[get_chunk_id(chunkloc)] = ChunkSource([air_tile for _ in range(CHUNK_SIZE)], []) # type: ignore

    with tqdm(total=CHUNK_AREA * chunkx * chunkz, desc="generating blocks") as progress_bar:
        for x, z in xy_range(chunkx * CHUNK_RADIUS, chunkz * CHUNK_RADIUS):
            height = height_base + int(scale_noise_function_output * sum(noise[x][z] * mux for noise, mux in zip(noises, perlin_noise_poller_mux)))
            for y in range(height):
                tile = base_tile
                if y > height - 4:
                    tile = sub_terrainian_tile
                if y == height - 1:
                    tile = surface_tile
                    height_map[((x, z))] = y
                    surface_tiles.append((x, y, z))
                if y < water_height:
                    tile = base_tile
                    if y == height - 1:
                        surface_tiles.append((x, y, z))
                cx, ox, cy, oy, cz, oz = get_chunk_and_offsets((x, y, z))
                chunk = cast(ChunkSource, model.model[get_chunk_id_xyz(cx, cy, cz)]).blocks
                chunk[get_block_id_xyz(ox, oy, oz)] = tile
            progress_bar.update(1)
        
    #for chunkloc, chunk in chunkslist: # type: ignore
    #    model_chunk_id = get_chunk_id(chunkloc) # type: ignore
    #    model.model[model_chunk_id] = ChunkSource(chunk, []) # type: ignore
    water_subgen: list[tuple[int, int, int]] = []
    # water gen
    for x, y, z in tqdm(surface_tiles, "placing water"):
        if y < water_height:
            for dy in  range(y - 2, y + 1):
                model.add_block((x, dy, z), subaqua_tile_provider(), defer=True)
            for dy in range(y + 1, water_height + 1):
                model.add_block((x, dy, z), water_tile_provider(), defer=True)
            #height_map[(x, y)] = water_height
            # feature subgen
            if prob(water_feature_chance):
                water_subgen.append((x, y, z))
    # feature subgen
    for x, y, z in tqdm(water_subgen, "placing water features"):
        target_block = water_feature_tile_provider()
        scaler = random.random() * 1.6
        for spot in get_sphere_blocks(
                (x, y + random.randint(-2, 2), z), 
                random.randint(
                    water_feature_min_radius, 
                    water_feature_max_radius
                ),
                scalex=random.random() * 2.6 * scaler,
                scaley=random.random() * 1.4 * scaler,
                scalez=random.random() * 2.6 * scaler
                ):
            if model.get_block(spot) == SAND:
                model.add_block(spot, target_block, defer=True)
    # tree gen
    for x, y, z in tqdm(surface_tiles, "generating trees"):
        if prob(tree_feature_chance) and model.get_block((x, y, z)) == GRASS:
            oy = 0
            log = log_tile_provider()
            for oy in range(random.randint(3, 5)):
                model.add_block((x, y + oy, z), log, defer=True)
            for spot in filter(
                    lambda pos: pos[1] > y + oy - 1, 
                    get_sphere_blocks(
                        (x, y + oy, z), 
                        0.5 + random.randint(2, 4),
                        scalex=0.8, scalez=0.8
                        )):
                if model.get_block(spot) == AIR:
                    leaves = leaves_tile_provider()
                    model.add_block(spot, leaves, defer=True)
    # grass / poppy / cornflower gen
    for x, y, z in tqdm(surface_tiles, "generating foliage"):
        if (
                    prob(foliage_feature_chance) 
                and model.get_block((x, y, z)) == GRASS 
                and model.get_block((x, y + 1, z)) == AIR):
            model.add_block((x, y + 1, z), foliage_tile_provider(), defer=True)
    # rendering chunks
    #for chunkloc in tqdm(xyz_range(chunkx, chunky, chunkz), "updating chunks", total=chunkx * chunky * chunkz): # type: ignore
    #    model.update_chunk(chunkloc) # type: ignore

    return GenerateWorldResult(dims, height_map, surface_tiles)
