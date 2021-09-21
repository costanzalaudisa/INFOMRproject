import numpy as np
import trimesh

from OpenGL.arrays import vbo
from pathlib import Path
from OpenGL.GL import *
from enum import Enum

class RenderMethod(Enum):
    FLAT = 0
    SMOOTH = 1
    POINT_CLOUD = 2

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

        # Define and fill buffer objects
        self.vertices = np.array([v - self.center for v in self.mesh.vertices], dtype="f")
        self.vertex_buffer = vbo.VBO(self.vertices)

        self.vertex_normals = np.array(self.mesh.vertex_normals, dtype="f")
        self.vertex_normal_buffer = vbo.VBO(self.vertex_normals)

        self.faces = np.array(self.mesh.faces, dtype=np.int32)
        self.face_buffer = vbo.VBO(self.faces, target=GL_ELEMENT_ARRAY_BUFFER)

        self.vertex_count = self.vertices.size
        self.face_vertex_count = self.faces.size

    def __del__(self):
        glDeleteBuffers(1, [self.vertex_buffer, self.vertex_normal_buffer, self.face_buffer])

    def render(self, method: RenderMethod = RenderMethod.FLAT, wireframe: bool = False):
        # Start local transform
        glPushMatrix()

        glScalef(*self.scale)
        glTranslatef(*self.position)
        glRotatef(self.rotation[0], *self.rotation[1])

        # Lighting
        glEnable(GL_LIGHTING)
        if method == RenderMethod.FLAT:
            glShadeModel(GL_FLAT)
        elif method == RenderMethod.SMOOTH:
            glShadeModel(GL_SMOOTH)
        glEnable(GL_COLOR_MATERIAL)

        glEnable(GL_LIGHT0)
        glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        # Set the color of the object
        glColor3f(*self.color)

        # Bind VBOs
        self.face_buffer.bind()

        glEnableClientState(GL_VERTEX_ARRAY)
        self.vertex_buffer.bind()
        glVertexPointer(3, GL_FLOAT, 0, None)

        glEnableClientState(GL_NORMAL_ARRAY)
        self.vertex_normal_buffer.bind()
        glNormalPointer(GL_FLOAT, 0, 0)

        if method == RenderMethod.POINT_CLOUD:
            # Draw as seperate points
            glPointSize(3)
            glDrawArrays(GL_POINTS, 0, self.vertex_count)
        else:
            # Assume all faces are triangles
            glDrawElements(GL_TRIANGLES, self.face_vertex_count, GL_UNSIGNED_INT, None)

        # If wireframe was selected, also draw the lines between vertices
        if wireframe:
            glPushMatrix()
            glDisable(GL_LIGHTING)
            glDisable(GL_LIGHT0)
            glShadeModel(GL_FLAT)
            glLineWidth(2)
            glColor3f(*self.line_color)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glDrawElements(GL_TRIANGLES, self.face_vertex_count, GL_UNSIGNED_INT, None)
            glPopMatrix()

        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)

        # Unbind VBOs
        self.face_buffer.unbind()
        self.vertex_buffer.unbind()
        self.vertex_normal_buffer.unbind()

        # End local transform
        glPopMatrix()

    def load_mesh(path: Path):
        # Load a mesh and return it as an Object
        mesh = trimesh.load(path, force="mesh")

        return Object(mesh, mesh.centroid)
