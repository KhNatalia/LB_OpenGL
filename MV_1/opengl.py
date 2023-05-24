from OpenGL.GLU import *
from OpenGL.GL import *
from pygame.locals import *
import pygame
import sys


def triangulate(tr_polygon, tr_holes=None):
    """
    Returns a list of triangles.
    Uses the GLU Tesselator functions!
    """
    if tr_holes is None:
        tr_holes = []
    tr_vertices = []

    def edgeFlagCallback(param1, param2): pass

    def beginCallback(param=None):
        vertices = []

    def vertexCallback(vertex, otherData=None):
        tr_vertices.append(vertex[:2])

    def combineCallback(vertex, neighbors, neighborWeights, out=None):
        out = vertex
        return out
    def endCallback(data=None): pass

    tess = gluNewTess()
    gluTessProperty(tess, GLU_TESS_WINDING_RULE, GLU_TESS_WINDING_ODD)
    # forces triangulation of polygons (i.e. GL_TRIANGLES) rather than returning triangle fans or strips
    gluTessCallback(tess, GLU_TESS_EDGE_FLAG_DATA, edgeFlagCallback)
    gluTessCallback(tess, GLU_TESS_BEGIN, beginCallback)
    gluTessCallback(tess, GLU_TESS_VERTEX, vertexCallback)
    gluTessCallback(tess, GLU_TESS_COMBINE, combineCallback)
    gluTessCallback(tess, GLU_TESS_END, endCallback)
    gluTessBeginPolygon(tess, 0)

    # first handle the main polygon
    gluTessBeginContour(tess)
    for point in tr_polygon:
        point3d = (point[0], point[1], 0)
        gluTessVertex(tess, point3d, point3d)
    gluTessEndContour(tess)

    # then handle each of the holes, if applicable
    if tr_holes:
        for hole in tr_holes:
            gluTessBeginContour(tess)
            for point in hole:
                point3d = (point[0], point[1], 0)
                gluTessVertex(tess, point3d, point3d)
            gluTessEndContour(tess)

    gluTessEndPolygon(tess)
    gluDeleteTess(tess)
    return tr_vertices


if __name__ == "__main__":
    width, height = 550, 400
    pygame.init()
    pygame.display.set_mode((width, height), DOUBLEBUF|OPENGL)
    pygame.display.set_caption("Tesselation Demo")
    clock = pygame.time.Clock()
    glClear(GL_COLOR_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, width, height, 0, -1, 1)     # flipped so top-left = (0, 0)!
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # define the polygon and some holes
    polygon = [(0, 0), (550, 0), (550, 400), (275, 200), (0, 400)]
    hole1 = [(10, 10), (10, 100), (100, 100), (100, 10)]
    hole2 = [(300, 50), (350, 100), (400, 50), (350, 200)]
    holes = [hole1, hole2]
    vertices = triangulate(polygon, tr_holes=holes)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        glColor(1, 0, 0)
        glBegin(GL_TRIANGLES)
        for vertex in vertices:
            glVertex(*vertex)
        glEnd()

        pygame.display.flip()
        clock.tick_busy_loop(60)
