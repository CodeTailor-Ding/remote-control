import cv2
import time
import struct
import numpy as np
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM


class clientTCP():
    def __init__(self, control, args: tuple):
        self.control = control
        self._serverHost = args[0]
        self._serverPort = args[1]
        self._socket = None
        self.__connect()
        self.__initThread()

    def __connect(self):
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._socket.connect((self._serverHost, self._serverPort) )
        msg = self.recvFromBuffer(self._socket, lens=4)
        width, height = struct.unpack('>HH', msg)
        self.control.setServerScreenSize(width=width, height=height)

    def __initThread(self):
        self.recvThread = Thread(target=self.__recvData)
        self.recvThread.start()

    def __recvData(self):
        preimg = np.zeros((1080, 1920, 3), dtype='uint8')
        ''' 此处分辨率为服务端默认传输的分辨率 '''

        while True:
            imglen, imgtype = self.recvFromBuffer(self._socket, head=True)
            recv_msg = self.recvFromBuffer(self._socket, imglen)

            # 解码
            data_decode = np.frombuffer(recv_msg, np.uint8)
            img_decode = cv2.imdecode(data_decode, cv2.IMREAD_UNCHANGED)
            if imgtype == 1:
                img_decode = preimg + img_decode
            preimg = img_decode
            transStyleIm=cv2.cvtColor(img_decode, cv2.COLOR_BGR2RGB)


            # height, width, channel = transStyleIm.shape
            # bytesPerLine = 3 * width
            # qImg = QImage(transStyleIm.data, width, height, bytesPerLine, QImage.Format_RGB888)
            # qpixmap = QPixmap.fromImage(qImg)
            
            self.control.recvTOview(transStyleIm)

    def sendData(self, data):
        stre = struct.pack('>HHB', data[0], data[1], data[2])
        self._socket.send(stre)

    @staticmethod
    def recvFromBuffer(buffer, lens=5, head=False):
        '''
        若head为True，则返回一个元组，其中包含（图像所占字节长度，接受到的图像信息‘
        0：图像为实际截屏图像
        1：图像为差值’，等。。。）
        Note：修改head信息时，需要修改lens的默认值
        '''
        buf = b''
        maxNone = 4
        while lens:
            newbuf = buffer.recv(lens)
            if newbuf is None:
                maxNone -= 1
                if maxNone <=0:
                    return None
                time.sleep(0.5)
                continue
            buf += newbuf
            lens -= len(newbuf)
        if head:
            # imglen, sign = struct.unpack('>Ib', buf[:4], buf[4:])
            # return (imglen, sign)
            return struct.unpack('>IB', buf)
        return buf

    def getSoket(self):
        if self._socket is None:
            self._connect()
        return self._socket
