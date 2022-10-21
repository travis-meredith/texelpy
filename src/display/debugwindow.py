
from __future__ import annotations

import time
from math import cos, radians, sin

import glm
import maths
from maths.constants import Colour
import model
import pyglet  # type: ignore
import pyshaders  # type: ignore
from blocks.blocks import AIR, LOG, WATER
from maths import get_raycast_discrete_block_hits
from pyglet import clock  # type: ignore
from pyglet import gl, graphics, shapes
from pyglet.window import key, mouse  # type: ignore

from display import gl_fixedfunction, glc
from display.constants import UV_CREATURE  # type: ignore

from .shaders import load_shader

pyshaders.transpose_matrices(False)

block_shader = load_shader("block")
water_shader = load_shader("water")
creature_shader = load_shader("creature")

class DebugWindow(pyglet.window.Window):

    __fps_display: pyglet.window.FPSDisplay

    model: model.Model

    texture_id: gl.GLuint
    noise_id: gl.GLuint

    _captured_mouse: bool = False
    camera_position: list[float] = [20., 32., 16.]
    camera_rotation: list[float] = [180., -40.]
    camera_speed: float = 20.
    keys: set[int] = set()
    sensitivity: float = 0.04
    creature_update_period: float = 1.

    __water_rect: shapes.Rectangle

    def __init__(self, *args, **kwargs):

        super(DebugWindow, self).__init__(*args, **kwargs)

        self.model = model.Model()

        clock.schedule(self.update)
        clock.schedule_interval(self.creature_update, self.creature_update_period)

        self.__water_rect = shapes.Rectangle(0, 0, *self.get_size(), color=(0, 75, 180))
        self.__fps_display = pyglet.window.FPSDisplay(window=self)
        

    @property
    def exclusive(self) -> bool:
        return self._captured_mouse

    @exclusive.setter
    def exclusive(self, exclusive: bool):
        pyglet.window.Window.set_exclusive_mouse(self, exclusive)
        self._captured_mouse = exclusive

    def on_key_press(self, symbol, modifiers):
        if symbol == key.Y:
            self.set_exclusive_mouse(True)
        elif symbol == key.U:
            self.set_exclusive_mouse(False)
        self.keys.add(symbol)

    def on_key_release(self, symbol, modifiers):
        if symbol in self.keys:
            self.keys.remove(symbol)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.exclusive:
            if button == mouse.LEFT:
                self.click()
            elif button == mouse.RIGHT:
                self.right_click()
            elif button == mouse.MIDDLE:
                self.middle_click()
        else:
            self.exclusive = True

    def on_mouse_motion(self, x, y, dx, dy):
        if self.exclusive:
            self.camera_rotation[0] += dx * self.sensitivity
            self.camera_rotation[1] += dy * self.sensitivity
            self.camera_rotation[1] = max(min(self.camera_rotation[1], 90.), -90.)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.on_mouse_motion(x, y, dx, dy)

    def _on_draw(self):
        self.clear()
        gl_fixedfunction.set_3d(
            *self.get_size(), 
            *self.get_viewport_size(), 
            *self.camera_rotation, 
            *self.camera_position
            )
        glColor3d(1, 1, 1) # type: ignore

        x, y, z = 0, 0, 0

        sidecount = 0
        vertices = []
        texture_data = []
        colour_data = []

        batch = graphics.Batch()

        n, m = 1.6, 0.4

        def draw(side, dirs, textures):
            nonlocal sidecount
            vertices.extend([x+dirs[0],y+dirs[1],z+dirs[2], x+dirs[3],y+dirs[4],z+dirs[5], x+dirs[6],y+dirs[7],z+dirs[8], x+dirs[9],y+dirs[10],z+dirs[11]])
            texture_data.extend(textures)
            colour_data.extend(side)
            sidecount += 1

        for creature_wrapper in self.model.creatures:
            creature, _ = creature_wrapper.creature, creature_wrapper.script
            x, y, z = creature.loc
            draw(Colour.LEFT, [m, n, m, -m, n, -m, -m, -n, -m, m, -n, m], UV_CREATURE)
            draw(Colour.LEFT, [-m, n, m, m, n, -m, m, -n, -m, -m, -n, m], UV_CREATURE)
            draw(Colour.LEFT, [-m, n, -m, m, n, m, m, -n, m, -m, -n, -m], UV_CREATURE)
            draw(Colour.LEFT, [m, n, -m, -m, n, m, -m, -n, m, m, -n, -m], UV_CREATURE)

        batch.add(sidecount * 4, GL_QUADS, self.model.group, # type: ignore
            ('v3f/static', vertices), 
            ('t2f/static', texture_data),
            ("c4B/static", colour_data))
            
        self.model.batch.draw()
        batch.draw()

        gl_fixedfunction.set_3d_trans(
            *self.get_size(),
            *self.get_viewport_size()
        )
        self.model.batch_fluid.draw()
        gl_fixedfunction.set_2d(
            *self.get_size(),
            *self.get_viewport_size()
        )
        if self.model.get_block((
                round(self.camera_position[0]), 
                round(self.camera_position[1]), 
                round(self.camera_position[2]))) == WATER:
            self.__water_rect.draw()
        self.__fps_display.draw()

    def on_setup(self):

        self.texture_id = glc.setup()
        global STARTTIME
        STARTTIME = time.time()
        
    def on_draw(self):

        model, view, projection = glc.get_mvp(self.get_viewport_size(), self.camera_rotation, self.camera_position) # type: ignore
        mvp = projection * view * model

        self.clear()

        block_shader.use()
        
        n = glm.normalize((0.57735, 0.57735, 0.57735))

        block_shader.uniforms.texture_sampler = self.texture_id
        block_shader.uniforms.mvp = mvp
        block_shader.uniforms.lightdirection = n.x, n.y, n.z

        glc.set_3d()

        self.model.batch.draw()

        glc.set_3d_trans()

        block_shader.clear()

        water_shader.use()

        water_shader.uniforms.intime = time.time() - STARTTIME
        water_shader.uniforms.texture_sampler = self.texture_id
        water_shader.uniforms.mvp = mvp
        water_shader.uniforms.eye = self.camera_position

        self.model.batch_fluid.draw()

        water_shader.clear()

        creature_shader.use()

        creature_shader.uniforms.mvp = mvp

        x, y, z = 0, 0, 0

        sidecount = 0
        vertices = []
        texture_data = []
        colour_data = []

        batch = graphics.Batch()

        n, m = 1.2, 0.4

        def draw(side, dirs, textures):
            nonlocal sidecount
            vertices.extend([x+dirs[0],y+dirs[1],z+dirs[2], x+dirs[3],y+dirs[4],z+dirs[5], x+dirs[6],y+dirs[7],z+dirs[8], x+dirs[9],y+dirs[10],z+dirs[11]])
            texture_data.extend(textures)
            colour_data.extend(side)
            sidecount += 1

        for creature_wrapper in self.model.creatures:
            creature, _ = creature_wrapper.creature, creature_wrapper.script
            x, y, z = creature.loc
            y += 1
            draw(creature.colour, [m, n, m, -m, n, -m, -m, -n, -m, m, -n, m], UV_CREATURE)
            draw(creature.colour, [-m, n, m, m, n, -m, m, -n, -m, -m, -n, m], UV_CREATURE)
            draw(creature.colour, [-m, n, -m, m, n, m, m, -n, m, -m, -n, -m], UV_CREATURE)
            draw(creature.colour, [m, n, -m, -m, n, m, -m, -n, m, m, -n, -m], UV_CREATURE)

        batch.add(sidecount * 4, 7, self.model.group, # type: ignore
            ('v3f/static', vertices), 
            ('t2f/static', texture_data),
            ("c4B/static", colour_data))

        batch.draw()

        creature_shader.clear()
        

    def move_horiz(self, dt: float, direction: float):
        theta = direction + self.camera_rotation[0]
        ox = self.camera_speed * dt * cos(radians(theta))
        oz = self.camera_speed * dt * sin(radians(theta))
        self.camera_position[0] -= ox
        self.camera_position[2] -= oz

    def move_verti(self, dt: float, up: int):
        self.camera_position[1] += self.camera_speed * dt * up

    def click(self):
        "left click action"
        "destroy block"
        for candidate in get_raycast_discrete_block_hits(
                self.camera_position, 
                self.camera_rotation):
            block = self.model.get_block(candidate)
            if block != AIR:
                self.model.remove_block(candidate)
                break

    def right_click(self):
        "right click action"
        "place leaves block"
        last = None
        for candidate in get_raycast_discrete_block_hits(
                self.camera_position, 
                self.camera_rotation):
            block = self.model.get_block(candidate)
            if block != AIR:
                if last is not None:
                    self.model.add_block(last, LOG)
                break
            last = candidate

    def middle_click(self):
        "middle click action"
        "inspect tile"
        print(self.camera_position)
        for candidate in get_raycast_discrete_block_hits(
                self.camera_position,
                self.camera_rotation):
            block = self.model.get_block(candidate)
            if block != AIR:
                print(candidate)
                break
        #for candidate in get_raycast_discrete_block_hits(
        #        self.camera_position, 
        #        self.camera_rotation):
        #    block = self.model.get_block(candidate)
        #    if block != AIR:
        #        vertices, start, length = self.model.get_block_vertices(candidate)
        #        def inner(dt):
        #            for i in range(start, start + length):
        #                for j in range(1):
        #                    vertices.vertices[i * 2 + j] += dt
        #        clock.schedule_interval(inner, 0.005)
        #        break

    def update(self, dt):
        "handle key-presses"
        if key.W in self.keys:
            self.move_horiz(dt, 270.)
        if key.S in self.keys:
            self.move_horiz(dt, 90.)
        if key.A in self.keys:
            self.move_horiz(dt, 180.)
        if key.D in self.keys:
            self.move_horiz(dt, 0.)
        if key.SPACE in self.keys:
            self.move_verti(dt, 1)
        if key.C in self.keys:
            self.move_verti(dt, -1)
        if key.J in self.keys:
            b = self.model.serialise()
            with open("saves/live.pickle", "wb") as file:
                file.write(b)

    def creature_update(self, dt):
        destroy = []
        for creature_wrapper in self.model.creatures:
            creature, script = creature_wrapper.creature, creature_wrapper.script
            script()
            if creature.clear():
                destroy.append(creature_wrapper)
        for creature_wrapper in destroy:
            self.model.creatures.remove(creature_wrapper)

