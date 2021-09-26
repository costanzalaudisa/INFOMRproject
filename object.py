from utils import normalize_vector
import numpy as np
import trimesh

from OpenGL.arrays import vbo
from pathlib import Path
from OpenGL.GL import *
from enum import Enum

class RenderMethod(Enum):
    FLAT = 0
    SMOOTH = 1
    NO_SHADING = 2
    POINT_CLOUD = 3

class Object:
    def __init__(self, mesh: trimesh.Trimesh, center: np.ndarray = None, color: np.ndarray = np.array([0.0, 0.5, 0.3]), line_color: np.ndarray = np.array([0.0, 0.1, 0.0])):
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

        self.update_vbos()

    def __del__(self):
        glDeleteBuffers(1, [self.vertex_buffer, self.vertex_normal_buffer, self.face_buffer])

    def update_vbos(self):
        # Define and fill buffer objects
        self.vertices = np.array([v - self.center for v in self.mesh.vertices], dtype="f")
        self.vertex_buffer = vbo.VBO(self.vertices)

        self.vertex_normals = np.array(self.mesh.vertex_normals, dtype="f")
        self.vertex_normal_buffer = vbo.VBO(self.vertex_normals)

        self.faces = np.array(self.mesh.faces, dtype=np.int32)
        self.face_buffer = vbo.VBO(self.faces, target=GL_ELEMENT_ARRAY_BUFFER)

        self.vertex_count = self.vertices.size
        self.face_vertex_count = self.faces.size

        #--------------#
        # Flat shading #
        #--------------#
        self.flat_vertices = []
        self.flat_vertex_normals = []
        self.flat_faces = []

        # Duplicate all vertices by how many faces include it
        # such that all vertices have the face normal as its normal
        v_i = 0
        for i, face in enumerate(self.faces):
            face_normal = self.mesh.face_normals[i]

            verts = [self.vertices[vi] for vi in face]

            face = []

            for v in verts:
                self.flat_vertices.append(v)
                self.flat_vertex_normals.append(face_normal)
                face.append(v_i)

                v_i += 1

            self.flat_faces.append(face)

        # Define and fill buffer objects for flat shading
        self.flat_vertices = np.array(self.flat_vertices, dtype="f")
        self.flat_vertex_buffer = vbo.VBO(self.flat_vertices)

        self.flat_vertex_normals = np.array(self.flat_vertex_normals, dtype="f")
        self.flat_vertex_normal_buffer = vbo.VBO(self.flat_vertex_normals)

        self.flat_faces = np.array(self.flat_faces, dtype=np.int32)
        self.flat_face_buffer = vbo.VBO(self.flat_faces, target=GL_ELEMENT_ARRAY_BUFFER)

        self.flat_vertex_count = self.flat_vertices.size
        self.flat_face_vertex_count = self.flat_faces.size

    def subdivide(self):
        self.mesh = trimesh.Trimesh(*trimesh.remesh.subdivide(self.mesh.vertices, self.mesh.faces))
        print(f"Subdivided to {len(self.mesh.vertices)} vertices")

        self.__del__()
        self.update_vbos()

    def simplify(self):
        self.mesh = self.mesh.simplify_quadratic_decimation(len(self.mesh.faces) / 4)
        print(f"Simplified to {len(self.mesh.vertices)} vertices")

        self.__del__()
        self.update_vbos()

    def render(self, method: RenderMethod = RenderMethod.FLAT, wireframe: bool = False):
        # Start local transform
        glPushMatrix()

        glScalef(*self.scale)
        glTranslatef(*self.position)
        glRotatef(self.rotation[0], *self.rotation[1])

        if method != RenderMethod.NO_SHADING and method != RenderMethod.POINT_CLOUD:
            # Lighting
            glEnable(GL_LIGHTING)
            if method == RenderMethod.FLAT:
                glShadeModel(GL_FLAT)
            elif method == RenderMethod.SMOOTH:
                glShadeModel(GL_SMOOTH)
            glEnable(GL_COLOR_MATERIAL)

            glEnable(GL_LIGHT0)
            glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)

        # Set polygon mode to fill polygons both from the front and back
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        # Set the color of the object
        glColor3f(*self.color)

        # Bind VBOs
        if method == RenderMethod.FLAT:
            self.flat_face_buffer.bind()

            glEnableClientState(GL_VERTEX_ARRAY)
            self.flat_vertex_buffer.bind()
            glVertexPointerf(self.flat_vertex_buffer)

            glEnableClientState(GL_NORMAL_ARRAY)
            self.flat_vertex_normal_buffer.bind()
            glNormalPointerf(self.flat_vertex_normal_buffer)
        else:
            self.face_buffer.bind()

            glEnableClientState(GL_VERTEX_ARRAY)
            self.vertex_buffer.bind()
            glVertexPointerf(self.vertex_buffer)

            glEnableClientState(GL_NORMAL_ARRAY)
            self.vertex_normal_buffer.bind()
            glNormalPointerf(self.vertex_normal_buffer)

        if method == RenderMethod.POINT_CLOUD:
            # Draw as seperate points
            glPointSize(3)
            glDrawArrays(GL_POINTS, 0, self.vertex_count)
        else:
            # Assume all faces are triangles
            glDrawElements(GL_TRIANGLES, self.face_vertex_count, GL_UNSIGNED_INT, None)

        # If wireframe was selected, also draw the lines between vertices
        if wireframe:
            # Locally change options
            glPushMatrix()
            glDisable(GL_LIGHTING)
            glDisable(GL_LIGHT0)
            glShadeModel(GL_FLAT)
            glLineWidth(2)

            # Set color
            glColor3f(*self.line_color)

            # Set polygon mode to lines
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

            # Draw the lines
            glDrawElements(GL_TRIANGLES, self.face_vertex_count, GL_UNSIGNED_INT, None)

            # End local transform
            glPopMatrix()

        # Clean up
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)

        # Unbind VBOs
        if method == RenderMethod.FLAT:
            self.flat_face_buffer.unbind()
            self.flat_vertex_buffer.unbind()
            self.flat_vertex_normal_buffer.unbind()
        else:
            self.face_buffer.unbind()
            self.vertex_buffer.unbind()
            self.vertex_normal_buffer.unbind()

        # Reset lighting
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
        glShadeModel(GL_FLAT)

        # End local transform
        glPopMatrix()

    def load_mesh(path: Path):
        # Load a mesh and return it as an Object
        mesh = trimesh.load(path, force="mesh")

        return Object(mesh, mesh.centroid)
