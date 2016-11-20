from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import time
import math
from winner import WINNER_LEFT, WINNER_RIGHT, WINNER_NOBODY

class ThisCircle:
  def __init__(self, x, y, radius):
    self.x, self.y, self.radius = x, y, radius
    self.snailRadius = 0
    self.snailAlpha = 0
    self.initialX, self.initialY = x, y
    self.ALPHA_STEP = 0.1
    self.RADIUS_STEP = 0.2

  def draw(self):
    glColor3f(1, 1, 1)
    glPushMatrix()
    glTranslate(self.x, 480 - self.y, 0)
    gluDisk(gluNewQuadric(), self.radius - 1, self.radius, 100, 1)
    glPopMatrix()

  def step(self):
    self.x = self.initialX + self.snailRadius * math.sin(self.snailAlpha)
    self.y = self.initialY + self.snailRadius * math.cos(self.snailAlpha)
    self.snailAlpha += self.ALPHA_STEP
    self.snailRadius += self.RADIUS_STEP

  def inBounds(self, st):
    dx = self.x - st[0]
    dy = self.y - st[1]
    return dx * dx + dy * dy <= self.radius * self.radius

class FollowTheCircle:
  def __init__(self, client1, client2):
    self.client1 = client1
    self.client2 = client2
    self.gameOver = False
    self.winner = None

    self.firstStep = time.time()
    self.STILL_TIME = 5
    self.MAX_TIME = 30

    self.circleLeft = ThisCircle(160, 240, 50)
    self.circleRight = ThisCircle(480, 240, 50)

  def draw(self):
    self.circleLeft.draw()
    self.circleRight.draw()
    self.client1.draw()
    # self.client2.draw()

  def step(self):
    if time.time() - self.firstStep > self.STILL_TIME:
      self.circleLeft.step()
      self.circleRight.step()

  def update(self):
    currentTime = time.time()
    if currentTime - self.firstStep > self.MAX_TIME:
      self.winner = WINNER_NOBODY
      self.gameOver = True
    if currentTime - self.firstStep > self.STILL_TIME:
      if not self.circleLeft.inBounds(self.client1.state.getState()):
        self.winner = WINNER_RIGHT
        self.gameOver = True
      # elif not self.circleRight.inBounds(self.client2.state.getState()):
      #   self.winner = WINNER_LEFT
      #   self.gameOver = True
