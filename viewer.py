import pygame as pg
import numpy as np
import math

from pygame.locals import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

from object import Object, RenderMethod
from utils import normalize_vector

# Define constants
W, H = 800, 600
FOV = 45
DISTANCE = -3
Z_NEAR, Z_FAR = 0.1, 50.0
FPS = 60
SCALE_FACTOR = 1.1
MOVE_X = np.array([0.05, 0, 0])
MOVE_Y = np.array([0, 0.05, 0])

class Viewer:
    # Initializer for the Viewer
    def __init__(self, object: Object):
        # Set veriables to be used within the viewer
        self.object = object
        self.clock = pg.time.Clock()
        self.keys_pressed_last_frame = []

        self.scale = np.array([1.0, 1.0, 1.0])
        self.position = np.array([0.0, 0.0, 0.0])
        self.rotation = (0.0, np.array([0.0, 0.0, 0.0]))
        self.angle_x = 0
        self.angle_y = 0
        self.render_method = RenderMethod.FLAT
        self.wireframe = True

        # Initialize a window
        pg.init()
        pg.display.set_mode((W,H), DOUBLEBUF|OPENGL)
        pg.display.set_caption("INFOMR Viewer")
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
                del self.object
                pg.quit()
                quit()
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

                    self.position += MOVE_X * diff_x / self.scale[0] / 10
                    self.position -= MOVE_Y * diff_y / self.scale[0] / 10
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_w:
                    self.position -= np.array(MOVE_Y)
                if event.key == pg.K_s:
                    self.position += np.array(MOVE_Y)
                if event.key == pg.K_a:
                    self.position += np.array(MOVE_X)
                if event.key == pg.K_d:
                    self.position -= np.array(MOVE_X)
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
                    self.timer = 0
                    if self.wireframe:
                        print("Enabled wireframe")
                    else:
                        print("Disabled wireframe")

        self.keys_pressed_last_frame = pg.key.get_pressed()

    def mainLoop(self):
        while True:
            # Clear the window
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # Reset view
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            # Handle all pygame events
            self.handleEvents()

            # Limit FPS
            self.clock.tick(FPS)

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

            # Render the object
            self.object.render(self.render_method, self.wireframe)

            # Render to window
            pg.display.flip()
