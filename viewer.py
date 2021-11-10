from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame as pg
import numpy as np
import math
import time

from pygame.locals import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from typing import List, Union

from object_renderer import ObjectRenderer, RenderMethod
from utils import normalize_vector
from object import Object

# Define constants
W, H = 800, 600
FOV = 45
DISTANCE = -3
Z_NEAR, Z_FAR = 0.1, 50.0
FPS = 60

SCALE_FACTOR = 1.1
MOUSE_MOVE_X = np.array([0.05, 0, 0])
MOUSE_MOVE_Y = np.array([0, 0.05, 0])
KEY_MOVE_X = np.array([0.01, 0, 0])
KEY_MOVE_Y = np.array([0, 0.01, 0])

class Viewer:
    # Initializer for the Viewer
    def __init__(self, objects: Union[Object, List[Object]]):
        # Set veriables to be used within the viewer
        if type(objects) is list:
            self.objects = objects
        else:
            self.objects = [objects]

        self.object_renderers = list(map(ObjectRenderer, self.objects))
        self.clock = pg.time.Clock()
        self.keys_pressed_last_frame = []

        self.scale = np.array([1.0, 1.0, 1.0])
        self.position = np.array([0.0, 0.0, 0.0])
        self.rotation = (0.0, np.array([0.0, 0.0, 0.0]))
        self.angle_x = 0
        self.angle_y = 0
        self.render_method = RenderMethod.FLAT
        self.wireframe = True
        self.axis_shown = False

        self.has_quit = False

        caption = "Model #" + str(self.object.model_num) + " - label: " + self.object.label

        # Initialize a window
        pg.init()
        pg.display.set_mode((W,H), DOUBLEBUF|OPENGL|RESIZABLE)
        pg.display.set_caption(caption)
        pg.key.set_repeat(int(1000 / FPS))

        # Set the perspective and move the "camera" back
        glMatrixMode(GL_PROJECTION)
        gluPerspective(FOV, (W/H), Z_NEAR, Z_FAR)
        glTranslatef(0.0, 0.0, DISTANCE)

    # Handle pygame events
    def handleEvents(self):
        for event in pg.event.get():
            # Close window when the red X is pressed
            if event.type == pg.QUIT:
                self.has_quit = True
                for object_renderer in self.object_renderers:
                    del object_renderer
            elif event.type == pg.MOUSEBUTTONDOWN:
                # Scroll down
                if event.button == 4:
                    self.scale *= SCALE_FACTOR
                # Scroll up
                if event.button == 5:
                    self.scale /= SCALE_FACTOR
            elif event.type == pg.MOUSEBUTTONUP:
                # Stop dragging
                if event.button == 1:
                    self.rotation = (self.rotation[0] % 360, normalize_vector(self.rotation[1]))
            elif event.type == pg.MOUSEMOTION:
                # If LMB is held
                if event.buttons[0]:
                    # Turn dragging motion into object rotation
                    diff_x, diff_y = event.rel

                    self.angle_x += diff_x
                    self.angle_y += diff_y

                # If RMB is held
                if event.buttons[2]:
                    # Turn dragging motion into object panning
                    diff_x, diff_y = event.rel

                    self.position += MOUSE_MOVE_X * diff_x / self.scale[0] / 10
                    self.position -= MOUSE_MOVE_Y * diff_y / self.scale[0] / 10
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_w or event.key == pg.K_UP:
                    self.position -= np.array(KEY_MOVE_Y)
                if event.key == pg.K_s or event.key == pg.K_DOWN:
                    self.position += np.array(KEY_MOVE_Y)
                if event.key == pg.K_a or event.key == pg.K_LEFT:
                    self.position += np.array(KEY_MOVE_X)
                if event.key == pg.K_d or event.key == pg.K_RIGHT:
                    self.position -= np.array(KEY_MOVE_X)
                if event.key == pg.K_1 and not self.keys_pressed_last_frame[pg.K_1]:
                    self.render_method = RenderMethod.POINT_CLOUD
                    self.timer = 0
                    print("Point cloud")
                if event.key == pg.K_2 and not self.keys_pressed_last_frame[pg.K_2]:
                    self.render_method = RenderMethod.NO_SHADING
                    self.timer = 0
                    print("No shading")
                if event.key == pg.K_3 and not self.keys_pressed_last_frame[pg.K_3]:
                    self.render_method = RenderMethod.FLAT
                    self.timer = 0
                    print("Flat shading")
                if event.key == pg.K_4 and not self.keys_pressed_last_frame[pg.K_4]:
                    self.render_method = RenderMethod.SMOOTH
                    self.timer = 0
                    print("Smooth shading")
                if event.key == pg.K_e and not self.keys_pressed_last_frame[pg.K_e]:
                    self.wireframe = not self.wireframe
                    if self.wireframe:
                        print("Enabled wireframe")
                    else:
                        print("Disabled wireframe")
                if event.key == pg.K_t and not self.keys_pressed_last_frame[pg.K_t]:
                    self.axis_shown = not self.axis_shown
                    if self.axis_shown:
                        print("Enabled axis visuals")
                    else:
                        print("Disabled axis visuals")
                if event.key == pg.K_F12 and not self.keys_pressed_last_frame[pg.K_F12]:
                    window_size = pg.display.get_window_size()
                    screen_buffer = glReadPixels(0, 0, *window_size, GL_RGBA, GL_UNSIGNED_BYTE)
                    screen = pg.image.fromstring(screen_buffer, window_size, "RGBA", 1)

                    t = time.localtime(time.time())
                    pg.image.save(screen, f"screenshots/{t.tm_year:04d}-{t.tm_mon:02d}-{t.tm_mday:02d}_{t.tm_hour:02d}.{t.tm_min:02d}.{t.tm_sec:02d}.png")
                if event.key == pg.K_r and not self.keys_pressed_last_frame[pg.K_r]:
                    self.angle_x = round(self.angle_x / 15) * 15
                    self.angle_y = round(self.angle_y / 15) * 15
                if event.key == pg.K_PAGEUP and not self.keys_pressed_last_frame[pg.K_PAGEUP]:
                    for obj in self.objects:
                        obj.subdivide()
                    for object_renderer in self.object_renderers:
                        object_renderer.update_vbos()
                if event.key == pg.K_PAGEDOWN and not self.keys_pressed_last_frame[pg.K_PAGEDOWN]:
                    for obj in self.objects:
                        obj.simplify()
                    for object_renderer in self.object_renderers:
                        object_renderer.update_vbos()
            if event.type == pg.VIDEORESIZE:
                glMatrixMode(GL_PROJECTION)
                glLoadIdentity()
                gluPerspective(FOV, (event.w/event.h), Z_NEAR, Z_FAR)
                glTranslatef(0.0, 0.0, DISTANCE)

        self.keys_pressed_last_frame = pg.key.get_pressed()

    def mainLoop(self):
        while True:
            # Handle all pygame events
            self.handleEvents()

            if self.has_quit:
                break

            # Limit FPS
            self.clock.tick(FPS)

            # Clear the window
            glClearColor(0.75, 1, 1, 1)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # Reset view
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            # Enable depth rendering
            # E.g. renders faces that are closer to the camera over ones that are further back
            glEnable(GL_DEPTH_TEST)

            # Enable proper scaling
            glEnable(GL_NORMALIZE)

            # Perform transformations
            glScalef(*self.scale)
            glTranslatef(*self.position)
            glRotatef(self.angle_x, 0.0, 1.0, 0.0)
            glRotatef(self.angle_y, math.cos(math.radians(self.angle_x)), 0.0, math.sin(math.radians(self.angle_x)))

            # Show axis visuals
            if self.axis_shown:
                glBegin(GL_LINES)
                glColor3f(1.0, 0.0, 0.0)
                glVertex3f(2**32, 0.0, 0.0)
                glVertex3f(-2**32, 0.0, 0.0)
                glColor3f(0.0, 0.0, 1.0)
                glVertex3f(0.0, 2**32, 0.0)
                glVertex3f(0.0, -2**32, 0.0)
                glColor3f(0.0, 1.0, 0.0)
                glVertex3f(0.0, 0.0, 2**32)
                glVertex3f(0.0, 0.0, -2**32)
                glEnd()

            # Render the object
            for object_renderer in self.object_renderers:
                object_renderer.render(self.render_method, self.wireframe)
                glTranslatef(1, 0, 0)

            # Render to window
            pg.display.flip()
