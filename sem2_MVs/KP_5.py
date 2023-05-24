import math

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
        self.arr_bits = self.ds[0x280100].value
        self.is_Susan = False
        self.isOverlap = False


    def init(self):
        glClearColor(0, 0, 0, 0.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glColor3f(1, 1, 1)

        draw_pixel = np.copy(self.image_pixels)
        self.rows = len(draw_pixel)
        self.cols = len(draw_pixel[0])
        # перевіряємо чи потрібно виконувати фільтрацію

        if self.is_Susan:
            draw_pixel = self.SUSAN(draw_pixel)

        self.draw_texture(draw_pixel, GL_LUMINANCE)
        self.print_text(0, self.height - 40, GLUT_BITMAP_HELVETICA_12, "'r' - return")
        self.print_text(0, self.height - 30, GLUT_BITMAP_HELVETICA_12, "'s' - SUSAN")
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

    def similarityFunction(self, r0, r, t):
        if math.fabs(r - r0) > t:
            return 0
        else:
            return 1

    def filter(self, data, f_size, t):
        res = np.zeros((self.rows, self.cols))
        p_size = (f_size - 1) / 2

        # pad_im = self.pad(res, p_size)
        r = f_size / 2

        for i in range(self.rows):
            for j in range(self.cols):

                v_start = i
                v_end = v_start + f_size
                h_start = j
                h_end = h_start + f_size

                value = 0
                for m in range(v_start, v_end):
                    for n in range(h_start, h_end):
                        if i + m > 0 & j + n > 0 & i + m < self.rows & j + n < self.cols:
                            mask = math.pow(m - r - v_start, 2) + math.pow(n - r- h_start, 2) < math.pow(r, 2)
                            value += self.similarityFunction(data[i][j], data[i][n], t) * mask
                res[i][j] = value
        return res

    def findEdge(self, data, res, f_size, t, g):
        res = self.filter(data, f_size, t)
        for i in range(self.rows):
            for j in range(self.cols):
                if res[i][j] < g:
                    res[i][j] = 2000 - res[i][j]
                else:
                    res[i][j] = 0
        return res

    def getImageEdges(self, data):
        res = []
        res = self.findEdge(data, res, 7, 280, 27)
        if self.isOverlap:
            for i in range(self.rows):
                for j in range(self.cols):
                    if res[i][j] < data[i][j]:
                        res[i][j] = data[i][j]
        return res

    def calcArea(self, x, y, data):
        res = 0
        th = 128    #заданий поріг

        for i in range(-3, 4):
            for j in range(-3, 4):
                if i + x > 0 & j + y > 0 & i + x < len(data[0]) & j + y < len(data):
                    res += math.exp(-math.pow((data[x + i][y + j] - data[x][y]) / th, 2))
        return res

    def findEdges(self, borders_map):
        mask_radius = 3

        for i in range(len(borders_map)):
            for j in range(len(borders_map[0])):
                v_start = 0 if i - mask_radius - 1 < 0 else i - mask_radius - 1
                v_end = self.rows - 1 if i + mask_radius > self.rows else i + mask_radius
                h_start = 0 if j - mask_radius - 1 < 0 else j - mask_radius - 1
                h_end = self.cols - 1 if j + mask_radius > self.cols else j + mask_radius

                similarity = 0
                # for v in range(v_start, v_end):
                #     for h in range(h_start, h_end):




    def SUSAN(self, data):
        data = self.normalization_func(data, 0, 1)
        mask_radius = 7
        output = np.copy(data)

        r = mask_radius / 2.0

        for i in range(self.rows):
            for j in range(self.cols):
                v_start = 0 if i - mask_radius - 1 < 0 else i - mask_radius - 1
                v_end = self.rows - 1 if i + mask_radius > self.rows else i + mask_radius
                h_start = 0 if j - mask_radius - 1 < 0 else j - mask_radius - 1
                h_end = self.cols - 1 if j + mask_radius > self.cols else j + mask_radius

                similarity = 0
                for v in range(v_start, v_end):
                    for h in range(h_start, h_end):
                        if (v == v_start and h == h_start) or (v == v_start and h == h_end - 1) or (v == v_end - 1 and h == h_start) or (v == v_end - 1 and h == h_end - 1):
                            similarity += 1
                        else:
                            # mask = (math.pow(v - r - v_start, 2) + math.pow(h - r - h_start, 2)) < math.pow(r, 2)
                            similarity += self.similarityFunction(output[i][j], output[v][h], 50) #* mask

                output[i][j] = similarity

        geo_threshold = output.max() / 2
        borders_map = np.copy(output)

        for i in range(len(output)):
            for j in range(len(output[0])):
                if output[i][j] < geo_threshold:
                    borders_map[i][j] = geo_threshold - output[i][j]
                else:
                    borders_map[i][j] = 0

        # center_mass = (borders_map * np.mgrid[0:borders_map.shape[0], 0:borders_map.shape[1]]).sum(1).sum(1)/borders_map.sum()
        max_val = borders_map.max()
        print(max_val)
        for i in range(len(output)):
            for j in range(len(output[0])):
                if borders_map[i][j] != 0:
                    borders_map[i][j] = 255
        #         else:
        #             borders_map[i][j] = 0
        print("yes")
        return np.array(borders_map, np.uint8)

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
        # return np.array(normalization, np.uint8)

    def keyboard_func(self, my_key, x, y):
        key = unicode(my_key, errors='ignore')
        if key == 's':
            self.is_Susan = True
        if key == 'r':
            self.is_Susan = False
        self.display()


def init_window(width, height):
    glutInitWindowSize(width, height)
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH) - width) // 2, (glutGet(GLUT_SCREEN_HEIGHT) - height) // 2)
    glutCreateWindow('KP_5')


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
