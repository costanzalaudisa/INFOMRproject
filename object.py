import numpy as np
import trimesh

from pathlib import Path
from OpenGL.GL import *
from enum import Enum

class RenderMethod(Enum):
    FLAT = 0
    SMOOTH = 1
    WIREFRAME = 2
    POINT_CLOUD = 3

class Object:
    def __init__(self, mesh: trimesh.Trimesh, center: np.ndarray = None, color: np.ndarray = np.array([0.5, 0.5, 0.5]), line_color: np.ndarray = np.array([0.3, 0.3, 0.3])):
        # Set local mesh
        if mesh is None:
            raise ValueError("A valid mesh should be provided")
        else:
            self.mesh = mesh

        # Set local center
        if center is None:
            self.center = mesh.centroid
        else:
            self.center = center

        # Set all other variables
        self.color = color
        self.line_color = line_color
        self.position = np.array([0.0, 0.0, 0.0])
        self.rotation = (0.0, np.array([0.0, 0.0, 0.0]))
        self.scale = np.array([1.0, 1.0, 1.0])

    def render(self, method: RenderMethod = RenderMethod.FLAT):
        if method == RenderMethod.WIREFRAME or method == RenderMethod.POINT_CLOUD:
            glPointSize(2)
        else:
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            # glLightfv(GL_LIGHT0, GL_POSITION, np.array([5, 5, 5, 0]))
            # glEnable(GL_COLOR_MATERIAL)
            glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
            glShadeModel(GL_SMOOTH)

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        # Start local transform
        glPushMatrix()

        glScalef(*self.scale)
        glTranslatef(*self.position)
        glRotatef(self.rotation[0], *self.rotation[1])

        if method == RenderMethod.WIREFRAME or method == RenderMethod.POINT_CLOUD:
            # Draw as seperate points
            glBegin(GL_POINTS)
        else:
            # Assume all faces are triangles
            glBegin(GL_TRIANGLES)

        # Set the color of the object
        glColor3f(*self.color)

        # Draw all the vertices
        self.draw_vertices(method)

        # Draw the object
        glEnd()

        # If wireframe was selected, also draw the lines between vertices
        if method == RenderMethod.WIREFRAME:
            glColor3f(*self.line_color)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glBegin(GL_TRIANGLES)
            self.draw_vertices(method)
            glEnd()

        # End local transform
        glPopMatrix()

    def draw_vertices(self, method: RenderMethod):
        # Go through each of the faces
        # Each face consists of exactly three vertices
        for i in range(len(self.mesh.faces)):
            face = self.mesh.faces[i]

            for vi in face:
                # Push normal vector to vector buffer
                if method == RenderMethod.FLAT:
                    face_normal = self.mesh.face_normals[i]
                    glNormal3f(*face_normal)
                elif method == RenderMethod.SMOOTH:
                    vertex_normal =  self.mesh.vertex_normals[vi]
                    glNormal3f(*vertex_normal)

                # Push the vertex to vertex buffer, adjusted for the center of the object
                glVertex3f(*(self.mesh.vertices[vi] - self.center))

    def load_mesh(path: Path):
        # Load a mesh and return it as an Object
        mesh = trimesh.load(path, force="mesh")

        return Object(mesh, mesh.centroid)
