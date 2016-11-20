from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

def rectangle(centerX, centerY, halfWidth, halfHeight, c):
  glColor3f(c[0], c[1], c[2])
  glPushMatrix()
  glTranslate(centerX, 480 - centerY, 0)
  glBegin(GL_POLYGON)
  glVertex3f(-halfWidth, +halfHeight, 0)
  glVertex3f(+halfWidth, +halfHeight, 0)
  glVertex3f(+halfWidth, -halfHeight, 0)
  glVertex3f(-halfWidth, -halfHeight, 0)
  glEnd()
  glPopMatrix()
