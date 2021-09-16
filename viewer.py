from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import trimesh

# Define window width and height
W, H = 500, 500

# Load an example mesh
mesh = trimesh.load('./models/m0/m0.off', force='mesh')

# Render a mesh from the center of the screen
def render_mesh(mesh: trimesh.Trimesh):
    glLoadIdentity()
    glColor3f(1.0, 0, 0)

    for face in mesh.faces:
        glBegin(GL_TRIANGLES)
        for vertex_index in face:
            x, y, z = mesh.vertices[vertex_index]
            glColor3f(1.0, 0, 0)
            glVertex3f(x, y, z)
        glEnd()

# Clear the screen and render a mesh
def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    render_mesh(mesh)

    glutSwapBuffers()

# Do panning / zooming / whatever here
def reshapeView():
    pass

glutInit()
glutInitDisplayMode(GLUT_RGBA)
glutInitWindowSize(W, H)
window = glutCreateWindow("INFOMR Viewer")
glutDisplayFunc(showScreen)
glutReshapeFunc(reshapeView)
glutMainLoop()
