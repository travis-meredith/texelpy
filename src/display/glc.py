


from math import cos, pi, radians, sin

import glm
from pyglet import image  # type: ignore
from pyglet.gl import glViewport  # type: ignore
from pyglet.gl import (GL_ALPHA_TEST, GL_BLEND, GL_CULL_FACE, GL_DEPTH_TEST,
                       GL_EQUAL, GL_NEAREST, GL_ONE, GL_ONE_MINUS_SRC_ALPHA,
                       GL_RGBA, GL_SRC_ALPHA, GL_TEXTURE_2D,
                       GL_TEXTURE_MAG_FILTER, GL_TEXTURE_MIN_FILTER,
                       GL_UNSIGNED_BYTE, GL_ZERO, GLuint, glAlphaFunc,
                       glBindTexture, glBlendFuncSeparate, glClearColor,
                       glDisable, glEnable, glTexImage2D, glTexParameteri)

from .constants import FOV, SKY_COLOUR, TEXTURE_PATH, TEXTURE_SIZE, ZFAR, ZNEAR


def setup() -> GLuint:  
    """setup gl state, load texture atlas and get texture atlas id"""
    glEnable(GL_TEXTURE_2D)
    glClearColor(*SKY_COLOUR) 
    glAlphaFunc(GL_EQUAL, 1) 

    # image addr
    id = GLuint()

    image_ = image.load(TEXTURE_PATH) 
    texture = image_.get_texture()
    glEnable(texture.target) 
    glBindTexture(texture.target, id) 
    glTexImage2D( 
        GL_TEXTURE_2D,  
        0,
        GL_RGBA,  
        TEXTURE_SIZE[0], TEXTURE_SIZE[1],  
        0,
        GL_RGBA,  
        GL_UNSIGNED_BYTE,  
        texture.get_image_data().get_data("RGBA")) 

    return id

def set_3d():
    """set gl state for 3d rendering without translucency; with transparency"""
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST) 
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST) 

    glEnable(GL_CULL_FACE) 
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_ALPHA_TEST)

    # disable translucency
    glDisable(GL_BLEND)  

def set_3d_trans():
    """set gl state for 3d rendering with translucency; without transparency"""

    # enable translucency
    glEnable(GL_BLEND)      
    #glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    #glBlendFunc(GL_ONE_MINUS_SRC_ALPHA, GL_ONE)
    glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE, GL_ZERO)
    glDisable(GL_ALPHA_TEST)
    

def get_mvp(
        view: tuple[float, float],
        rot: tuple[float, float], 
        pos: tuple[float, float, float]
        ) -> tuple[glm.mat4, glm.mat4, glm.mat4]:
    """return model, view, and projection matrices"""

    vw, vh = view
    rx, ry = -radians(rot[0]), radians(rot[1])
    position = glm.vec3(*pos)

    glViewport(0, 0, max(1, vw), max(1, vh)) 

    # direction vector from camera perspective in model space
    direction = glm.vec3(
        cos(ry) * sin(rx),
        sin(ry),
        cos(ry) * cos(rx)
        )

    # direction vector perpendicular on the y plane to the camera
    # perspective direction vector
    right = glm.vec3(
        sin(rx - pi / 2),
        0,
        cos(rx - pi / 2)
    )

    # up from camera perspective
    up = glm.cross(right, direction)

    projection_matrix = glm.perspective(FOV, vw / vh, ZNEAR, ZFAR)
    view_matrix = glm.lookAt(position, position + direction, up)
    model_matrix = (glm.mat4(1.))

    return model_matrix, view_matrix, projection_matrix
