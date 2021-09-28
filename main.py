from object import Object
from viewer import Viewer

from classes import define_classes
from filter import get_info, get_db_info
from stats import plot_stats

## Define PSB classes
#files = ['./classes/train.cla', './classes/test.cla']
#define_classes(files)

## Get entire PSB database info
#get_db_info("models")

# Get database statistics and plot data
plot_stats()

# Load a model
mesh_file = "./models/m303/m303.off"

# Get current model's info
model_num, label, num_vertices, num_faces, type_faces, bounding_box = get_info(mesh_file)

print("#################")
print("### MESH INFO ###")
print("#################")
print("Model number:", model_num)
print("Label:", label)
print("Number of vertices:", num_vertices)
print("Number of faces:", num_faces)
print("Type of faces:", type_faces)
print("Bounding box:", bounding_box)

# Show the mesh using the viewer
obj = Object.load_mesh(mesh_file)

# Pre-process the mesh
obj.center()
obj.scale()

# View the loaded mesh
viewer = Viewer(obj)
viewer.mainLoop()
