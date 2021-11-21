import trimesh
import utils
import numpy as np
import math

from pathlib import Path
from math import sqrt

SAMPLE_SIZE = 10000
BIN_COUNT = 15
BIN_COUNT += 1 # ensure that bin_count actually resolves to bin_count bins

class Object:
    def __init__(self, mesh: trimesh.Trimesh, model_num: int = None, label: str = None):
        # Set local mesh
        if mesh is None:
            raise ValueError("A valid mesh should be provided")
        else:
            self.mesh = mesh

        self.model_num = model_num
        self.label = label

    # Load a mesh and return it as an Object
    def load_mesh(path: Path):
        mesh = trimesh.load(path, force="mesh")

        if path.name.startswith("m"):
            # Get model num from path
            model_num = int(path.name.split(".")[0].split("m")[1])
        else:
            model_num = None

        # Get label from model num
        label = None
        if model_num != "":
            label = utils.get_label_by_id(model_num)

        return Object(mesh, model_num, label)

    # Retrieve object info and return it
    def get_info(self):
        label = self.label
        model_num = self.model_num
        num_vertices = self.mesh.vertices.shape[0]
        num_faces = self.mesh.faces.shape[0]
        num_edges = self.mesh.edges.shape[0]
        bounding_box = list(map(list, self.mesh.bounds))
        barycenter = list(self.mesh.centroid)
        diagonal = self.mesh.scale

        # Calculate features
        surface = self.mesh.area
        bounding_box_volume = None
        try:
            bounding_box_volume = self.mesh.bounding_box_oriented.volume
        except:
            print("Something went wrong when calculating the axis aligned bounding box")

        volume = None
        try:
            volume = self.mesh.convex_hull.volume
        except:
            print("Something went wrong when calculating the convex_hull")

        compactness = None
        if volume:
            compactness = surface ** 3 / (36 * math.pi * volume ** 2)

        # Calculate distances between 2 surface points over the entire mesh and pick the largest
        diameter = np.linalg.norm(self.mesh.vertices[0] - self.mesh.vertices[1])
        for i in range(len(self.mesh.vertices)):
            for j in range(i, len(self.mesh.vertices)):
                diff = np.linalg.norm(self.mesh.vertices[i] - self.mesh.vertices[j])
                if diff > diameter:
                    diameter = diff

        # Calculate eccentricity from eigenvalues (e1/e3 so major/minor) -> NOTE!!! values seem weird, probably needs checking
        eigenvalues, eigenvectors = self.get_eigen()
        eccentricity = abs(max(eigenvalues))/abs(min(eigenvalues))

        A3 = self.A3()
        D1 = self.D1()
        D2 = self.D2()
        D3 = self.D3()
        D4 = self.D4()

        type_faces = ""

        if self.mesh.faces.shape[1] == 3:
            type_faces = "triangles"
        elif self.mesh.faces.shape[1] == 4:
            type_faces = "quads"

        if label is None or model_num is None:
            print("Mesh has no label.")
            model_num = "N/A"
            label = "N/A"

        return model_num, label, num_vertices, num_faces, num_edges, type_faces, bounding_box, barycenter, diagonal, surface, bounding_box_volume, volume, compactness, diameter, eccentricity, A3, D1, D2, D3, D4

    # Calculate feature A3
    def A3(self):
        vertices = self.mesh.vertices

        angles = []

        for _ in range(SAMPLE_SIZE):
            samples = vertices[np.random.choice(vertices.shape[0], 3, replace=False)]
            angles.append(utils.angle_between(samples[1] - samples[0], samples[2] - samples[0]))

        bins = np.linspace(0, math.pi, BIN_COUNT)
        bin_counts = np.histogram(angles, bins)[0]

        assert sum(bin_counts) == SAMPLE_SIZE, f"Not all samples were binned properly: {sum(bin_counts)} not equal to {SAMPLE_SIZE}"

        bin_counts = list(bin_counts / np.linalg.norm(bin_counts))

        return bin_counts

    # Calculate feature D1
    def D1(self):
        vertices = self.mesh.vertices
        centroid = self.mesh.centroid

        distances = []
        for _ in range(SAMPLE_SIZE):
            sample = vertices[np.random.choice(vertices.shape[0], 1, replace=False)]
            distances.append(np.linalg.norm(sample - centroid))

        bins = np.linspace(0, sqrt(3), BIN_COUNT)
        bin_counts = np.histogram(distances, bins)[0]

        # assert sum(bin_counts) == SAMPLE_SIZE, f"Not all samples were binned properly: {sum(bin_counts)} not equal to {SAMPLE_SIZE}"

        bin_counts = list(bin_counts / np.linalg.norm(bin_counts))

        return bin_counts

    # Calculate feature D2
    def D2(self):
        vertices = self.mesh.vertices

        distances = []
        for _ in range(SAMPLE_SIZE):
            sample = vertices[np.random.choice(vertices.shape[0], 2, replace=False)]
            distances.append(np.linalg.norm(sample[0] - sample[1]))

        bins = np.linspace(0, sqrt(3), BIN_COUNT)
        bin_counts = np.histogram(distances, bins)[0]

        # assert sum(bin_counts) == SAMPLE_SIZE, f"Not all samples were binned properly: {sum(bin_counts)} not equal to {SAMPLE_SIZE}"

        bin_counts = list(bin_counts / np.linalg.norm(bin_counts))

        return bin_counts

    # Calculate feature D3
    def D3(self):
        vertices = self.mesh.vertices

        square_rooted_areas = []
        for _ in range(SAMPLE_SIZE):
            sample = vertices[np.random.choice(vertices.shape[0], 3, replace=False)]
            a = np.linalg.norm(sample[0] - sample[1])
            b = np.linalg.norm(sample[1] - sample[2])
            c = np.linalg.norm(sample[0] - sample[2])

            p = (a + b + c) / 2
            area = sqrt(np.abs(p * (p - a) * (p - b) * (p - c)))
            square_rooted_areas.append(sqrt(area))

        # Largest triangle has sides of sqrt(2) each
        # Area of this triangle is 0.5 * sqrt(3)
        bins = np.linspace(0, sqrt(0.5 * sqrt(3)), BIN_COUNT)
        bin_counts = np.histogram(square_rooted_areas, bins)[0]

        # assert sum(bin_counts) == SAMPLE_SIZE, f"Not all samples were binned properly: {sum(bin_counts)} not equal to {SAMPLE_SIZE}"

        bin_counts = list(bin_counts / np.linalg.norm(bin_counts))

        return bin_counts

    # Calculate feature D4
    def D4(self):
        vertices = self.mesh.vertices

        cube_rooted_volumes = []

        for _ in range(SAMPLE_SIZE):
            sample = vertices[np.random.choice(vertices.shape[0], 4, replace=False)]
            ad = sample[0] - sample[3]
            bd = sample[1] - sample[3]
            cd = sample[2] - sample[3]

            volume = np.abs(np.dot(ad, np.cross(bd, cd))) / 6

            cube_rooted_volumes.append(volume ** (1/3))

        # Largest tetrahedron has sides of sqrt(2) each
        # Volume of this tetrahedron is 1/3
        bins = np.linspace(0, (1/3)**(1/3), BIN_COUNT)
        bin_counts = np.histogram(cube_rooted_volumes, bins)[0]

        # assert sum(bin_counts) == SAMPLE_SIZE, f"Not all samples were binned properly: {sum(bin_counts)} not equal to {SAMPLE_SIZE}"

        bin_counts = list(bin_counts / np.linalg.norm(bin_counts))

        return bin_counts

    # Run checks on model
    def check_model(self):
        model_num = self.model_num

        # Run checks on the model (is it watertight? does it have a consistent winding, outward normals?)
        watertight = self.mesh.is_watertight
        winding = self.mesh.is_winding_consistent
        normals = np.isfinite(self.mesh.center_mass).all()
        pos_volume = self.mesh.volume > 0.0

        return model_num, watertight, winding, normals, pos_volume

    # Get model's eigenvectors and eigenvalues
    def get_eigen(self):
        # Compute the covariance matrix for mesh
        A = np.transpose(self.mesh.vertices)

        A_cov = np.cov(A)

        # Compute eigenvalues and eigenvectors for covariance matrix
        eigenvalues, eigenvectors = np.linalg.eig(A_cov)

        # Get major, medium, minor eigenvectors by eigenvalue magnitude
        indices = [0, 1, 2]
        indices.remove(np.argmax(eigenvalues, axis=0))
        indices.remove(np.argmin(eigenvalues, axis=0))

        major_eigenvector = eigenvectors[np.argmax(eigenvalues, axis=0)]
        medium_eigenvector = eigenvectors[indices[0]]
        minor_eigenvector = eigenvectors[np.argmin(eigenvalues, axis=0)]

        # Fix e3 by replacing it with e1 × e2 (Tech Tips 3A)
        minor_eigenvector = np.cross(major_eigenvector, medium_eigenvector)

        eigenvectors = np.array([major_eigenvector, medium_eigenvector, minor_eigenvector])

        return eigenvalues, eigenvectors

    # Preprocess model
    def preprocess(self, vertex_count, threshold):
        self.process()                          # adjust meshes (remove duplicate faces, etc.)
        self.remesh_to(vertex_count, threshold) # remesh
        self.center()                           # translate barycenter to origin
        self.align()                            # compute eigenvectors and align with coordinate frame
        self.flip()                             # flip based on moment test
        self.scale()                            # scale to unit volume

    # Adjust mesh (remove duplicate faces, etc.)
    def process(self):
        # Remove duplicate faces and vertices
        self.mesh.process()
        self.mesh.remove_duplicate_faces()

    # Center mesh
    def center(self):
        # Center the mesh such that its center becomes [0.0, 0.0, 0.0]
        self.mesh.apply_translation(-1 * self.mesh.centroid)

    # Align mesh
    def align(self):
        # Calculate eigenvectors
        eigenvalues, eigenvectors = self.get_eigen()

        # Align eigenvectors with the XYZ coordinate frame by projecting (Tech Tips 3A)
        self.mesh = trimesh.Trimesh(np.dot(self.mesh.vertices, eigenvectors), self.mesh.faces)

    # Scale the mesh such that it tightly fits in a unit bounding box
    def scale(self):
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

    # Flip mesh according to moment test
    def flip(self):
        # Perform flipping test (Tech Tips 3A)
        f = sum((self.mesh.triangles_center)*((self.mesh.triangles_center)**2))

        # Mirror mesh using scaling factors
        self.mesh = trimesh.Trimesh((self.mesh.vertices * np.sign(f)), self.mesh.faces)

    # Remesh mesh
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

    # Save a mesh to a file
    def save_mesh(self, path: Path):
        self.mesh.export(path, "off")
