import numpy as np
import trimesh

from pathlib import Path
from OpenGL.GL import *


class Object:
    def __init__(self, mesh: trimesh.Trimesh, center: np.ndarray = None, color: np.ndarray = np.array([0.5, 0.5, 0.5])):
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
        self.position = np.array([0.0, 0.0, 0.0])
        self.rotation = (0.0, np.array([0.0, 0.0, 0.0]))
        self.scale = np.array([1.0, 1.0, 1.0])

    def render(self):
        # Start local transform
        glPushMatrix()

        glScalef(*self.scale)
        glTranslatef(*self.position)
        glRotatef(self.rotation[0], *self.rotation[1])

        # Assume all faces are triangles
        glBegin(GL_TRIANGLES)

        # Set the color of the object
        glColor3f(*self.color)

        # Go through each of the faces
        # Each face consists of exactly three vertices
        for i in range(len(self.mesh.faces)):
            face = self.mesh.faces[i]
            face_normal = self.mesh.face_normals[i]
            triangle = np.array([self.mesh.vertices[vi] for vi in face])

            for v in triangle:
                # Push normal vector to vector buffer
                glNormal3f(*face_normal)

                # Push the vertex to vertex buffer, adjusted for the center of the object
                glVertex3f(*(v - self.center))

        # Draw the object
        glEnd()

        # End local transform
        glPopMatrix()

    def load_mesh(path: Path):
        # Load a mesh and return it as an Object
        mesh = trimesh.load(path, force="mesh")

        return Object(mesh, mesh.centroid)
