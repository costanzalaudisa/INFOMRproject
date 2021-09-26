from object import Object
from viewer import Viewer

from classes import define_classes
from filter import get_info

mesh_file = "./models/0/m0/m0.off"

files = ['./classes/train.cla', './classes/test.cla']
define_classes(files)

get_info(mesh_file)

# Show the mesh using the viewer
viewer = Viewer(Object.load_mesh(mesh_file))
viewer.mainLoop()