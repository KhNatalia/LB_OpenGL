from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np


class Image:
    def __init__(self):
        self.number_of_images = 112
        self.rows = 512
        self.columns = 512
        self.pixel_spacing = 0.744000
        self.slice_thickness = 3.0
        self.spacing_between_slices = 3.0
        self.scale = 512

        self.X_orientation = np.array([0.0, 1.0, 0.0])
        self.Y_orientation = np.array([0.0, 0.0, -1.0])
        self.x_coord, self.y_coord = 462, 320

        self.image_position_25 = np.array([103.467, -190.625, 1449.592])
        self.image_position_1 = np.array([163.467, -190.625, 1449.592])

        self.position_25 = self.get_position_25()

        self.width, self.height = 600, 600
        self.isTextVisible = False
        self.mouse_on_image = False

    def init(self):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, self.width / self.height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def get_position_25(self):
        position_25 = [
            self.image_position_25[0] + self.rows * self.X_orientation[0] * self.pixel_spacing + self.columns * self.Y_orientation[0] * self.pixel_spacing,
            self.image_position_25[1] + self.rows * self.X_orientation[1] * self.pixel_spacing + self.columns * self.Y_orientation[1] * self.pixel_spacing,
            self.image_position_25[2] + self.rows * self.X_orientation[2] * self.pixel_spacing + self.columns * self.Y_orientation[2] * self.pixel_spacing]
        print(position_25)
        return position_25

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(1.0, 1.0, 1.0, 0.0)

        self.draw_texture()

        self.print_text(0.0, 0.0, 2.0, GLUT_BITMAP_HELVETICA_18, 'z')
        self.print_text(0.0, 2.0, 0.0, GLUT_BITMAP_HELVETICA_18, 'y')
        self.print_text(2.5, 0.0, 0.0, GLUT_BITMAP_HELVETICA_18, 'x')

        self.print_text_2D(-40, -50, GLUT_BITMAP_HELVETICA_12, str(self.position_25))

        glutSwapBuffers()

    def print_text_2D(self, x, y, font, line):
        glColor3f(0, 0, 0)
        glPushAttrib(GL_DEPTH_TEST)
        glRasterPos2d(x, y)
        for i in line:
            glutBitmapCharacter(font, ord(i))
        glPopAttrib()

    def print_text(self, x, y, z, font, line):
        glColor3f(0, 0, 0)
        glPushAttrib(GL_DEPTH_TEST)
        glRasterPos3d(x, y, z)
        for i in line:
            glutBitmapCharacter(font, ord(i))
        glPopAttrib()

    def draw_texture(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -6.0)

        glRotatef(-69.0, 1.0, 0.0, 0.0)
        glRotatef(0.0, 0.0, 1.0, 0.0)
        glRotatef(-119.0, 0.0, 0.0, 1.0)

        # Оси координат
        # ------------------------
        glBegin(GL_LINES)
        # x
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(2.5, 0.0, 0.0)
        # y
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 2.0, 0.0)
        # z
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 2.0)
        glEnd()
        # ------------------------

        # Рисуем куб
        # ------------------------
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # координаты точек куба
        position_0 = [self.image_position_1[0] / self.pixel_spacing / self.scale,
                      self.image_position_1[1] / self.pixel_spacing / self.scale,
                      self.image_position_1[2] / self.spacing_between_slices / self.scale]
        position_1 = [self.rows / self.scale + position_0[0],
                      self.columns / self.scale + position_0[1],
                      ((self.number_of_images - 1) + self.slice_thickness) / self.rows / self.pixel_spacing + position_0[2]]

        x0, y0, z0 = position_0[0], position_0[1], position_0[2]
        x1, y1, z1 = position_1[0], position_1[1], position_1[2]

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)
        glBegin(GL_QUADS)
        glColor3f(0, 0, 0)
        glVertex3f(x1, y1, z0), glVertex3f(x1, y1, z1), glVertex3f(x1, y0, z1), glVertex3f(x1, y0, z0)
        glVertex3f(x1, y1, z0), glVertex3f(x0, y1, z0), glVertex3f(x0, y1, z1), glVertex3f(x1, y1, z1)
        glVertex3f(x1, y0, z0), glVertex3f(x0, y0, z0), glVertex3f(x0, y1, z0), glVertex3f(x1, y1, z0)

        glColor4f(0, 0, 0, 0.2)
        glVertex3f(x0, y1, z1), glVertex3f(x0, y1, z0), glVertex3f(x0, y0, z0), glVertex3f(x0, y0, z1)
        glVertex3f(x1, y1, z1), glVertex3f(x0, y1, z1), glVertex3f(x0, y0, z1), glVertex3f(x1, y0, z1)
        glVertex3f(x1, y0, z1), glVertex3f(x0, y0, z1), glVertex3f(x0, y0, z0), glVertex3f(x1, y0, z0)

        glEnd()
        glDisable(GL_BLEND)
        # ------------------------

        # Рисуем срез
        # ------------------------
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)
        glColor4f(1, 0, 0, 0.2)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        slope_25 = 25 * self.spacing_between_slices / self.scale + z0
        glColor4f(1, 0, 0, 0.2)
        glBegin(GL_QUADS)
        glVertex3f(x0, y1, slope_25), glVertex3f(x1, y1, slope_25), glVertex3f(x1, y0, slope_25), glVertex3f(x0, y0, slope_25)
        glEnd()
        glDisable(GL_BLEND)
        # ------------------------

        # Устанавливаем точку
        # ------------------------
        point = [self.x_coord / self.scale + x0,
                 self.y_coord / self.scale + y0,
                 slope_25]
        glPointSize(5)
        glColor3f(0, 0, 0)
        glBegin(GL_POINTS)
        glVertex3f(point[0], point[1], point[2])
        glEnd()
        # ------------------------


def init_window(width, height):
    glutInitWindowSize(width, height)
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH) - width) // 2, (glutGet(GLUT_SCREEN_HEIGHT) - height) // 2)
    glutCreateWindow('RGR')


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    file = Image()
    init_window(file.width, file.height)
    file.init()
    glutDisplayFunc(file.display)
    glutIdleFunc(file.display)
    glutMainLoop()


if __name__ == '__main__':
    main()
