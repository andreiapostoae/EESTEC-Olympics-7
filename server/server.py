#!/usr/bin/env python3.4
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
import time
import threading
import socket
from clientstate import ClientState, MOUSE_UP, MOUSE_DOWN
from annimations import CountdownAnimation, DisplayWinners
from winner import WINNER_LEFT, WINNER_NOBODY, WINNER_RIGHT
from pingpong import PingPong
from clickthedisks import ClickTheDisks
from followthecircle import FollowTheCircle

SOCKET_SERVER_HOST = "localhost"
SOCKET_SERVER_PORT = 10000

class ClientDragData:
  def __init__(self, game, client):
    self.game = game
    self.client = client
    self.prevMouseState = MOUSE_UP
    self.obj = None

  def startDragging(self, x, y):
    self.obj = self.game.getObjectAt(x, y)
    if self.obj is not None:
      self.obj.draggable = False

  def endDragging(self):
    if self.obj is not None:
      self.obj.draggable = True
    self.obj = None

  def update(self):
    x, y, s = self.client.state.getState()

    if self.obj is None and self.prevMouseState == MOUSE_UP and s == MOUSE_DOWN:
      self.startDragging(x, y)
    elif s == MOUSE_UP:
      self.endDragging()
    self.prevMouseState = s

    if self.obj is not None:
      self.obj.moveTo(x, y)

class Client(threading.Thread):
  def __init__(self, shape, socketServer, state):
    super(Client, self).__init__()
    print("Waiting for client...")
    conn, addr = socketServer.accept()
    print("Client connected: {}".format(addr))
    self.conn = conn
    self.state = state
    self.shape = shape
    self.clientDragData = None

  def setClientDragData(self, clientDragData):
    self.clientDragData = clientDragData

  def run(self):
    self.state.recvTeamName(self.conn)
    while True:
      self.state.recv(self.conn)

  def _drawCircle(self):
    CIRCLE_RADIUS = 10
    gluDisk(gluNewQuadric(), 0, CIRCLE_RADIUS, 100, 1)

  def _drawSquare(self):
    HALF_SQUARE_SIZE = 10
    glBegin(GL_POLYGON)
    glVertex3f(-HALF_SQUARE_SIZE, -HALF_SQUARE_SIZE, 0)
    glVertex3f(+HALF_SQUARE_SIZE, -HALF_SQUARE_SIZE, 0)
    glVertex3f(+HALF_SQUARE_SIZE, +HALF_SQUARE_SIZE, 0)
    glVertex3f(-HALF_SQUARE_SIZE, +HALF_SQUARE_SIZE, 0)
    glEnd()

  def draw(self):
    x, y, s = self.state.getState()
    if s == MOUSE_UP:
      glColor3f(1, 1, 1)
    else:
      glColor3f(1, 0, 0)
    glPushMatrix()
    glTranslate(x, 480 - y, 0)
    if self.shape == 'circle':
      self._drawCircle()
    else:
      self._drawSquare()
    glPopMatrix()

  def update(self):
    if self.clientDragData is not None:
      self.clientDragData.update()

class GameServer:
  def __init__(self):
    self.game = None
    self.annimation = None

  def initServer(self):
    self.socketServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socketServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.socketServer.bind((SOCKET_SERVER_HOST, SOCKET_SERVER_PORT))
    self.socketServer.listen(1)

  def waitForClients(self):
    self.client1 = Client('square', self.socketServer, ClientState(0, 0, MOUSE_UP))
    self.client1.start()
    self.client2 = None

  def startGUI(self):
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(640, 480)
    glutCreateWindow(b"Game Server")
    glutReshapeFunc(self.reshape)
    glutMainLoop()

  def reshape(self, w, h):
    glutDisplayFunc(lambda: self.display(w, h))
    glutPostRedisplay();

  def display(self, w, h):
    time.sleep(0.04)
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, 640, 0, 480, -1, 1)

    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    if self.annimation is not None:
      if self.annimation.done:
        self.annimation = None
      else:
        self.annimation.draw()
    else:
      if self.game is not None:
        self.game.update()
        self.game.step()
        self.game.draw()

    glutSwapBuffers()
    glutPostRedisplay();

  def play(self, gameClass):
    self.annimation = None
    self.game = gameClass(self.client1, self.client2)
    self.client1.setClientDragData(ClientDragData(self.game, self.client1))
    # self.client2.setClientDragData(ClientDragData(self.game, self.client2))

  def playAnnimation(self, annimationObj):
    self.game = None
    self.annimation = annimationObj

class GameSequencer(threading.Thread):
  def __init__(self, gameServer):
    super(GameSequencer, self).__init__()
    self.gameServer = gameServer

  def waitForAnnimationToComplete(self):
    while self.gameServer.annimation is not None:
      time.sleep(0.1)

  def waitForGameOver(self):
    while not self.gameServer.game.gameOver:
      time.sleep(0.5)

  def run(self):
    sequence = [
        PingPong, ClickTheDisks, FollowTheCircle,
        PingPong, ClickTheDisks, FollowTheCircle,
        PingPong, ClickTheDisks, FollowTheCircle,
        #ClickTheDisks, ClickTheDisks, ClickTheDisks, ClickTheDisks, ClickTheDisks, ClickTheDisks, ClickTheDisks
        #PingPong, PingPong, PingPong, PingPong, PingPong, PingPong, PingPong, PingPong, PingPong, PingPong
    ]
    for gameClass in sequence:
      self.gameServer.playAnnimation(CountdownAnimation())
      self.waitForAnnimationToComplete()

      self.gameServer.play(gameClass)
      self.waitForGameOver()

      assert self.gameServer.game.winner is not None
      self.gameServer.playAnnimation(DisplayWinners(self.gameServer.game.winner))
      self.waitForAnnimationToComplete()

def main():
  gameServer = GameServer()
  gameServer.initServer()
  gameServer.waitForClients()
  gameSequencer = GameSequencer(gameServer)
  gameSequencer.start()
  gameServer.startGUI()

if __name__ == '__main__':
  main()
