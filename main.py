import trimesh
from viewer import Viewer

# Load an example mesh
mesh = trimesh.load('./models/m0/m0.off', force='mesh')
print(mesh)

# Automatically look for center values in info.txt file (A/N: could be better?)
with open('./models/m0/m0_info.txt') as file:
    lines = file.readlines()
    lines = [line.rstrip() for line in lines]

for line in lines:
    if 'center' in line:
        value = line[line.find('('):]
        mesh_center = eval(value)

#mesh_center = (0.333778, 0.277507, 0.423717)

# Show the mesh using the viewer
viewer = Viewer(mesh, mesh_center)
viewer.mainLoop()