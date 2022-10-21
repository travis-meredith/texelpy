
import random
from contextlib import suppress
from sys import argv
from typing import Callable

import pyglet  # type: ignore

import maths
from ai import Creature
from blocks.blocks import APPLE_LEAVES
from creatureapi import ModelAPIProtocol, create_model_api
from display import DebugWindow
from maths import DIRECTIONS
from model import CreatureWrapper, DefaultWorldGenerationConfig
from model.worldgenconfig import HighFlatLandConfig

def generate_ai_script(
        model_api: ModelAPIProtocol, 
        script: Callable[[ModelAPIProtocol], None]
        ) -> Callable[[], None]:
    def inner():
        script(model_api)
    return inner

def ai_script(model_api: ModelAPIProtocol):
    "ai that walks randomly"
    x, y, z = model_api.get_loc()
    direction = random.choice(DIRECTIONS)
    model_api.try_walk(direction)

def apple_picker(model_api: ModelAPIProtocol):
    "ai that walks randomly and scans a 5-metre radius of APPLE_LEAVES to pick"
    x, y, z = loc = model_api.get_loc()
    search_sphere = maths.blocks.get_sphere_blocks(loc, 5)
    direction = random.choice(DIRECTIONS)
    model_api.try_walk(direction)
    for tileloc in search_sphere:
        block = model_api.get_block(tileloc)
        if block == APPLE_LEAVES:
            model_api.try_mine(tileloc)
    #if random.randint(1, 5) == 5:
    #    print(model_api.get_inventory())
    #    print(model_api.try_eat(items.APPLE))
    #    print(model_api.get_inventory())

def instance(world_generation: bool):
    # world loading / generation
    window = DebugWindow(width=1600, height=900, caption="MinePy", resizable=False)
    config = DefaultWorldGenerationConfig()
    if world_generation:
        window.model.generate(config)
    else:
        with open("saves/live.pickle", "rb") as file:
            window.model.deserialise(file.read())

    # creature instantiation
    sx, sz = 16, 20
    mx = sx + 8
    creature_positions = [(x, window.model.surface_height(x, sz), sz) for x in range(sx, mx)]
    creatures = [Creature(loc, colour=maths.rng.random_rgb()) for loc in creature_positions]
    model_apis = [create_model_api(window.model, creature) for creature in creatures]
    scripts = [generate_ai_script(model_api, apple_picker) for model_api in model_apis]
    wrapped_creatures = [CreatureWrapper(creature, script) for creature, script in zip(creatures, scripts)]
    window.model.add_creatures(wrapped_creatures)

    # window setup
    window.camera_position = [10, window.model.surface_height(10, 10) + 5, 10]
    window.camera_rotation = [0, 0]
    window.exclusive = True
    window.on_setup()

    # run
    pyglet.app.run()

if __name__ == "__main__":
    world_generation_flag = True
    with suppress(Exception):
        world_generation_flag = not bool(int(argv[1]))
    instance(world_generation_flag)

