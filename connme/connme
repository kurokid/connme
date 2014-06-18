#!/usr/bin/env python2

import sip
sip.setapi('QString', 2)
from PyQt4 import QtGui, QtCore, QtNetwork
from connmeMain import connme
import sys,os

class SingleApplicationWithMessaging(QtGui.QApplication):

    messageAvailable = QtCore.pyqtSignal(object)

    def __init__(self, argv, key):
        QtGui.QApplication.__init__(self, argv)
        self._key = key
        self._memory = QtCore.QSharedMemory(self)
        self._memory.setKey(self._key)
        if self._memory.attach():
            self._running = True
        else:
            self._running = False
            if not self._memory.create(1):
                raise RuntimeError(self._memory.errorString())
        self._timeout = 1000
        self._server = QtNetwork.QLocalServer(self)
        if not self.isRunning():
            self._server.newConnection.connect(self.handleMessage)
            self._server.listen(self._key)

    def handleMessage(self):
        socket = self._server.nextPendingConnection()
        if socket.waitForReadyRead(self._timeout):
            self.messageAvailable.emit(
                socket.readAll().data().decode('utf-8'))
            socket.disconnectFromServer()
        else:
            QtCore.qDebug(socket.errorString())

    def isRunning(self):
        return self._running

    def sendMessage(self, message):
        if self.isRunning():
            socket = QtNetwork.QLocalSocket(self)
            socket.connectToServer(self._key, QtCore.QIODevice.WriteOnly)
            if not socket.waitForConnected(self._timeout):
                print(socket.errorString())
                return False
            if not isinstance(message, bytes):
                message = message.encode('utf-8')
            socket.write(message)
            if not socket.waitForBytesWritten(self._timeout):
                print(socket.errorString())
                return False
            socket.disconnectFromServer()
            return True
        return False

def main():
    key = 'connme'
    app = SingleApplicationWithMessaging(sys.argv, key)
    if app.isRunning():
        app.sendMessage(' '.join(sys.argv[1:]))
        sys.exit(1)

    gui = connme()
    gui.address = os.path.realpath(__file__)
    app.messageAvailable.connect(gui.processClient)
    gui.showGui()
    sys.exit(app.exec_())

if __name__ == '__main__':
    euid = os.geteuid()
    os.chdir(sys.path[0])
    if euid != 0:
        if os.path.exists("/usr/bin/gksu"):
            args = ['gksu', sys.executable] + sys.argv + [os.environ]
            os.execlpe('gksu', *args)
        elif os.path.exists("/usr/bin/kdesudo"):
            args = ['kdesudo', sys.executable] + sys.argv + [os.environ]
            os.execlpe('kdesudo', *args)
    main()