from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pydicom
import numpy as np
import math
from pydicom.uid import generate_uid

path_file = "copy of DICOM_Image_for_Lab_2.dcm"


class Image:
    def __init__(self, path):
        self.ds = pydicom.read_file(path)
        self.image_pixels = np.array(self.ds.pixel_array)

        self.image_position = np.array(self.ds[0x0200032].value)
        self.X_orientation = np.array(self.ds[0x0200037].value[:3])
        self.Y_orientation = np.array(self.ds[0x0200037].value[3:6])
        self.letter_X = self.check_letters(self.X_orientation[0], self.X_orientation[1], self.X_orientation[2])
        self.letter_Y = self.check_letters(self.Y_orientation[0], self.Y_orientation[1], self.Y_orientation[2])
        self.patient_orientation = self.ds[0x0200020].value

        self.width, self.height = self.ds[0x280010].value, self.ds[0x280011].value
        self.isTextVisible = False
        self.mouse_on_image = False
        self.x_coord, self.y_coord = 0, 0

    def init(self):
        glClearColor(0, 0, 0, 0.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(-self.width, self.width, -self.height, self.height)

    def check_letters(self, cos_1, cos_2, cos_3):
        if cos_1 == 1 and cos_2 == cos_3 == 0:
            return 'L'
        elif cos_1 == cos_3 == 0 and cos_2 == 1:
            return 'A'
        elif cos_1 == cos_2 == 0 and cos_3 == 1:
            return 'H'
        elif cos_1 == 0 and cos_2 > math.cos(45) > cos_3:
            return 'AF'
        elif cos_1 == 0 and cos_2 > math.cos(45) and cos_3 > math.cos(45):
            return 'AH'
        elif cos_1 == 0 and cos_2 < math.cos(45) < cos_3:
            return 'PH'
        elif cos_1 == 0 and cos_2 < math.cos(45) and cos_3 < math.cos(45):
            return 'PF'

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glColor3f(1, 1, 1)

        self.draw_texture()

        self.print_text(self.width - 10, self.height / 2, GLUT_BITMAP_HELVETICA_12, self.letter_X)
        self.print_text(self.width / 2, self.height - 10, GLUT_BITMAP_HELVETICA_12, self.letter_Y)
        if self.isTextVisible == True:
            self.print_text(self.x_coord - self.width + 10, -self.y_coord + self.height, GLUT_BITMAP_HELVETICA_12, "(" + str(self.x_coord - self.width) + "," + str(self.height - self.y_coord) + ")")
            if self.mouse_on_image:
                pixel_coord = self.coord_3D()
                self.print_text(self.x_coord - self.width + 10, -self.y_coord + self.height - 15, GLUT_BITMAP_HELVETICA_12, "(" + str(round(pixel_coord[0], 2)) + "," + str(round(pixel_coord[1], 2)) + "," + str(round(pixel_coord[2], 2)) + ")")

        glutSwapBuffers()

    def print_text(self, x, y, font, line):
        glColor3f(1, 1, 1)
        glPushAttrib(GL_DEPTH_TEST)
        glRasterPos2d(x, y)
        for i in line:
            glutBitmapCharacter(font, ord(i))
        glPopAttrib()

    def draw_texture(self):
        glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, self.width, self.height, 0, GL_LUMINANCE, GL_UNSIGNED_BYTE, self.image_pixels)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glEnable(GL_TEXTURE_2D)

        glBegin(GL_QUADS)
        glTexCoord2d(0.0, 0.0)
        glVertex2d(self.width, self.height)
        glTexCoord2d(1.0, 0.0)
        glVertex2d(0.0, self.height)
        glTexCoord2d(1.0, 1.0)
        glVertex2d(0.0, 0.0)
        glTexCoord2d(0.0, 1.0)
        glVertex2d(self.width, 0.0)
        glEnd()
        glDisable(GL_TEXTURE_2D)

    def motion_func(self, x, y):
        self.isTextVisible = True
        if x > self.width and y < self.height:
            self.mouse_on_image = True
        else:
            self.mouse_on_image = False
        self.x_coord, self.y_coord = x, y
        self.display()

    def coord_3D(self):
        c, r = self.x_coord - self.width, self.height - self.y_coord
        pixel_coord = self.image_position + c * self.X_orientation + r * self.Y_orientation
        return pixel_coord


def reshape(width, height):
    glutInitWindowSize(width, height)
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH) - width) // 2, (glutGet(GLUT_SCREEN_HEIGHT) - height) // 2)


def init_window(width, height):
    glutInitWindowSize(width, height)
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH) - width) // 2, (glutGet(GLUT_SCREEN_HEIGHT) - height) // 2)
    glutCreateWindow('KP_5')
    glutReshapeWindow(width, height)


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    file = Image(path_file)
    init_window(file.width * 2, file.height * 2)
    file.init()
    glutDisplayFunc(file.display)
    glutPassiveMotionFunc(file.motion_func)
    glutMainLoop()


if __name__ == '__main__':
    main()
