import pydicom
from math import cos
from OpenGL.arrays.numpymodule import ARRAY_TO_GL_TYPE_MAPPING
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *


class Image:
    def __init__(self, filename):
        self.image = pydicom.read_file(filename)

    def width(self):
        return self.image['0028', '0011'].value

    def height(self):
        return self.image['0028', '0010'].value

    def image_position(self):
        return self.image['0020', '0032'].value

    def image_orientation(self):
        return self.image['0020', '0037'].value

    def patient_position(self):
        return self.image['0018', '5100'].value

    def pixel_spacing(self):
        try:
            pixelSpacing = image['0028', '0030'].value
        except:
            pixelSpacing = [0.8, 0.8]
        return pixelSpacing

    def pixels(self):
        return self.image.pixel_array

    def patient_orientation(self):
        patient_orientation = self.image['0020', '0020'].value
        return patient_orientation[0], patient_orientation[1]

    def bits_allocated(self):
        bitsPerPixel = self.image['0028', '0100'].value
        return bitsPerPixel


def define_let1(cos1):
    if cos1 == 0:
        return ''
    elif cos1 > cos(45):
        return 'L'
    else:
        return 'R'


def define_let2(cos2):
    if cos2 == 0:
        return ''
    elif cos2 > cos(45):
        return 'A'
    else:
        return 'P'


def define_let3(cos3):
    if cos3 == 0:
        return ''
    elif cos3 > cos(45):
        return 'H'
    else:
        return 'F'


def define_letters(imageOrientationArray):
    x = define_let1(imageOrientationArray[0]) + define_let2(imageOrientationArray[1]) + define_let3(
        imageOrientationArray[2])
    y = define_let1(imageOrientationArray[3]) + define_let2(imageOrientationArray[4]) + define_let3(
        imageOrientationArray[5])
    return x, y


def display():
    global image
    glClear(GL_COLOR_BUFFER_BIT)
    imageOrientationArray = list(map(float, image.image_orientation()))
    x, y = define_letters(imageOrientationArray)
    glBegin(GL_QUADS)
    glTexCoord2d(0.0, 0.0)
    glVertex2d(image.width(), image.height())
    glTexCoord2d(1.0, 0.0)
    glVertex2d(0.0, image.height())
    glTexCoord2d(1.0, 1.0)
    glVertex2d(0.0, 0.0)
    glTexCoord2d(0.0, 1.0)
    glVertex2d(image.width(), 0.0)
    glEnd()
    draw_text('Coronal plane', image.width() / 2 - 35, -10)
    draw_text(x, image.width() - 10, image.height() / 2)
    draw_text(y, image.width() / 2, image.height())
    glFlush()


def reshape(w, h):
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluOrtho2D(- w / 2, w / 2, - h / 2, h / 2)


def init():
    global image
    pixels = image.pixels()
    gl_type = ARRAY_TO_GL_TYPE_MAPPING.get(pixels.dtype)
    glBindTexture(GL_TEXTURE_2D, glGenTextures(1))
    glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, image.width(), image.height(), 0, GL_LUMINANCE, gl_type, pixels)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glEnable(GL_TEXTURE_2D)
    glClearColor(0.0, 0.0, 0.0, 0.0)


def mouse(x, y):
    global image
    display()
    width = glutGet(GLUT_WINDOW_WIDTH)
    height = glutGet(GLUT_WINDOW_HEIGHT)
    x_coord = x - width / 2
    y_coord = height - y - image.width()
    if width / 2 < x < width and 0 < y < height / 2:
        image_orientation = image.image_orientation()
        image_position = image.image_position()
        pixel_spacing = image.pixel_spacing()
        pixel_spacing_x = pixel_spacing[0]
        pixel_spacing_y = pixel_spacing[1]
        x_position = image_position[0] + pixel_spacing_x * image_orientation[0] * x_coord + pixel_spacing_y * \
                     image_orientation[3] * y_coord
        y_position = image_position[1] + pixel_spacing_x * image_orientation[4] * y_coord + pixel_spacing_y * \
                     image_orientation[1] * x_coord
        z_position = image_position[2] + image_orientation[2] * x_coord / image_position[2] + image_orientation[
            5] * y_coord / image_position[2]
        text = "Patient coordinates (mm): [" + str(x_position) + "; " + str(y_position) + "; " + str(z_position) + "]"
        draw_text(text, -width / 2 + 10, -height / 2 + 40)
    if 0 < x < width and 0 < y < height:
        text = "Image coordinates (px): [" + str(x_coord) + "; " + str(y_coord) + "]"
        draw_text(text, -width / 2 + 10, -height / 2 + 20)
    glFlush()


def draw_text(text, x, y):
    glDisable(GL_TEXTURE_2D)
    glColor3f(255, 255, 255)
    glRasterPos2f(x, y)
    for character in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(character))
    glEnable(GL_TEXTURE_2D)


def keyboard(key, x, y):
    if key == chr(27).encode():
        sys.exit(0)


def main(filename):
    global image
    image = Image(filename)
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize(image.width() * 2, image.height() * 2)
    glutInitWindowPosition(100, 100)
    glutCreateWindow('DydykLab5')
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutPassiveMotionFunc(mouse)
    glutMainLoop()


main('changed_dicom.dcm')
