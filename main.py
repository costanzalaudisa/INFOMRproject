import trimesh
from viewer import Viewer

# Load an example mesh
mesh = trimesh.load('./models/m0/m0.off', force='mesh')
mesh_center = (0.333778, 0.277507, 0.423717)

# Show the mesh using the viewer
viewer = Viewer(mesh, mesh_center)
viewer.mainLoop()
