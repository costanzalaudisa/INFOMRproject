import trimesh

from pathlib import Path
from math import sqrt

class Object:
    def __init__(self, mesh: trimesh.Trimesh):
        # Set local mesh
        if mesh is None:
            raise ValueError("A valid mesh should be provided")
        else:
            self.mesh = mesh

    def load_mesh(path: Path):
        # Load a mesh and return it as an Object
        mesh = trimesh.load(path, force="mesh")

        return Object(mesh)

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

    def subdivide(self):
        self.mesh = trimesh.Trimesh(*trimesh.remesh.subdivide(self.mesh.vertices, self.mesh.faces))
        print(f"Subdivided to {len(self.mesh.vertices)} vertices")

    def simplify(self):
        self.mesh = self.mesh.simplify_quadratic_decimation(len(self.mesh.faces) / 4)
        print(f"Simplified to {len(self.mesh.vertices)} vertices")

    def save_mesh(self, path: Path):
        # Save a mesh to a file
        self.mesh.export(path, "off")
