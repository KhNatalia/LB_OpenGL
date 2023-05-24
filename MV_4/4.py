from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pydicom
import numpy as np
from pydicom.uid import generate_uid

path_file = "DICOM_Image_for_Lab_2.dcm"


class Image:
    def __init__(self, path):
        self.high_border = 180
        self.low_border = 15
        self.scaling_factor = 0.0101769
        self.shear_ratio = 3.142
        self.min_el = 0
        self.max_el = 255

        self.ds = pydicom.read_file(path)
        self.new_ds = pydicom.read_file(path)

        self.intercept = self.ds[0x0281053].value
        self.slope = self.ds[0x0281052].value

        self.image_pixels = self.ds.pixel_array
        self.new_image_pixels = np.array(self.image_pixels).astype(float)

        self.bits = self.ds[0x280100].value
        self.data_type = GL_FLOAT if (self.slope != 0) & (self.intercept != 1) else GL_UNSIGNED_BYTE if self.bits == 8 else GL_UNSIGNED_INT
        self.width, self.height = self.ds[0x280010].value, self.ds[0x280011].value
        self.isTextVisible = True

    def init(self):
        glClearColor(0, 0, 0, 0.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glColor3f(1, 1, 1)

        self.draw_texture(self.new_image_pixels, self.data_type)
        if self.isTextVisible:
            self.print_text(5, self.height - 10, GLUT_BITMAP_HELVETICA_12, "Max value: " + str(self.max_el))
            self.print_text(5, self.height - 25, GLUT_BITMAP_HELVETICA_12, "Min value: " + str(self.min_el))
            self.print_text(5, self.height - 40, GLUT_BITMAP_HELVETICA_12, "Type: " + str(self.data_type))
            self.print_text(5, self.height - 55, GLUT_BITMAP_HELVETICA_12, "Slope: " + str(self.slope))
            self.print_text(5, self.height - 70, GLUT_BITMAP_HELVETICA_12, "Intercept: " + str(self.intercept))
        glutSwapBuffers()

    def print_text(self, x, y, font, line):
        glColor3f(1, 1, 1)
        glPushAttrib(GL_DEPTH_TEST)
        glRasterPos2d(x, y)
        for i in line:
            glutBitmapCharacter(font, ord(i))
        glPopAttrib()

    def draw_texture(self, data, data_type):
        glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, self.width, self.height, 0, GL_LUMINANCE, data_type, data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
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

    def change_value(self):
        for i in range(self.height):
            for j in range(self.width):
                if self.new_image_pixels[i, j] > self.high_border:
                    self.new_image_pixels[i, j] = float(self.high_border * self.scaling_factor + self.shear_ratio)
                elif self.new_image_pixels[i, j] < self.low_border:
                    self.new_image_pixels[i, j] = float(self.low_border * self.scaling_factor + self.shear_ratio)
                else:
                    self.new_image_pixels[i, j] = float(self.new_image_pixels[i, j] * self.scaling_factor + self.shear_ratio)
        self.min_el, self.max_el = self.new_image_pixels.min(), self.new_image_pixels.max()
        for i in range(self.height):
            for j in range(self.width):
                self.new_image_pixels[i, j] = ((self.new_image_pixels[i, j] - self.min_el) * (self.high_border - self.low_border)) / (self.max_el - self.min_el) + self.low_border

    def return_value(self):
        self.new_image_pixels = np.array(self.image_pixels).astype(float)

    def mouse_func(self, button, state, x, y):
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            self.slope = self.scaling_factor
            self.intercept = self.shear_ratio
            self.change_value()
            self.display()
        if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
            self.max_el = 255
            self.min_el = 0
            self.intercept = self.ds[0x0281053].value
            self.slope = self.ds[0x0281052].value
            self.return_value()
            self.display()

    def save_to_file(self):
        self.new_ds.PixelData = self.new_image_pixels.tobytes()
        self.new_ds[0x0281052].value = self.slope
        self.new_ds[0x0281053].value = self.intercept
        self.new_ds[0x0080008].value = ('DERIVED', 'SECONDARY')
        self.new_ds[0x008103e].value = 'slope-{0}, intercept-{1}'.format(self.slope, self.intercept)
        if 'SeriesDescriptionCode' in self.new_ds.trait_names():
            del self.new_ds[0x008103f]
        self.new_ds[0x0020000d].value = self.new_ds[0x0020000d].value
        self.new_ds[0x020000E].value = generate_uid()
        self.ds[0x0200011].value = 2
        self.ds[0x0200013].value = 1
        self.ds[0x0080018].value = generate_uid()
        self.ds.add_new(tag=0x0020003, VR='UI', value=self.ds[0x0080018].value)
        self.new_ds.save_as('new_DICOM.dcm')

    def keyboard_func(self, my_key, x, y):
        key = unicode(my_key, errors='ignore')
        if key == 's':
            self.save_to_file()


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
    glutMouseFunc(file.mouse_func)
    glutMainLoop()


if __name__ == '__main__':
    main()
