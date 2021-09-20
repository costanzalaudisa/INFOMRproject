from typing import Tuple
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from numpy.linalg import norm
import trimesh
import pygame as pg
from pygame.locals import *
import numpy as np
import math

# Perspective constants
W, H = 800, 600
FOV = 45
DISTANCE = -3
Z_NEAR, Z_FAR = 0.1, 50.0
FPS = 60
SCALE_FACTOR = 1.1
SCALE_UP_FACTOR = np.ones(3) * SCALE_FACTOR
SCALE_DOWN_FACTOR = np.ones(3) / SCALE_FACTOR
MOVE_X = np.array([0.05, 0, 0])
MOVE_Y = np.array([0, 0.05, 0])

# Function to normalize vectors
def normalize_vector(v: np.ndarray):
    return v / np.linalg.norm(v)

# Function to calculate surface normal
def compute_normal(triangle: np.ndarray):
    # Triangle consists of three vertices
    if len(triangle) != 3:
        raise Error("Something other than a triangle was passed")

    v1, v2, v3 = triangle
    normal = normalize_vector(np.cross(v2 - v1, v3 - v1))

    return normalize_vector(np.cross(v2 - v1, v3 - v1))

# Render a mesh from the center of the screen
def renderMesh(mesh: trimesh.Trimesh, center: np.ndarray = np.array([0.0, 0.0, 0.0]), color: np.ndarray = np.array([1.0, 1.0, 1.0])):
    # Assume all faces are triangles
    glBegin(GL_TRIANGLES)

    # Go through each of the faces
    # Each face consists of exactly three vertices
    for face in mesh.faces:
        triangle = np.array([mesh.vertices[vi] for vi in face])

        face_normal = compute_normal(triangle)
        for vertex_index in face:
            # Get the vertex and render it, adjusted for the center of the object
            v = mesh.vertices[vertex_index]
            glColor3fv(color)
            glNormal3fv(face_normal)
            glVertex3fv(v - center)
    
    # Draw the object
    glEnd()

# TODO: what does this do?
def map_hemisphere(x,y):
    z = math.sqrt(abs(1-math.pow(x,2)-math.pow(y,2)))
    return z

# Calculate angle of two spatial vectors
def angle_calculation(a,b):
    #print(a,b)
    r = math.degrees(math.acos((np.dot(a, b))/(np.linalg.norm(a)*np.linalg.norm(b) + 0.0000001)))

    return r


### VIEWER CLASS ###
class Viewer:
    # Initializer for the Viewer
    def __init__(self, mesh: trimesh.Trimesh, mesh_center: np.ndarray = np.array([0.0, 0.0, 0.0])):
        self.mesh = mesh
        self.mesh_center = mesh_center

        # Set variables to be used within the viewer
        self.clock = pg.time.Clock()
        self.dragLeft = False
        self.dragRight = False
        self.mouse_x = 0
        self.mouse_y = 0
        self.p1 = (0.0, 0.0, 0.0)
        self.position = np.array([0.0, 0.0, 0.0])
        self.norm_mouse_pos = (0.0, 0.0, 0.0)

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
            if event.type == pg.QUIT: # Close window when the red X is pressed
                pg.quit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                # Start dragging and set previous mouse location
                if event.button == 1:
                    self.dragLeft = True
                    mouse_x, mouse_y = event.pos
                    self.mouse_x = mouse_x
                    self.mouse_y = mouse_y
                    norm_mouse_pos = (2*self.mouse_x / W-1, 2*mouse_y / H-1, map_hemisphere(2*mouse_x / W-1, 2*mouse_y / H-1))
                    self.p1 = (norm_mouse_pos[0],norm_mouse_pos[1],map_hemisphere(norm_mouse_pos[0],norm_mouse_pos[1]))
                if event.button == 3: # how to handle this now?
                    self.dragRight = True
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
                    self.dragLeft = False
                if event.button == 3:
                    self.dragRight = False
            elif event.type == pg.MOUSEMOTION:
                # Turn dragging motion into object rotation
                if self.dragLeft:
                    mouse_x, mouse_y = event.pos

                    # TODO: Look at this, can this be improved?
                    glRotate((abs(mouse_x - self.mouse_x) + abs(mouse_y - self.mouse_y)) / 2, (mouse_y - self.mouse_y), (mouse_x - self.mouse_x), 0)
                    norm_mouse_pos = (2*self.mouse_x / W-1, 2*mouse_y / H-1, map_hemisphere(2*mouse_x / W-1, 2*mouse_y / H-1))
                    p2 = (norm_mouse_pos[0],norm_mouse_pos[1],map_hemisphere(norm_mouse_pos[0],norm_mouse_pos[1]))
                    # cist = np.cross(self.p1, p2)
                    self.p1 = p2
                    self.mouse_x = mouse_x
                    self.mouse_y = mouse_y
                if self.dragRight:
                    mouse_x, mouse_y = event.pos

                    #TODO: this doesn't work anymore and I'm not sure how to fix it

                    ## Movement threshold
                    #threshold = 25
                    #diff_x = (mouse_x - self.mouse_x)
                    #diff_y = (mouse_y - self.mouse_y)

                    #if (mouse_x < self.mouse_x) and abs(diff_x) > threshold:
                    #    self.position += np.array(MOVE_X)
                    #if (mouse_x > self.mouse_x) and abs(diff_x) > threshold:
                    #    self.position -= np.array(MOVE_X)                  
                    #if (mouse_y < self.mouse_y) and abs(diff_y) > threshold:
                    #    self.position -= np.array(MOVE_Y)
                    #if (mouse_y > self.mouse_y) and abs(diff_y) > threshold:
                    #    self.position += np.array(MOVE_Y)

                    #self.mouse_x = mouse_x
                    #self.mouse_y = mouse_y
            # Pan object with WASD keys or arrow keys
            elif event.type == pg.KEYDOWN :
                if event.key == pg.K_w or event.key == pg.K_UP:
                    self.position += np.array(MOVE_Y)                    
                if event.key == pg.K_s or event.key == pg.K_DOWN:
                    self.position -= np.array(MOVE_Y)
                if event.key == pg.K_a or event.key == pg.K_LEFT:
                    self.position -= np.array(MOVE_X)
                if event.key == pg.K_d or event.key == pg.K_RIGHT:
                    self.position += np.array(MOVE_X)

    def mainLoop(self):
        while True:
            # Clear the window
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            self.handleEvents()
            self.clock.tick(FPS)
            # glMultMatrixf(self.modelMat)
            # self.modelMat = glGetFloatv(GL_MODELVIEW_MATRIX, self.a)

            glEnable(GL_DEPTH_TEST)
            glDepthFunc(GL_LESS)
            # TODO: Fix this
            glShadeModel(GL_SMOOTH)
            light = np.array([5, 5, 5, 0])
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glLightfv(GL_LIGHT0, GL_POSITION, light)
            glEnable(GL_COLOR_MATERIAL)
            glColor3f(0.5, 0.5, 0.5)
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

            glTranslatef(*self.position)
            axis = (self.p1[0], self.p1[1])
            glRotatef(angle_calculation(np.array([0.0, 0.0, 0.0]), self.p1), axis[1], axis[0], 0)
            renderMesh(self.mesh, self.mesh_center)

            #glLoadIdentity()
            glTranslatef(0,0.0,-10000)

            glMultMatrixf(self.modelMat)

            # Render to window
            pg.display.flip()