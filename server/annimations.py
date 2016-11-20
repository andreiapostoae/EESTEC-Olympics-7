from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import time
from winner import WINNER_LEFT, WINNER_NOBODY, WINNER_RIGHT
import drawing

class CountdownAnimation:
  def __init__(self):
    self.counter = 3
    self.firstDrawTimeOfCurrentValue = None
    self.done = False

  def draw(self):
    if self.firstDrawTimeOfCurrentValue is None:
      self.firstDrawTimeOfCurrentValue = time.time()
    else:
      currentTime = time.time()
      if currentTime - self.firstDrawTimeOfCurrentValue >= 1:
        self.counter -= 1
        self.firstDrawTimeOfCurrentValue = currentTime
        if self.counter == 0:
          self.done = True
          return
    glColor3f(1, 1, 1)
    glPushMatrix()
    glTranslate(310, 220, 0)
    glutStrokeCharacter(GLUT_STROKE_ROMAN, ord('0') + self.counter)
    glPopMatrix()

class DisplayWinners:
  def __init__(self, winner):
    self.animationStartTime = None
    self.winner = winner
    self.done = False
    self.annimationLengthSeconds = 1

    self.HALF_LINE_THICKNESS = 20
    self.HALF_LINE_LENGTH = 80
    self.HALF_EQUAL_PADDING = 40
    self.RED = (1, 0, 0)
    self.GREEN = (0, 1, 0)
    self.BLUE = (0, 0, 1)

  def _drawLeft(self):
    if self.winner == WINNER_LEFT:
      drawing.rectangle(160, 240, self.HALF_LINE_THICKNESS, self.HALF_LINE_LENGTH, self.GREEN)
      drawing.rectangle(160, 240, self.HALF_LINE_LENGTH, self.HALF_LINE_THICKNESS, self.GREEN)
    elif self.winner == WINNER_RIGHT:
      drawing.rectangle(160, 240, self.HALF_LINE_LENGTH, self.HALF_LINE_THICKNESS, self.RED)

  def _drawRight(self):
    if self.winner == WINNER_RIGHT:
      drawing.rectangle(480, 240, self.HALF_LINE_THICKNESS, self.HALF_LINE_LENGTH, self.GREEN)
      drawing.rectangle(480, 240, self.HALF_LINE_LENGTH, self.HALF_LINE_THICKNESS, self.GREEN)
    elif self.winner == WINNER_LEFT:
      drawing.rectangle(480, 240, self.HALF_LINE_LENGTH, self.HALF_LINE_THICKNESS, self.RED)

  def _drawCenter(self):
    if self.winner == WINNER_NOBODY:
      drawing.rectangle(320, 240 - self.HALF_EQUAL_PADDING,
          self.HALF_LINE_LENGTH, self.HALF_LINE_THICKNESS, self.BLUE)
      drawing.rectangle(320, 240 + self.HALF_EQUAL_PADDING,
          self.HALF_LINE_LENGTH, self.HALF_LINE_THICKNESS, self.BLUE)

  def draw(self):
    if self.animationStartTime is None:
      self.animationStartTime = time.time()
    else:
      if time.time() - self.animationStartTime >= self.annimationLengthSeconds:
        self.done = True
        return
      self._drawLeft()
      self._drawRight()
      self._drawCenter()
