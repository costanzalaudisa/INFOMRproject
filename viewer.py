from typing import Tuple
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from numpy.linalg import norm
import trimesh
import pygame as pg
from pygame.locals import *
import numpy as np

# Define constants
W, H = 800, 600
FOV = 45
DISTANCE = -3
Z_NEAR, Z_FAR = 0.1, 50.0
FPS = 60
SCALE_FACTOR = 1.1
SCALE_UP_FACTOR = np.ones(3) * SCALE_FACTOR
SCALE_DOWN_FACTOR = np.ones(3) / SCALE_FACTOR

def normalize_vector(v: np.ndarray):
    return v / np.linalg.norm(v)

def compute_normal(triangle: np.ndarray):
    # Triangle consists of three vertices
    if len(triangle) != 3:
        raise Error("Someething other than a triangle was passed")

    v1, v2, v3 = triangle

    print(triangle)
    normal = normalize_vector(np.cross(v2 - v1, v3 - v1))
    print(normal)

    return normalize_vector(np.cross(v2 - v1, v3 - v1))

# Render a mesh from the center of the screen
def renderMesh(mesh: trimesh.Trimesh, center: np.ndarray = np.array([0.0, 0.0, 0.0]), color: np.ndarray = np.array([1.0, 1.0, 1.0])):
    # Assume all faces are triangles
    glBegin(GL_TRIANGLES)

    # Go through each of the faces
    # Each face consists of exactly three vertices
    for face in mesh.faces:
        triangle = np.array([mesh.vertices[vi] for vi in face])
        glNormal3fv(compute_normal(triangle))

        for vertex_index in face:
            # Get the vertex and render it, adjusted for the center of the object
            v = mesh.vertices[vertex_index]
            glColor3fv(color)
            glVertex3fv(v - center)
    # Draw the object
    glEnd()

class Viewer:
    # Initializer for the Viewer
    def __init__(self, mesh: trimesh.Trimesh, mesh_center: np.ndarray = np.array([0.0, 0.0, 0.0])):
        self.mesh = mesh
        self.mesh_center = mesh_center

        # Set veriables to be used within the viewer
        self.clock = pg.time.Clock()
        self.drag = False
        self.mouse_x = 0
        self.mouse_y = 0

        # Initialize a window
        pg.init()
        pg.display.set_mode((W,H), DOUBLEBUF|OPENGL)
        pg.display.set_caption("INFOMR Viewer")
        pg.key.set_repeat(int(1000 / FPS))

        # Set the perspective and move the "camera" back
        gluPerspective(FOV, (W/H), Z_NEAR, Z_FAR)
        glTranslatef(0.0, 0.0, DISTANCE)

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
                    glScalef(*SCALE_UP_FACTOR)
                # Scroll up
                if event.button == 5:
                    glScalef(*SCALE_DOWN_FACTOR)
            elif event.type == pg.MOUSEBUTTONUP:
                # Stop dragging
                if event.button == 1:
                    self.drag = False
            elif event.type == pg.MOUSEMOTION:
                # Turn dragging motion into object rotation
                if self.drag:
                    mouse_x, mouse_y = event.pos
                    # TODO: Look at this, can this be improved?
                    glRotate((abs(mouse_x - self.mouse_x) + abs(mouse_y - self.mouse_y)) / 2, (mouse_y - self.mouse_y), (mouse_x - self.mouse_x), 0)
                    self.mouse_x = mouse_x
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_w:
                    glTranslatef(0, -0.05, 0)
                if event.key == pg.K_s:
                    glTranslatef(0, 0.05, 0)
                if event.key == pg.K_a:
                    glTranslatef(0.05, 0, 0)
                if event.key == pg.K_d:
                    glTranslatef(-0.05, 0, 0)

    def mainLoop(self):
        while True:
            self.handleEvents()
            self.clock.tick(FPS)

            # Clear the window
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # TODO: Fix this
            glShadeModel(GL_SMOOTH)
            light = np.array([5, 5, 5, 0])
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glLightfv(GL_LIGHT0, GL_POSITION, light)
            glEnable(GL_COLOR_MATERIAL)
            glColor3f(0, 1, 0)
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

            renderMesh(self.mesh, self.mesh_center)

            # Render to window
            pg.display.flip()
