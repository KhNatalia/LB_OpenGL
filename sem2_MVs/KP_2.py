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

        self.mouse_on_image = False
        self.x_coord, self.y_coord = 0, 0

        self.is_normalization = False
        self.is_inversion = False

    def init(self):
        glClearColor(0, 0, 0, 0.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glColor3f(1, 1, 1)

        draw_pixel = np.copy(self.image_pixels)
        if self.is_normalization:
            draw_pixel = self.normalization_func(draw_pixel, 0.75, 1)
        elif self.is_inversion:
            draw_pixel = self.inversion_func(draw_pixel)

        self.draw_texture(draw_pixel, GL_LUMINANCE)

        if self.mouse_on_image:
            self.print_text(0, 10, GLUT_BITMAP_HELVETICA_12, "(" + str(draw_pixel[self.x_coord][self.height - self.y_coord]) + ")")

        self.print_text(0, self.height - 40, GLUT_BITMAP_HELVETICA_12, "'r' - return")
        self.print_text(0, self.height - 30, GLUT_BITMAP_HELVETICA_12, "'n' - histogram normalization")
        self.print_text(0, self.height - 20, GLUT_BITMAP_HELVETICA_12, "'i' - inversion images")
        self.print_text(0, self.height - 10, GLUT_BITMAP_HELVETICA_12, "Press the key:")

        glutSwapBuffers()

    def print_text(self, x, y, font, line):
        glColor3f(0, 0, 1)
        glPushAttrib(GL_DEPTH_TEST)
        glRasterPos2d(x, y)
        for i in line:
            glutBitmapCharacter(font, ord(i))
        glPopAttrib()

    def draw_texture(self, data, internal_format):
        gl_type = ARRAY_TO_GL_TYPE_MAPPING.get(data.dtype)

        glTexImage2D(GL_TEXTURE_2D, 0, internal_format, self.width, self.height, 0, internal_format, gl_type, data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glEnable(GL_TEXTURE_2D)

        glBegin(GL_QUADS)
        glTexCoord2d(0.0, 0.0)
        glVertex2d(0.0, 0.0)
        glTexCoord2d(1.0, 0.0)
        glVertex2d(self.width, 0.0)
        glTexCoord2d(1.0, 1.0)
        glVertex2d(self.width, self.height)
        glTexCoord2d(0.0, 1.0)
        glVertex2d(0.0, self.height)
        glEnd()

        glDisable(GL_TEXTURE_2D)

    def normalization_func(self, pixels, p_min, p_max):
        pixel_max = int(float(p_max * pixels.max()))
        pixel_min = int(float(p_min * pixels.max()))

        new_min = 0
        new_max = 255
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

        return np.array(normalization, np.uint8)

    def inversion_func(self, pixels):
        pixel_max = int(float(pixels.max()))
        pixel_min = int(float(pixels.min()))

        inversion = []

        for row in pixels:
            new_row = []
            for pixel in row:
                new_pixel = pixel_max - pixel + pixel_min
                new_row.append(new_pixel)
            inversion.append(new_row)

        return np.array(inversion, np.uint8)

    def pixels_transformations(self, data):
        transform_image = []
        for i in range(self.width):
            transform_image.append([])
            for j in range(self.height):
                transform_image[i].append(data[i][j] and self.image_pixels[i][j])

        return transform_image

    def keyboard_func(self, my_key, x, y):
        key = unicode(my_key, errors='ignore')
        if key == 'n':
            self.is_normalization = True
            self.is_inversion = False
        if key == 'i':
            self.is_inversion = True
            self.is_normalization = False
        if key == 'r':
            self.is_inversion = False
            self.is_normalization = False

    def motion_func(self, x, y):
        self.x_coord, self.y_coord = x, y
        if (0 < x < self.width) and (0 < y < self.height):
            self.mouse_on_image = True
        else:
            self.mouse_on_image = False
        self.display()


def init_window(width, height):
    glutInitWindowSize(width, height)
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH) - width) // 2, (glutGet(GLUT_SCREEN_HEIGHT) - height) // 2)
    glutCreateWindow('KP_2')


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    file = Image(path_file)
    init_window(file.width, file.height)
    file.init()
    glutDisplayFunc(file.display)
    glutKeyboardFunc(file.keyboard_func)
    glutPassiveMotionFunc(file.motion_func)
    glutMainLoop()


if __name__ == '__main__':
    main()
