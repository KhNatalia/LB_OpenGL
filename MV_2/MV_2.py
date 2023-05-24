import math

from OpenGL.GL import *
from OpenGL.GLUT import *
from tkinter import *

from OpenGL.raw.GLU import gluOrtho2D

name = 'KP_2'


def display():
    glColor3d(1, 0, 0)
    glLineWidth(1)
    glClear(GL_COLOR_BUFFER_BIT)
    glBegin(GL_LINES)
    glVertex2f(0, 240)
    glVertex2f(640, 240)
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(320, 480)
    glVertex2f(320, 0)
    glEnd()

    glBegin(GL_POINTS)
    glColor3d(1, 0, 0)

    # визначаємо сторону зсуву
    sign_x = 1 if x2 > x1 else -1 if x2 < x1 else 0
    sign_y = 1 if y2 > y1 else -1 if y2 < y1 else 0

    dx = math.fabs(x2 - x1)
    dy = math.fabs(y2 - y1)

    # визначаємо нахил відрізку
    # ex відповідає за протяжність по координаті x
    # ey відповідає за протяжність по координаті y
    if dx > dy:
        pdx, pdy = sign_x, 0
        ex, ey = dy, dx
    else:
        pdx, pdy = 0, sign_y
        ex, ey = dx, dy

    x, y = x1, y1

    err, t = ey / 2, 0

    while t < ey:
        glVertex2i(x, y)
        err -= ex
        if err < 0:
            err += ey
            x += sign_x
            y += sign_y
        else:
            x += pdx
            y += pdy
        t += 1
    glEnd()
    glFlush()

    glutSwapBuffers()
    glutPostRedisplay()
    return


def cartesian_to_cylindrical(x, y):
    ro = math.sqrt(x**2 + y**2)
    fi = math.degrees(math.atan(y / x))

    return ro, fi


def main():
    glutInit(sys.argv)

    glutInitWindowSize(640, 480)
    glutInitWindowPosition(50, 50)
    glutCreateWindow(name)
    glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGB)

    glClearColor(0, 0, 0, 0)
    glColor3f(0, 0, 0)
    glPointSize(1)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, 640, 0, 480)

    global x1, x2, y1, y2
    print("Введіть координати відрізка у діапазоні від -100 до 100")
    x1 = int(input('x1: ')) + 320
    y1 = int(input('y1: ')) + 240
    x2 = int(input('x2: ')) + 320
    y2 = int(input('y2: ')) + 240
    glutDisplayFunc(display)
    ro1, fi1 = cartesian_to_cylindrical(x1, y1)
    ro2, fi2 = cartesian_to_cylindrical(x2, y2)
    print("Початкова точка у циліндричній системі: ro = %.2f" % ro1, "fi = %.2f" % fi1, "градусів")
    print("Кінцева точка у циліндричній системі: ro = %.2f" % ro2, "fi = %.2f" % fi2, "градусів")
    glutMainLoop()
    return


if __name__ == '__main__':
    main()
