from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pydicom

path_file = "DICOM_Image_for_Lab_2.dcm"


class Image:
    def __init__(self, path):
        self.ds = pydicom.read_file(path)
        self.image_pixels = self.ds[0x7fe00010].value
        self.bits = self.ds[0x280100].value
        if self.bits == 8:
            self.data_type = GL_UNSIGNED_BYTE
        self.width, self.height = self.ds[0x280010].value, self.ds[0x280011].value
        self.isTextVisible = False
        self.sd = self.ds[0x081030]
        self.my_attr = self.sd.name + ' - ' + self.sd.value

    def init(self):
        glClearColor(0, 0, 0, 0.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glColor3f(1, 1, 1)
        self.draw_texture(self.image_pixels)
        if self.isTextVisible:
            self.print_text(5, self.height - 15, GLUT_BITMAP_HELVETICA_12, self.my_attr)
        glutSwapBuffers()

    def print_text(self, x, y, font, line):
        glColor3f(1, 1, 1)
        glPushAttrib(GL_DEPTH_TEST)
        glRasterPos2d(x, y)
        for i in line:
            glutBitmapCharacter(font, ord(i))
        glPopAttrib()

    def draw_texture(self, data, data_type=GL_UNSIGNED_BYTE):
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

    def mouse_button(self, button, state, x, y):
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            self.isTextVisible = not self.isTextVisible
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
    glutMouseFunc(file.mouse_button)
    glutMainLoop()


if __name__ == '__main__':
    main()
