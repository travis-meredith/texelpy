
from math import cos, radians, sin

from pyglet.gl import *  # type: ignore

def set_2d(width: int, height: int, vwidth: float, vheight: float):
    glDisable(GL_DEPTH_TEST) # type: ignore
    glViewport(0, 0, max(1, vwidth), max(1, vheight)) # type: ignore
    glMatrixMode(GL_PROJECTION) # type: ignore
    glLoadIdentity() # type: ignore
    glOrtho(0, max(1, width), 0, max(1, height), -1, 1) # type: ignore
    glMatrixMode(GL_MODELVIEW) # type: ignore
    glLoadIdentity() # type: ignore

def set_3d(width: int, height: int, vwidth: float, vheight: float, rotx: float, roty: float, posx: float, posy: float, posz: float):
    glEnable(GL_CULL_FACE) # type: ignore
    glEnable(GL_DEPTH_TEST) # type: ignore
    glEnable(GL_BLEND) # type: ignore
    glEnable(GL_ALPHA_TEST) # type: ignore
    glViewport(0, 0, max(1, vwidth), max(1, vheight)) # type: ignore
    glMatrixMode(GL_PROJECTION) # type: ignore
    glLoadIdentity() # type: ignore
    gluPerspective(100., width / float(height), 0.05, 1200.) # type: ignore
    glMatrixMode(GL_MODELVIEW) # type: ignore
    glLoadIdentity() # type: ignore
    glRotatef(rotx, 0, 1, 0) # type: ignore
    glRotatef(-roty, cos(radians(rotx)), 0, sin(radians(rotx))) # type: ignore
    glTranslatef(-posx, -posy, -posz) # type: ignore

def set_3d_trans(width: int, height: int, vwidth: float, vheight: float):
    glEnable(GL_BLEND)# type: ignore 
    glDisable(GL_ALPHA_TEST)# type: ignore 
    #glDisable(GL_DEPTH_TEST)

def set_draw(width: int, height: int, vwidth: float, vheight: float, rotx: float, roty: float, posx: float, posy: float, posz: float):
    glMatrixMode(GL_PROJECTION) # type: ignore
    glLoadIdentity() # type: ignore
    gluPerspective(100., width / float(height), 0.05, 300.0) # type: ignore
    glMatrixMode(GL_MODELVIEW) # type: ignore
    glLoadIdentity() # type: ignore
    glRotatef(rotx, 0, 1, 0) # type: ignore
    glRotatef(-roty, cos(radians(rotx)), 0, sin(radians(rotx))) # type: ignore
    glTranslatef(-posx, -posy, -posz) # type: ignore

def setup(): # type: ignore
    glClearColor(0.5, 0.69, 1., 1.) # type: ignore
    glEnable(GL_CULL_FACE) # type: ignore
    glEnable(GL_DEPTH_TEST) # type: ignore
    glEnable(GL_BLEND) # type: ignore
    glEnable(GL_ALPHA_TEST) # type: ignore 
    glAlphaFunc(GL_EQUAL, 1) # type: ignore 
    glBlendFunc(GL_ONE, GL_ONE) # type: ignore 
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST) # type: ignore 
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST) # type: ignore 
    #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, 8) # type: ignore 
     
