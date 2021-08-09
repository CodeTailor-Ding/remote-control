import ClientTCP
import RemoteGUI

import sys
from queue import Queue
from typing import Tuple
from PySide6.QtWidgets import QApplication

class Control():

    def __init__(self, destination: Tuple) -> None:
        self._recvBuffer = Queue(20)
        self._sendBuffer = Queue(10)
        self._serverScreenSize = (1920, 1080)
        self.__initConnect(destination)
        self.__initWindow()

    def __initConnect(self, args):
        self._tcp = ClientTCP.clientTCP(self, args)

    def __initWindow(self):
        self._mainwindow = RemoteGUI.MainWindow(self)
        self._mainwindow.show()

    def recvTOview(self, recvData):
        self._mainwindow.image_label.display(recvData)

    def clickTOsend(self, args):
        if self._tcp is None:
            return
        self._tcp.sendData(args)

    def setServerScreenSize(self, width, height):
        self._serverScreenSize = (width, height)

    def getServerScreenSize(self):
        return self._serverScreenSize

    def pri(self, data):
        print(data)


def main():
    ServerHost = '192.168.2.112'
    ServerPort = 8020

    app = QApplication()
    Control((ServerHost, ServerPort))
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()