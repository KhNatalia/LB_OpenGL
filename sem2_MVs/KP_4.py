import operator
import pickle

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
        self.is_Segmentation = False


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
        if self.is_Segmentation:
            draw_pixel = self.traingle_thresholding(draw_pixel)

        self.draw_texture(draw_pixel, GL_LUMINANCE)

        self.print_text(0, self.height - 40, GLUT_BITMAP_HELVETICA_12, "'r' - return")
        self.print_text(0, self.height - 30, GLUT_BITMAP_HELVETICA_12, "'t' - Triangle thresholding")
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
    def traingle_thresholding(self, data):
        data_norm = self.normalization_func(data, 0, 1)   # нормалізовані дані

        # будуємо гістограму
        hist_value = {key: (data_norm == key).sum() for key in range(data_norm.min(), data_norm.max() + 1)}
        hist = list(hist_value.values())
        b_min, b_max = np.argmin(hist), np.argmax(hist)

        # розраховуємо найбільшу відстань між лінієї(від мінімуму до максимуму гістограми) та рівнями яскравості
        x = [el for el in reversed(range(b_max, b_min + 1, 1))]
        dist = {key: self.distance(b_min, b_max, key, hist[b_min], hist[b_max], hist[key]) for key in x}
        tresholding = max(dist.items(), key=operator.itemgetter(1))[0]  # порогове значення

        # сегментоване зображення
        mask = np.copy(data_norm)
        for i in range(len(mask)):
            for j in range(len(mask[i])):
                if mask[i][j] < tresholding:
                    mask[i][j] = 0
                elif mask[i][j] >= tresholding:
                    mask[i][j] = 255

        self.save(data_norm, mask)
        return mask

    # функція визначає відстань між лінієї(від мінімуму до максимуму гістограми) та рівня яскравості
    def distance(self, x_min, x_max, x_key, y_min, y_max, y_key):
        A, B, C = self.equation_line(x_min, x_max, y_min, y_max)
        answer = np.abs(A * x_key + B * y_key + C) / np.sqrt(A**2 + B**2)
        return answer

    # функція розраховує парамеьтри для рівняння прямої
    def equation_line(self, x1, x2, y1, y2):
        A = y2 - y1
        B = -(x2 - x1)
        C = -x1 * (y2 - y1) + y1 * (x2 - x1)
        return A, B, C

    # функція виконує збереження данних
    def save(self, data_norm, mask):
        # утворюємо таблицю властивостей
        table = [{'x': x, 'y': y, 'mask': mask[x, y], 'value': data_norm[x, y]}
                 for x in range(data_norm.shape[0]) for y in range(data_norm.shape[1])]

        with open('filename.pickle', 'wb') as handle:
            pickle.dump(table, handle, protocol=pickle.HIGHEST_PROTOCOL)

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

        return np.array(normalization, np.uint8)

    def keyboard_func(self, my_key, x, y):
        key = unicode(my_key, errors='ignore')
        if key == 't':
            self.is_Segmentation = True
        if key == 'r':
            self.is_Segmentation = False
        self.display()


def init_window(width, height):
    glutInitWindowSize(width, height)
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH) - width) // 2, (glutGet(GLUT_SCREEN_HEIGHT) - height) // 2)
    glutCreateWindow('KP_4')


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
