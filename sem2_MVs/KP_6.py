from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pydicom
import numpy as np
from OpenGL.arrays.numpymodule import ARRAY_TO_GL_TYPE_MAPPING

path_file = "DICOM_Image_16b.dcm"


class Image:
    def __init__(self, path):
        self.ds = pydicom.read_file(path)
        self.image_pixels = np.array(self.ds.pixel_array)
        self.width, self.height = self.ds[0x280010].value, self.ds[0x280011].value

        self.rows = 0; self.cols = 0

        self.isTransform = False
        self.isReverse = False
        self.isReturn = False

        line = float(input("Enter the line to perform mirroring: "))
        coef = float(input("Enter the scaling factor more then 0: "))
        while coef < 0:
            сoef = float(input("Enter the scaling factor more then 0: "))

        # розрахунок матриць для двовимірного геометричного перетворення
        # матрися відзеркалення відносно лінії паралельної до осі Оу
        matrix_mirroring = np.array([[-1, 0, 0, 0],
                                     [0, 1, 0, 0],
                                     [0, 0, 1, 0],
                                     [2 * line, 0, 0, 1]])

        # масштабування відносно осі Оу
        matrix_scaling = np.array([[1, 0, 0, 0],
                                   [0, coef, 0, 0],
                                   [0, 0, 1, 0],
                                   [0, 0, 0, 1]])

        self.default_matrix = None
        # множення матриць для виконання геометричного перетворення
        self.matrix_transform = matrix_mirroring.dot(matrix_scaling)
        # зворотня матриця для оберненного геометричного перетворення
        self.reverse_matrix_transform = np.linalg.inv(self.matrix_transform)

    def init(self):
        glClearColor(0, 0, 0, 0.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(-self.width / 2, self.width / 2, -self.height / 2, self.height / 2)
        glMatrixMode(GL_MODELVIEW)
        self.default_matrix = glGetFloatv(GL_MODELVIEW_MATRIX)

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glColor3f(1, 1, 1)

        draw_pixel = np.copy(self.image_pixels)
        self.rows = len(draw_pixel)
        self.cols = len(draw_pixel[0])

        draw_pixel = self.normalization_func(draw_pixel, 0, 1)

        if self.isTransform:
            self.draw_texture(np.array(draw_pixel, np.uint8), GL_LUMINANCE, 'c')
        elif self.isReverse:
            self.draw_texture(np.array(draw_pixel, np.uint8), GL_LUMINANCE, 'r')
        elif self.isReturn:
            self.draw_texture(np.array(draw_pixel, np.uint8), GL_LUMINANCE, 'b')
        else:
            self.draw_texture(np.array(draw_pixel, np.uint8), GL_LUMINANCE, '')
        # self.print_text(- self.width / 2, self.height / 2 - 40, GLUT_BITMAP_HELVETICA_12, "'b' - back to start position ")
        # self.print_text(- self.width / 2, self.height / 2 - 30, GLUT_BITMAP_HELVETICA_12, "'r' - reverse transformation")
        # self.print_text(- self.width / 2, self.height / 2 - 20, GLUT_BITMAP_HELVETICA_12, "'c' - complex transformation")
        # self.print_text(- self.width / 2, self.height / 2 - 10, GLUT_BITMAP_HELVETICA_12, "Press the key:")

        glutSwapBuffers()

    # def print_text(self, x, y, font, line):
    #     glColor3f(0, 0, 1)
    #     glPushAttrib(GL_DEPTH_TEST)
    #     glRasterPos2d(x, y)
    #     for i in line:
    #         glutBitmapCharacter(font, ord(i))
    #     glPopAttrib()

    def draw_texture(self, data, internal_format, type_transform):
        gl_type = ARRAY_TO_GL_TYPE_MAPPING.get(data.dtype)

        glTexImage2D(GL_TEXTURE_2D, 0, internal_format, self.width, self.height, 0, internal_format, gl_type, data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glEnable(GL_TEXTURE_2D)

        glMatrixMode(GL_MODELVIEW)
        glLoadMatrixf(glGetFloatv(GL_MODELVIEW_MATRIX))
        if type_transform == 'c':
            glMultMatrixf(self.matrix_transform)
            self.isTransform = False
        elif type_transform == 'r':
            glMultMatrixf(self.reverse_matrix_transform)
            self.isReverse = False
        elif type_transform == 'b':
            glLoadMatrixf(self.default_matrix)

        self.default()

        glDisable(GL_TEXTURE_2D)
        glFlush()

    def default(self):
        glBegin(GL_QUADS)
        glTexCoord2d(0.0, 0.0)
        glVertex2d(-self.width / 4, -self.height / 4)
        glTexCoord2d(0.0, 1.0)
        glVertex2d(-self.width / 4, self.height / 4)
        glTexCoord2d(1.0, 1.0)
        glVertex2d(self.width / 4, self.height / 4)
        glTexCoord2d(1.0, 0.0)
        glVertex2d(self.width / 4, -self.height / 4)
        glEnd()

    # функція виконує нормальзацію
    def normalization_func(self, pixels, p_min, p_max):
        pixel_max = int(float(p_max * pixels.max()))
        pixel_min = int(float(p_min * pixels.max()))

        new_min = 0
        new_max = np.iinfo(np.int8).max#255
        normalization = []

        for row in pixels:
            new_row = []
            for pixel in row:
                new_pixel = ((pixel - pixel_min) / (pixel_max - pixel_min)) * (new_max - new_min)
                if new_pixel <= 0:
                    new_pixel = 0
                if new_pixel > new_max:
                    new_pixel = new_max
                new_row.append(new_pixel)
            normalization.append(new_row)

        return normalization

    def keyboard_func(self, my_key, x, y):
        key = unicode(my_key, errors='ignore')
        if key == 'c':
            self.isTransform = True
            self.isReverse = False
            self.isReturn = False
        if key == 'r':
            self.isTransform = False
            self.isReverse = True
            self.isReturn = False
        if key == 'b':
            self.isTransform = False
            self.isReverse = False
            self.isReturn = True
        self.display()

def init_window(width, height):
    glutInitWindowSize(width, height)
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH) - width) // 2, (glutGet(GLUT_SCREEN_HEIGHT) - height) // 2)
    glutCreateWindow('KP_6')


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    file = Image(path_file)
    init_window(file.width * 2, file.height * 2)
    file.init()
    glutDisplayFunc(file.display)
    glutKeyboardFunc(file.keyboard_func)
    glutMainLoop()


if __name__ == '__main__':
    main()
