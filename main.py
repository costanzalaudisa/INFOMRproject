from object import Object
from viewer import Viewer

from classes import define_classes
from filter import get_info, get_db_info

## Get entire PSB database info
#get_db_info("models")

## Define PSB classes
#files = ['./classes/train.cla', './classes/test.cla']
#define_classes(files)

mesh_file = "./models/0/m0/m0.off"

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
viewer = Viewer(Object.load_mesh(mesh_file))
viewer.mainLoop()