from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pydicom
import numpy as np

path_file1 = "2-mri.dcm"
path_file2 = "2-ct.dcm"


class Image:
    def __init__(self):
        self.image1 = pydicom.read_file(path_file1)
        self.image2 = pydicom.read_file(path_file2)

        self.width1, self.height1 = self.image1[0x280011].value, self.image1[0x280010].value
        self.width2, self.height2 = self.image2[0x280011].value, self.image2[0x280010].value

        self.pixels = []

    @staticmethod
    def max_brightness(image):
        image_type = np.dtype('int' + str(image[0x280100].value))
        return np.iinfo(image_type).max

    def colored_image(self, image):
        output = []
        image_pixels = image.pixel_array

        p_max = np.amax(image_pixels)
        p_min = np.amin(image_pixels)
        delta = p_max - p_min
        max_brightness = self.max_brightness(image)

        for row in image_pixels:
            new_row = []
            for pixel in row:
                new_pixel = int((float(pixel) / delta) * max_brightness)
                if new_pixel < 0:
                    new_pixel = 0
                elif new_pixel > max_brightness:
                    new_pixel = max_brightness
                new_row.append([new_pixel, new_pixel, new_pixel, max_brightness])
            output.append(new_row)

        return output

    def init(self):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, glGenTextures(1))

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width1, self.height1, 0, GL_RGBA, GL_UNSIGNED_BYTE, self.pixels)

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)

        glClearColor(0, 0, 0, 0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        gluOrtho2D(-self.width2 / 2, self.width2 / 2, -self.height2 / 2, self.height2 / 2)

    def display(self):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT)
        self.draw_texture()

    def draw_texture(self):
        glBegin(GL_QUADS)
        glTexCoord2d(0.0, 0.0)
        glVertex2d(self.width2 / 2, self.height2 / 2)
        glTexCoord2d(0.0, 1.0)
        glVertex2d(self.width2 / 2, -self.height2 / 2)
        glTexCoord2d(1.0, 1.0)
        glVertex2d(-self.width2 / 2, -self.height2 / 2)
        glTexCoord2d(1.0, 0.0)
        glVertex2d(-self.width2 / 2, self.height2 / 2)
        glEnd()
        glFlush()

    def multimodal_image(self):
        output = []
        size = 40

        image1 = self.colored_image(self.image1)
        image2 = self.colored_image(self.image2)

        num_i = 0
        for i in range(len(image1)):
            new_row = []
            if num_i == size:
                num_i = 0
            num_j = 0
            for j in range(len(image1[0])):
                new_pixel = image1[i][j]
                if num_j == size:
                    num_j = 0
                if i < len(image1) / 2:
                    if ((0 <= num_i < (size / 2)) and ((size / 2) <= num_j < size)) or (((size / 2) <= num_i < size) and (0 <= num_j < (size / 2))):
                        new_pixel = image2[i][j]
                new_row.append([new_pixel[0], new_pixel[1], new_pixel[2], new_pixel[3]])
                num_j += 1
            output.append(new_row)
            num_i += 1

        return output

    def keyboard_func(self, my_key, x, y):
        key = unicode(my_key, errors='ignore')
        if key == '1':
            self.pixels = self.colored_image(self.image1)
        if key == '2':
            self.pixels = self.colored_image(self.image2)
        if key == 'm':
            self.pixels = self.multimodal_image()

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width1, self.height1, 0, GL_RGBA, GL_UNSIGNED_BYTE, self.pixels)
        self.display()


def init_window(width, height):
    glutInitWindowSize(width, height)
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH) - width) // 2, (glutGet(GLUT_SCREEN_HEIGHT) - height) // 2)
    glutCreateWindow('KP_8')


def main():
    glutInit()
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA)
    file = Image()
    init_window(file.width2, file.height2)
    file.init()
    glutDisplayFunc(file.display)
    glutKeyboardFunc(file.keyboard_func)
    glutMainLoop()


if __name__ == '__main__':
    main()
