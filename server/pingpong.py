from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from winner import WINNER_LEFT, WINNER_RIGHT
import drawing
import time

class PingPongPad():
  def __init__(self, x, y):
    self.x, self.y = x, y
    self.HALF_SIZE_X = 15
    self.HALF_SIZE_Y = 60

  def draw(self):
    drawing.rectangle(self.x, self.y, self.HALF_SIZE_X, self.HALF_SIZE_Y, (1, 1, 1))

  def updateY(self, y):
    self.y = y

  def insideBounds(self, x, y):
    return x >= self.x - self.HALF_SIZE_X and \
           x <= self.x + self.HALF_SIZE_X and \
           y >= self.y - self.HALF_SIZE_Y and \
           y <= self.y + self.HALF_SIZE_Y

class PingPongBall():
  def __init__(self, x, y):
    self.x, self.y = x, y
    self.directionX, self.directionY = 0.49, 0.71
    self._initConstants()


  def _initConstants(self):
    self.PING_PONG_BALL_RADIUS = 10
    self.BORDER_SIZE = 5
    self.BALL_SPEED_MULTIPLIER = 15.0
    self.SPEED_INCREASE = 0.5
    self.MAX_BALL_SPEED_MULTIPLIER = 40

  def draw(self):
    if self.out():
      glColor3f(1, 0, 0)
    else:
      glColor3f(1, 1, 1)
    glPushMatrix()
    glTranslate(self.x, 480 - self.y, 0)
    gluDisk(gluNewQuadric(), 0, self.PING_PONG_BALL_RADIUS, 100, 1)
    glPopMatrix()

  def step(self):
    self.x += self.directionX * self.BALL_SPEED_MULTIPLIER
    self.y += self.directionY * self.BALL_SPEED_MULTIPLIER

    if self.BALL_SPEED_MULTIPLIER < self.MAX_BALL_SPEED_MULTIPLIER:
      self.BALL_SPEED_MULTIPLIER += self.SPEED_INCREASE

    if self.y <= self.BORDER_SIZE or self.y >= 480 - self.BORDER_SIZE:
      self.directionY *= -1

  def hitPad(self, pad):
    return abs(self.x - pad.x) < self.PING_PONG_BALL_RADIUS + pad.HALF_SIZE_X and \
           abs(self.y - pad.y) < self.PING_PONG_BALL_RADIUS + pad.HALF_SIZE_Y

  def updateAfterHit(self, pad):
    self.directionX *= -1.0

  def out(self):
    return self.x <= self.BORDER_SIZE or self.x >= 640 - self.BORDER_SIZE


class PingPong:
  def __init__(self, client1, client2):
    self.client1 = client1
    self.client2 = client2
    self.pad1 = PingPongPad(15, 240)
    self.pad2 = PingPongPad(640 - 15, 240)
    self.ball = PingPongBall(320, 240)
    self.lastHitPad = None
    self.gameOver = False
    self.winner = None
    self.drawFirstTime = None
    self.printed = False

  def draw(self):
    self.pad1.draw()
    self.pad2.draw()
    self.ball.draw()
    # self.client1.draw()
    # self.client2.draw()

  def step(self):
    if self.gameOver: return

    self.ball.step()

    if self.lastHitPad is None:
      if self.ball.hitPad(self.pad1):
        self.ball.updateAfterHit(self.pad1)
        self.lastHitPad = self.pad1
      elif self.ball.hitPad(self.pad2):
        self.ball.updateAfterHit(self.pad2)
        self.lastHitPad = self.pad2
    else:
      if self.lastHitPad is self.pad1 and self.ball.hitPad(self.pad2):
        self.ball.updateAfterHit(self.pad2)
        self.lastHitPad = self.pad2
      elif self.lastHitPad is self.pad2 and self.ball.hitPad(self.pad1):
        self.ball.updateAfterHit(self.pad1)
        self.lastHitPad = self.pad1

  def setWhoWon(self):
    self.winner = WINNER_LEFT if self.ball.x >= 320 else WINNER_RIGHT

  def update(self):
    if self.drawFirstTime is None:
      self.drawFirstTime = time.time()
    if self.gameOver and self.printed is False:
      print(time.time() - self.drawFirstTime)
      printed = True
      return
    if self.ball.out():
      self.setWhoWon()
      self.gameOver = True
      return

    _, y1, s1 = self.client1.state.getState()
    # _, y2, s2 = self.client2.state.getState()
    self.pad1.updateY(y1)
    self.pad2.updateY(y1)
