import cv2
import time

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout


class DisplayLabel(QLabel):
    
    def __init__(self, parent, control):
        super(DisplayLabel, self).__init__(parent)
        self._control = control
        self.serverSize = self._control.getServerScreenSize()
        # self.resize(QSize(1920, 1080))
        # self.setAutoFillBackground(True)
        self.setMinimumSize(QSize(800, 600))
        self.setAlignment(Qt.AlignCenter)

    def display(self, imgdata):
        transSizeIm = cv2.resize(imgdata, (self.size().width(), self.size().height()))

        height, width, channel = transSizeIm.shape
        bytesPerLine = 3 * width
        qImg = QImage(transSizeIm.data, width, height, bytesPerLine, QImage.Format_RGB888)
        qpixmap = QPixmap.fromImage(qImg)
        
        self.setPixmap(qpixmap)

    def mousePressEvent(self, QMouseEvent):
        time.sleep(0.01)
        screenX = self.size().width()
        screenY = self.size().height()
        mouseX = int(QMouseEvent.x() * self.serverSize[0] / screenX)
        mouseY = int(QMouseEvent.y() * self.serverSize[1] / screenY)
        if QMouseEvent.buttons() == Qt.LeftButton:
            self._control.clickTOsend((mouseX, mouseY, 0))
        elif QMouseEvent.buttons() == Qt.RightButton:
            self._control.clickTOsend((mouseX, mouseY, 1))


class MainWindow(QWidget):

    def __init__(self, control):
        super(MainWindow, self).__init__()
        self.WINDOWSIZE = QSize(1920, 1080)
        self.image_label = DisplayLabel(self, control)
        self.__initWindow()

    def __initWindow(self):
        self.resize(self.WINDOWSIZE)

        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.image_label)
        self.setLayout(self.main_layout)

    #键盘监听事件，当按下ctrl+Z的组合是，关闭窗口
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Z and event.modifiers() == Qt.ControlModifier:
            self.close()

