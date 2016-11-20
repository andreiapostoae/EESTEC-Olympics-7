from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import time
from winner import WINNER_LEFT, WINNER_RIGHT, WINNER_NOBODY

class SafeArea:
  def __init__(self, x, y, halfSquareSize):
    self.x, self.y = x, y
    self.halfSquareSize = halfSquareSize

  def draw(self):
    glColor3f(1, 1, 1)
    glPushMatrix()
    glTranslate(self.x, 480 - self.y, 0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(-self.halfSquareSize, -self.halfSquareSize, 0)
    glVertex2f(+self.halfSquareSize, -self.halfSquareSize, 0)
    glVertex2f(+self.halfSquareSize, +self.halfSquareSize, 0)
    glVertex2f(-self.halfSquareSize, +self.halfSquareSize, 0)
    glEnd()
    glPopMatrix()

  def inBounds(self, disk):
    return abs(self.x - disk.x) <= self.halfSquareSize and \
           abs(self.y - disk.y) <= self.halfSquareSize

  def getZSpot(self, zeroCount):
    line = zeroCount // 3
    col = zeroCount % 3
    x = self.x - self.halfSquareSize + (self.halfSquareSize / 2 * (col + 1))
    y = self.y - self.halfSquareSize + (self.halfSquareSize / 2 * (line + 1))
    return x, y

class Disk:
  def __init__(self, x, y, maxRadius):
    self.x, self.y = x, y
    self.radius = 0
    self.claimed = False
    self.maxRadius = maxRadius
    self.RADIUS_STEP = 5
    self.colorRGB = (1, 1, 1)
    self.draggable = True
    self.performStep = True

  def inBounds(self, x, y):
    return abs(self.x - x) <= self.radius and abs(self.y - y) <= self.radius

  def draw(self):
    glColor3f(self.colorRGB[0], self.colorRGB[1], self.colorRGB[2])
    glPushMatrix()
    glTranslate(self.x, 480 - self.y, 0)
    gluDisk(gluNewQuadric(), 0, self.radius, 100, 1)
    glPopMatrix()

  def step(self):
    if not self.performStep: return
    if self.radius < self.maxRadius:
      self.radius += self.RADIUS_STEP

  def moveTo(self, x, y):
    self.x, self.y = x, y

  def setClaimed(self):
    self.draggable = False
    self.claimed = True

  def finalMoveToSafe(self, x, y, r, colorR, colorG, colorB):
    self.performStep = False
    self.x, self.y, self.radius = x, y, r
    self.colorRGB = (colorR, colorG, colorB)

class ClickTheDisks:
  def __init__(self, client1, client2):
    self.client1 = client1
    self.client2 = client2
    self.gameOver = False
    self.winner = None

    # Specific to this game.
    self.disks = []
    self.firstDrawTime = None
    self.MAX_TIME = 20

    self.addInitialDisks()

    SAFE_AREA_HALF_LEN = 40
    SAFE_AREA_PADDING = 20
    self.safeAreaLeft = SafeArea(
        SAFE_AREA_PADDING + SAFE_AREA_HALF_LEN,
        SAFE_AREA_PADDING + SAFE_AREA_HALF_LEN,
        SAFE_AREA_HALF_LEN)
    self.safeAreaRight = SafeArea(
        640 - (SAFE_AREA_PADDING + SAFE_AREA_HALF_LEN),
        480 - (SAFE_AREA_PADDING + SAFE_AREA_HALF_LEN),
        SAFE_AREA_HALF_LEN)

    self.pointsLeft = 0
    self.pointsRight = 0

  def addInitialDisks(self):
    centerX, centerY = 320, 240
    DISK_RADIUS = 25
    DISK_SPACING = 15
    for i in [-1, 0, 1]:
      for j in [-1, 0, 1]:
        self.disks.append(Disk(centerX + i * (2 * DISK_RADIUS + DISK_SPACING),
                               centerY + j * (2 * DISK_RADIUS + DISK_SPACING),
                               DISK_RADIUS))

  def setWhoWon(self):
    if self.pointsLeft > self.pointsRight: self.winner = WINNER_LEFT
    elif self.pointsLeft < self.pointsRight: self.winner = WINNER_RIGHT
    else: self.winner = WINNER_NOBODY

  def getObjectAt(self, x, y):
    for disk in self.disks:
      if disk.draggable and disk.inBounds(x, y):
        return disk
    return None

  def draw(self):
    if self.firstDrawTime is None:
      self.firstDrawTime = time.time()
    else:
      if self.pointsLeft + self.pointsRight == 9:
        self.gameOver = True;
        print(time.time() - self.firstDrawTime)
        self.setWhoWon()
      else:
        if time.time() - self.firstDrawTime >= self.MAX_TIME:
          self.setWhoWon()
          self.gameOver = True

    self.safeAreaLeft.draw()
    self.safeAreaRight.draw()
    for disk in self.disks:
      if disk.claimed:
        disk.draw()
    for disk in self.disks:
      if not disk.claimed:
        disk.draw()
    self.client1.draw()
    # self.client2.draw()

  def step(self):
    for disk in self.disks:
      disk.step()

  def update(self):
    self.client1.update()
    # self.client2.update()

    for disk in self.disks:
      if not disk.draggable: continue
      if self.safeAreaLeft.inBounds(disk):
        disk.setClaimed()
        safeX, safeY = self.safeAreaLeft.getZSpot(self.pointsLeft)
        disk.finalMoveToSafe(safeX, safeY, 7, 1, 0, 0)
        self.pointsLeft += 1
      elif self.safeAreaRight.inBounds(disk):
        disk.setClaimed()
        safeX, safeY = self.safeAreaRight.getZSpot(self.pointsRight)
        disk.finalMoveToSafe(safeX, safeY, 7, 0, 1, 0)
        self.pointsRight += 1

