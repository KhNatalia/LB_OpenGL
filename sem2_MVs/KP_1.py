from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pydicom
import numpy as np

path_file = "DICOM_Image_for_Lab_2.dcm"


class Image:
    def __init__(self, path):
        self.ds = pydicom.read_file(path)
        self.image_pixels = np.array(self.ds.pixel_array)
        self.width, self.height = self.ds[0x280010].value, self.ds[0x280011].value

    def init(self):
        glClearColor(0, 0, 0, 0.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glColor3f(1, 1, 1)

        self.draw_texture(self.image_pixels, GL_LUMINANCE)

        self.print_text(10, 10, GLUT_BITMAP_HELVETICA_12, "'g' - change color channel")
        self.print_text(10, 20, GLUT_BITMAP_HELVETICA_12, "'b' - bit mask overlay")
        self.print_text(10, 30, GLUT_BITMAP_HELVETICA_12, "Press the key:")

        glutSwapBuffers()

    def print_text(self, x, y, font, line):
        glColor3f(1, 1, 1)
        glPushAttrib(GL_DEPTH_TEST)
        glRasterPos2d(x, y)
        for i in line:
            glutBitmapCharacter(font, ord(i))
        glPopAttrib()

    def draw_texture(self, data, internal_format):
        bits = self.ds[0x280100].value
        r_intercept = self.ds[0x281053].value
        r_slope = self.ds[0x281052].value

        if (r_slope != 0) & (r_intercept != 1):
            data_type = GL_FLOAT
        elif bits == 8:
            data_type = GL_UNSIGNED_BYTE

        glTexImage2D(GL_TEXTURE_2D, 0, internal_format, self.width, self.height, 0, internal_format, data_type, data)
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

    def create_bit_mask(self):
        bit_mask = []

        for i in range(self.width):
            bit_mask.append([])
            for j in range(self.height):
                if i >= j:
                    bit_mask[i].append(0)
                else:
                    bit_mask[i].append(255)

        return bit_mask

    def boolean_transformations(self, data):
        transform_image = []
        for i in range(self.width):
            transform_image.append([])
            for j in range(self.height):
                transform_image[i].append(data[i][j] and self.image_pixels[i][j])

        return transform_image

    def create_gradient(self):
        gradient = {}
        color = 0
        for key in range(np.amin(self.image_pixels), np.amax(self.image_pixels) // 2):
            gradient[key] = color
            color += 1
            if color > np.amax(self.image_pixels):
                color = 255
        for key in range(np.amax(self.image_pixels) // 2, np.amax(self.image_pixels) + 1):
            gradient[key] = color
            color -= 1
            if color < 0:
                color = 0

        gradient_image = []
        for pixel_line in self.image_pixels:
            line = []
            for pixel in pixel_line:
                line.append(gradient[pixel])
            gradient_image.append(line)

        return np.array(gradient_image)

    def channel_G(self, data):
        rgb = np.zeros((self.height, self.width, 3), 'uint8')

        rgb[..., 1] = data
        rgb[..., 0] = 0
        rgb[..., 2] = 0

        return rgb

    def keyboard_func(self, my_key, x, y):
        key = unicode(my_key, errors='ignore')
        if key == 'g':
            gradient = self.create_gradient()
            self.draw_texture(self.channel_G(gradient), GL_RGB)

            self.print_text(10, 10, GLUT_BITMAP_HELVETICA_12, "'b' - bit mask overlay")
            self.print_text(10, 20, GLUT_BITMAP_HELVETICA_12, "'r' - return to normal image")
            self.print_text(10, 30, GLUT_BITMAP_HELVETICA_12, "Press the key:")

            glutSwapBuffers()
        if key == 'b':
            bit_mask = self.create_bit_mask()
            self.draw_texture(self.boolean_transformations(bit_mask), GL_LUMINANCE)

            self.print_text(10, 10, GLUT_BITMAP_HELVETICA_12, "'g' - change color channel")
            self.print_text(10, 20, GLUT_BITMAP_HELVETICA_12, "'r' - return to normal image")
            self.print_text(10, 30, GLUT_BITMAP_HELVETICA_12, "Press the key:")

            glutSwapBuffers()
        if key == 'r':
            self.draw_texture(self.image_pixels, GL_LUMINANCE)

            self.print_text(10, 10, GLUT_BITMAP_HELVETICA_12, "'g' - change color channel")
            self.print_text(10, 20, GLUT_BITMAP_HELVETICA_12, "'b' - bit mask overlay")
            self.print_text(10, 30, GLUT_BITMAP_HELVETICA_12, "Press the key:")

            glutSwapBuffers()


def init_window(width, height):
    glutInitWindowSize(width, height)
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH) - width) // 2, (glutGet(GLUT_SCREEN_HEIGHT) - height) // 2)
    glutCreateWindow('KP_1')


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    file = Image(path_file)
    init_window(file.width, file.height)
    file.init()
    glutDisplayFunc(file.display)
    glutKeyboardFunc(file.keyboard_func)
    glutMainLoop()


if __name__ == '__main__':
    main()
