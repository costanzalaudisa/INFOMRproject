import trimesh
import utils

from pathlib import Path
from math import sqrt
class Object:
    def __init__(self, mesh: trimesh.Trimesh, model_num: int = None, label: str = None):
        # Set local mesh
        if mesh is None:
            raise ValueError("A valid mesh should be provided")
        else:
            self.mesh = mesh

        self.model_num = model_num
        self.label = label

    def load_mesh(path: Path):
        # Load a mesh and return it as an Object
        mesh = trimesh.load(path, force="mesh")

        # Get model num from path
        model_num = int(path.name.split(".")[0].split("m")[1])

        # Get label from model num
        label = None
        if model_num != "":
            label = utils.get_label_by_id(model_num)

        return Object(mesh, model_num, label)

    def get_info(self):
        # Retrieve object info and return it
        label = self.label
        model_num = self.model_num
        num_vertices = self.mesh.vertices.shape[0]
        num_faces = self.mesh.faces.shape[0]
        num_edges = self.mesh.edges.shape[0]
        type_faces = ""
        bounding_box = self.mesh.bounds

        if self.mesh.faces.shape[1] == 3:
            type_faces = "triangles"
        elif self.mesh.faces.shape[1] == 4:
            type_faces = "quads"

        if label is None or model_num is None:
            print("Mesh has no label.")
            model_num = "N/A"
            label = "N/A"

        return model_num, label, num_vertices, num_faces, num_edges, type_faces, bounding_box

    def process(self):
        # Remove duplicate faces and vertices
        self.mesh.process()
        self.mesh.remove_duplicate_faces()

    def center(self):
        # Center the mesh such that its center becomes [0.0, 0.0, 0.0]
        self.mesh.apply_translation(-1 * self.mesh.centroid)

    def scale(self):
        # Scale the mesh such that it tightly fits in a unit bounding box

        # Get the longest edge of the current bounding box
        # This is what we will be scaling to
        edges_sizes = self.mesh.bounds[1] - self.mesh.bounds[0]
        longest_edge = max(edges_sizes)

        # Calculate scale factor:
        # sqrt(3) is the diagonal of the unit box
        # sqrt(pow(longest_edge, 2) * 3) is the diagonal of a box where all edges are of longest_edge
        # Divide this by each other to get the scale factor
        scale_factor = sqrt(3) / sqrt(pow(longest_edge, 2) * 3)

        # Apply found scale factor
        self.mesh.apply_scale(scale_factor)

    def remesh_to(self, vertex_count, threshold):
        # Remesh the mesh such that the mesh has vertex_count +/- threshold vertices
        while len(self.mesh.vertices) > vertex_count + threshold or len(self.mesh.vertices) < vertex_count - threshold:
            # If number of vertices is too high, simplify
            if len(self.mesh.vertices) > vertex_count + threshold:
                self.simplyify_to(vertex_count)

            # If number of vertices is too low, subdivide
            if len(self.mesh.vertices) < vertex_count - threshold:
                self.subdivide()

    def subdivide(self):
        self.mesh = trimesh.Trimesh(*trimesh.remesh.subdivide(self.mesh.vertices, self.mesh.faces))

    def simplify(self):
        self.mesh = self.mesh.simplify_quadratic_decimation(len(self.mesh.faces) / 4)

    def simplyify_to(self, vector_count):
        new_face_count = vector_count * (len(self.mesh.faces) / len(self.mesh.vertices))
        self.mesh = self.mesh.simplify_quadratic_decimation(new_face_count)

    def save_mesh(self, path: Path):
        # Save a mesh to a file
        self.mesh.export(path, "off")
