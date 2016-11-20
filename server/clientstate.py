import threading
import time

MOUSE_UP = 0
MOUSE_DOWN = 1

class ClientState:
  def __init__(self, x, y, s):
    self.lock = threading.Lock()
    self.setState(x, y, s)
    self.lastReceivedPacketTime = 0.0

  def getState(self):
    with self.lock:
      return self.x, self.y, self.s

  def setState(self, x, y, s):
    if x < 0 or x > 640 or y < 0 or y > 480:
      print("ERROR: trying to set out of bounds values for x, y: {}, {}".format(x, y))
      return
    with self.lock:
      self.x, self.y, self.s = x, y, s

  def sendTeamName(self, conn, name):
    toSend = name.encode() + b'\x00'
    print(toSend)
    conn.sendall(toSend)

  def recvTeamName(self, conn):
    receivedNameBytes = b'\x01'
    while receivedNameBytes[-1] != 0:
      receivedNameBytes += conn.recv(1)
    self.teamName = receivedNameBytes[1:len(receivedNameBytes) - 1].decode()
    print("Team name:", self.teamName)

  def send(self, conn):
    conn.sendall(self._encode())

  def recv(self, conn):
    self._decode(self._receivePacket(conn))

  def _receivePacket(self, conn):
    packetSize = 5
    result = bytes(0)
    while len(result) < packetSize:
      result += conn.recv(packetSize - len(result))
    return result

  def _encode(self):
    with self.lock:
      return bytes([self.x >> 8, self.x & 0xff, self.y >> 8, self.y & 0xff, self.s])

  def _decode(self, b):
    with self.lock:
      self.x = int(b[0]) * 256 + int(b[1])
      self.y = int(b[2]) * 256 + int(b[3])
      self.s = int(b[4])
