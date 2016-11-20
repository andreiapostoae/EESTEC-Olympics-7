#!/usr/bin/env python3.4

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from clientstate import ClientState, MOUSE_UP, MOUSE_DOWN
import socket
import threading
import time

HOST = "0.0.0.0"
PORT = 10000
SERVER_STATE_UPDATE_FREQUENCY_SECONDS = 0.01

class Client(threading.Thread):
  def __init__(self):
    global HOST, PORT
    super(Client, self).__init__()
    self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.conn.connect((HOST, PORT))
    self.state = ClientState(0, 0, MOUSE_UP)

  def run(self):
    global SERVER_STATE_UPDATE_FREQUENCY_SECONDS
    self.state.sendTeamName(self.conn, "test-client")
    while True:
      time.sleep(SERVER_STATE_UPDATE_FREQUENCY_SECONDS)
      self.state.send(self.conn)

class GtkGUI:
  def destroy(self, widget, data=None):
    Gtk.main_quit()

  def motion_cb(self, widget, event):
    self.client.state.setState(int(event.x),
                               int(event.y),
                               MOUSE_DOWN if (event.state & Gdk.ModifierType.BUTTON1_MASK) else MOUSE_UP)

  def __init__(self):
    self.client = Client()
    self.client.start()

    self.window = Gtk.Window()
    self.window.connect("destroy", self.destroy)
    self.window.set_border_width(0)
    self.window.resize(640, 480)

    self.area = Gtk.DrawingArea()
    self.area.connect("motion-notify-event", self.motion_cb)
    self.area.set_events(Gdk.EventMask.POINTER_MOTION_MASK |
                         Gdk.EventMask.BUTTON_PRESS_MASK)
    self.window.add(self.area)
    self.area.show()
    self.window.show()

  def main(self):
    Gtk.main()

if __name__ == "__main__":
  GtkGUI().main()
