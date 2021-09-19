import numpy as np
import pygame as pg

from pygame.locals import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

from utils import normalize_vector
from object import Object

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
        self.drag = False
        self.mouse_x = 0
        self.mouse_y = 0

        self.scale = np.array([1.0, 1.0, 1.0])
        self.position = np.array([0.0, 0.0, 0.0])
        self.rotation = (0.0, np.array([0.0, 0.0, 0.0]))

        # Initialize a window
        pg.init()
        pg.display.set_mode((W,H), DOUBLEBUF|OPENGL)
        pg.display.set_caption("INFOMR Viewer")
        pg.key.set_repeat(int(1000 / FPS))

        # Set the perspective and move the "camera" back
        glMatrixMode(GL_PROJECTION)
        gluPerspective(FOV, (W/H), Z_NEAR, Z_FAR)
        glTranslatef(0.0, 0.0, DISTANCE)

        self.a = (GLfloat * 16)()
        self.modelMat = glGetFloatv(GL_MODELVIEW_MATRIX, self.a)

    # Handle pygame events
    def handleEvents(self):
        for event in pg.event.get():
            # Close window when the red X is pressed
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                # Start dragging and set previous mouse location
                if event.button == 1:
                    self.drag = True
                    mouse_x, mouse_y = event.pos
                    self.mouse_x = mouse_x
                    self.mouse_y = mouse_y
                # Scroll down
                if event.button == 4:
                    self.scale *= SCALE_FACTOR
                # Scroll up
                if event.button == 5:
                    self.scale /= SCALE_FACTOR
            elif event.type == pg.MOUSEBUTTONUP:
                # Stop dragging
                if event.button == 1:
                    self.drag = False
                    self.rotation = (self.rotation[0] % 360, normalize_vector(self.rotation[1]))
            elif event.type == pg.MOUSEMOTION:
                # Turn dragging motion into object rotation
                if self.drag:
                    mouse_x, mouse_y = event.pos

                    # TODO: Look at this, can this be improved?
                    self.rotation = (self.rotation[0] + (abs(mouse_x - self.mouse_x) + abs(mouse_y - self.mouse_y)) / 2, self.rotation[1] + np.array([(mouse_y - self.mouse_y), (mouse_x - self.mouse_x), 0.0]))

                    # Reset previous mouse position
                    self.mouse_x = mouse_x
                    self.mouse_y = mouse_y
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_w:
                    self.position -= np.array(MOVE_Y)
                if event.key == pg.K_s:
                    self.position += np.array(MOVE_Y)
                if event.key == pg.K_a:
                    self.position += np.array(MOVE_X)
                if event.key == pg.K_d:
                    self.position -= np.array(MOVE_X)

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
            glDepthFunc(GL_LESS)

            # Enable light shading
            glShadeModel(GL_SMOOTH)
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glLightfv(GL_LIGHT0, GL_POSITION, np.array([5, 5, 5, 0]))
            glEnable(GL_COLOR_MATERIAL)
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

            # Perform transformations
            glScalef(*self.scale)
            glTranslatef(*self.position)
            glRotatef(self.rotation[0], *self.rotation[1])

            # Render the object
            self.object.render()

            # Render to window
            pg.display.flip()
