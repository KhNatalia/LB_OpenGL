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

        self.arr_bits = self.ds[0x280100].value
        self.is_Sober = False


    def init(self):
        glClearColor(0, 0, 0, 0.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glColor3f(1, 1, 1)

        draw_pixel = np.copy(self.image_pixels)
        # перевіряємо чи потрібно виконувати фільтрацію
        if self.is_Sober:
            draw_pixel = self.filtration(draw_pixel, 2)

        self.draw_texture(draw_pixel, GL_LUMINANCE)

        self.print_text(0, self.height - 40, GLUT_BITMAP_HELVETICA_12, "'r' - return")
        self.print_text(0, self.height - 30, GLUT_BITMAP_HELVETICA_12, "'s' - Sobel filter")
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

    # функція виконує фільтрацію
    def filtration(self, data, border_size):
        arr_filter = np.zeros((self.height, self.width))    # відфільтрований масив

        data_norm = self.normalization_func(data, 0.7, 1)   # нормалізовані дані
        data_pad = self.border_pixels(data_norm, border_size)   # нові дані з доданими границями

        for i in range(self.height):
            for j in range(self.width):
                # викликаємо фільтр для кожного пікселя
                arr_filter[i, j] = self.filter_Sobel(data_pad[i:i + 3, j:j + 3])

        return np.array(arr_filter, np.uint8)

    # функція виконує нормальзацію
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

    # довизначаємо границі пікселів за межами зображення
    def border_pixels(self, data, size):
        height, weigh = data.shape

        # розміри збільшеного масиву
        new_height, new_weigh = height + 2 * size, weigh + 2 * size
        # новий массив
        new_data = np.zeros((new_height, new_weigh))

        # довизначаємо границі пікселів за межами зображення
        for i in range(new_height):
            for j in range(new_weigh):
                new_data[i][j] = data[(i - size) % height][(j - size) % weigh]

        return np.array(new_data, np.uint8)

    # фільтр Собеля
    def filter_Sobel(self, data):
        x_mask = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
        y_mask = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])

        return np.sqrt((x_mask * data).sum()**2 + (y_mask * data).sum()**2)

    def keyboard_func(self, my_key, x, y):
        key = unicode(my_key, errors='ignore')
        if key == 's':
            self.is_Sober = True
        if key == 'r':
            self.is_Sober = False
        self.display()


def init_window(width, height):
    glutInitWindowSize(width, height)
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH) - width) // 2, (glutGet(GLUT_SCREEN_HEIGHT) - height) // 2)
    glutCreateWindow('KP_3')


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
