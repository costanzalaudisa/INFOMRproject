from object import Object
from viewer import Viewer

# Show the mesh using the viewer
viewer = Viewer(Object.load_mesh("./models/m0/m0.off"))
viewer.mainLoop()
