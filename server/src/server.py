import cv2
import time
import queue
import struct
import pyautogui
import threading
import numpy as np
from win32.win32api import GetSystemMetrics
from socket import socket, AF_INET, SOCK_STREAM

IMGBUFFER = queue.Queue(40)
T_FIG = True

def sendmsg(session, addr):

    global T_FIG, IMGBUFFER
    MAXRESET = 3
    imageSize = (1920, 1080)
    quality = 100
    encode_param_jpg = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    count = 1
    preimg = np.zeros((imageSize[1], imageSize[0], 3), dtype='uint8')
    ts = time.time()
    offsetTimes = MAXRESET
    while T_FIG:
        primeIm = pyautogui.screenshot()
        # 转为opencv的BGR格式
        transStyleIm=cv2.cvtColor(np.asarray(primeIm), cv2.COLOR_RGB2BGR)
        # 改变图像大小
        transSizeIm = cv2.resize(transStyleIm, imageSize)
        # 将原始图像编码
        img_encode = cv2.imencode(".jpg", transSizeIm, encode_param_jpg)[1]

        offset = transSizeIm - preimg
        if offsetTimes > 0 and (offset==0).all():
            offsetTimes -= 1
            continue

        preimg = transSizeIm
        off_encode = cv2.imencode(".jpg", offset, encode_param_jpg)[1]
        # 转为数组形式
        str_total = np.asarray(img_encode).tostring()
        str_offset = np.asarray(off_encode).tostring()

        try:
            # 向客户端发送图像信息
            if offsetTimes > 0 and len(str_offset) < len(str_total):
                print('发送{}--{}----{}FPS'.format(count, 1, count/(time.time()-ts)))
                # session.send(struct.pack('>IB', len(str_offset), int(1)))
                # session.send(str_offset)
                IMGBUFFER.put_nowait(struct.pack('>IB', len(str_offset), int(1)))
                IMGBUFFER.put_nowait(str_offset)
                offsetTimes -= 1
            else:
                print('发送{}--{}----{}FPS'.format(count, 0, count/(time.time()-ts)))
                # session.send(struct.pack('>IB', len(str_total), int(0)))
                # session.send(str_total)
                IMGBUFFER.put_nowait(struct.pack('>IB', len(str_total), int(0)))
                IMGBUFFER.put_nowait(str_total)
                offsetTimes = MAXRESET
            count += 1
        except ConnectionResetError as cre:
            print('[{}]'.format(time.strftime('%Y-%m-%d %H:%M:%S')), cre)
            break
        except queue.Full as ful:
            print(ful)
            break


def sendFromBUffer(session, addr):
    global T_FIG, IMGBUFFER
    while True:
        msg = IMGBUFFER.get()
        try:
            session.send(msg)
        except ConnectionResetError as cre:
            print(cre)
            break
    T_FIG = False


def recvmsg(session, addr):
    global T_FIG
    def recvFromBuffer(buffer, lens=5):
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
        return buf

    while T_FIG:
        try:
            comanddata = recvFromBuffer(session)
            _x, _y, _c = struct.unpack('>HHB', comanddata)
            if _c == 0:
                butt = 'left'
            elif _c == 1:
                butt = 'right'
            pyautogui.click(_x, _y, button=butt)
        except ConnectionResetError as cre:
            break


def _TCPToWait():

    global T_FIG, IMGBUFFER
    localhost = ''
    localport = 8020

    socket_server = socket(AF_INET, SOCK_STREAM)
    socket_server.bind((localhost, localport))
    socket_server.listen(1)

    while True:
        BASESIZE = (GetSystemMetrics(0), GetSystemMetrics(1))
        print('The server is ready to receive...')
        connectionSocket, addr = socket_server.accept()
        print('[{}] {}连接到服务器。'.format(time.strftime('%Y-%m-%d %H:%M:%S'), addr))

        # 发送本机分辨率信息（用于在控制端发送控制信息时，确定控制信息的坐标）
        msg = struct.pack('>HH', BASESIZE[0], BASESIZE[1])
        connectionSocket.send(msg)

        sendt = threading.Thread(target=sendmsg, args=(connectionSocket, addr))
        sendFBt = threading.Thread(target=sendFromBUffer, args=(connectionSocket, addr))
        recvt = threading.Thread(target=recvmsg, args=(connectionSocket, addr))
        
        sendt.start()
        sendFBt.start()
        recvt.start()
        sendt.join()
        sendFBt.join()
        recvt.join()

        connectionSocket.close()
        T_FIG = True
        while not IMGBUFFER.empty():
            t = IMGBUFFER.get()


if __name__ == '__main__':
    _TCPToWait()
