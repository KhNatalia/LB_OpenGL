from OpenGL.GL import *
from OpenGL.GLUT import *
import pydicom
import numpy as np

path_dir = "Lab#7"


class Image:
    def __init__(self, path):
        self.num = len([file_name for file_name in os.listdir(path) if os.path.isfile(os.path.join(path, file_name))])

        self.width, self.height = 256, 256
        self.image_pixels = np.zeros((self.num, self.height, self.width))
        self.front = np.zeros((self.height, self.num + 12, self.width))
        self.side = np.zeros((self.width, self.num + 12, self.height))

        self.image_pixels = []

        for file_name in os.listdir(path):
            self.ds = pydicom.read_file('Lab#7/' + file_name)
            self.image_pixels.append(self.normalization_func(self.ds.pixel_array, 0, 255))

        for i in range(self.height):
            for j in range(self.num):
                for n in range(self.width):
                    self.front[i][j][n] = self.image_pixels[j][i][n]

        for i in range(self.width):
            for j in range(self.num):
                for n in range(self.height):
                    self.side[i][j][n] = self.image_pixels[j][n][i]

        self.t, self.t_front, self.t_side = 0, 0, 0

    def init(self):
        glClearColor(0, 0, 0, 0.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-1, 1, -1, 1, -1, 1)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_MODELVIEW)
        glRotatef(-60, 1, 0, 0)
        glRotatef(45, 0, 0, 1)

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        self.draw_coordinates()
        self.draw_texture(self.t, self.t_front, self.t_side)

        glutSwapBuffers()

    # малює координатну площину
    def draw_coordinates(self):
        glColor3f(1, 0, 1)
        glBegin(GL_LINES)
        glVertex3f(-2.0, 0.0, 0.0)
        glVertex3f(2.0, 0.0, 0.0)
        glVertex3f(0.0, -2.0, 0.0)
        glVertex3f(0.0, 2.0, 0.0)
        glVertex3f(0.0, 0.0, -2.0)
        glVertex3f(0.0, 0.0, 2.0)
        glEnd()
        self.print_text(1.2, 0, 0, GLUT_BITMAP_HELVETICA_12, "x")
        self.print_text(0, 1.2, 0, GLUT_BITMAP_HELVETICA_12, "y")
        self.print_text(0, 0, 0.9, GLUT_BITMAP_HELVETICA_12, "z")

    # малює три площини зображення
    def draw_texture(self, t, t_front, t_side):#data, internal_format, type_transform):
        self.default(self.image_pixels[t], self.height, self.width)
        # основна(нижня)
        glEnable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex3f(0, 0, t * 4 / self.height)
        glTexCoord2f(1, 0)
        glVertex3f(1, 0, t * 4 / self.height)
        glTexCoord2f(1, 1)
        glVertex3f(1, 1, t * 4 / self.height)
        glTexCoord2f(0, 1)
        glVertex3f(0, 1, t * 4 / self.height)
        glEnd()

        self.default(self.side[t_front], self.height, 32)
        # передня
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex3f(t_front / self.height, 0, 0)
        glTexCoord2f(1, 0)
        glVertex3f(t_front / self.height, 1, 0)
        glTexCoord2f(1, self.num / 32)
        glVertex3f(t_front / self.height, 1, self.num * 4 / self.height)
        glTexCoord2f(0, self.num / 32)
        glVertex3f(t_front / self.height, 0, self.num * 4 / self.height)
        glEnd()

        self.default(self.front[t_side], self.width, 32)
        # бокова
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex3f(0, t_side / self.height, 0)
        glTexCoord2f(1, 0)
        glVertex3f(1, t_side / self.height, 0)
        glTexCoord2f(1, self.num / 32)
        glVertex3f(1, t_side / self.height, self.num * 4 / self.height)
        glTexCoord2f(0, self.num / 32)
        glVertex3f(0, t_side / self.height, self.num * 4 / self.height)
        glEnd()

        glDisable(GL_TEXTURE_2D)
        glFlush()

    def default(self, data, height, width):
        glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, height, width, 0, GL_LUMINANCE, GL_UNSIGNED_BYTE, data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)

    def print_text(self, x, y, z, font, line):
        glColor3f(1, 1, 1)
        glPushAttrib(GL_DEPTH_TEST)
        glRasterPos3f(x, y, z)
        for i in line:
            glutBitmapCharacter(font, ord(i))
        glPopAttrib()

    # функція виконує нормальзацію
    def normalization_func(self, pixels, p_min, p_max):
        min_pixel = np.min(pixels)
        max_pixel = np.max(pixels)
        normalization = (pixels - min_pixel) / (max_pixel - min_pixel) * (p_max - p_min) + p_min
        return normalization.astype(int)

    # матриця перетворення для віддзеркалення відносно осі zOx
    @staticmethod
    def get_transform_matrix():
        matrix = np.array([
            1, 0, 0, 0,
            0, -1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1,
        ])

        return matrix

    def keyboard_func(self, my_key, x, y):
        key = unicode(my_key, errors='ignore')
        if key == "t":                                      # виконує віддзеркалення
            transform_matrix = self.get_transform_matrix()
            glMultMatrixf(transform_matrix)
        elif key == "w" and self.t < self.num - 1:          # підіймає основну площину
            self.t += 1
        elif key == "s" and self.t > 0:                     # опускає основну площину
            self.t -= 1
        elif key == "d" and self.t_front < self.width - 1:  # рухає в назад передню площину
            self.t_front += 1
        elif key == "a" and self.t_front > 0:               # рухає вперед передню площину
            self.t_front -= 1
        elif key == "," and self.t_side < self.height - 1:  # рухає вправо бокову площину
            self.t_side += 1
        elif key == "." and self.t_side > 0:                # рухає вліво бокову площину
            self.t_side -= 1
        self.display()

def init_window(width, height):
    glutInitWindowSize(width, height)
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH) - width) // 2, (glutGet(GLUT_SCREEN_HEIGHT) - height) // 2)
    glutCreateWindow('KP_7')


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    file = Image(path_dir)
    init_window(file.width * 2, file.height * 2)
    file.init()
    glutDisplayFunc(file.display)
    glutKeyboardFunc(file.keyboard_func)
    glutMainLoop()


if __name__ == '__main__':
    main()
