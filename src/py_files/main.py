import os
import sys
import tkinter as tk

import cv2
import matplotlib
import numpy as np
import pandas as pd
import qimage2ndarray
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

matplotlib.use("Qt5Agg")
import asyncio
import re
import threading
import time

from matplotlib.animation import TimedAnimation
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from PyQt5 import QtCore

import src.py_files.irib as irib
import src.py_files.outfile as of

start = time.time()
start = 0
globalfinish = 0
mylst_index = 0




class WorkerThread(QThread):
    finished = pyqtSignal(int)
    force_quit = pyqtSignal(int)
    my_url = ''

    def url_get(self, my_url):
        self.my_url = my_url

    def run(self):
        #url = 'http://127.0.0.1:8080/play/index.m3u8'
        #url = irib.geturl()
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        cmds = (['ffmpeg.exe -y -fflags +genpts -f hls -i "{}" -f h264 -'.format(self.my_url)], ['ldecod.exe -d decoder.cfg'])
        self.execute(*self.runners(cmds))
        #self.onfinish()
        self.finished.emit(0)

    def onfinish(self):
        print("finished")
        dir_name = "/Users/shima/PycharmProjects/VQM"
        test = os.listdir(dir_name)

        for item in test:
            if item.endswith(".264"):
                os.remove(os.path.join(dir_name, item))
            if item.endswith(".yuv"):
                os.remove(os.path.join(dir_name, item))

    def proc_jm(self, line):
        lst = line.decode("utf-8").rstrip().split(',')
        if lst[0].startswith('*'):
            a = 0
        elif len(lst) == 2:
            of.width = int(lst[0])
            of.height = int(lst[1])
        else:
            of.lst_nn = lst
            of.lst_nn.append(of.width)
            of.lst_nn.append(of.height)
            y = self.read_model(of.lst_nn)
            of.lst_prediction.append(y)

    def proc_ffmpeg(self, line):
        res = []
        pointer = 0
        for i in re.finditer(b'\x00\x00\x00\x01', line):
            res.append(i.start())
        if len(res) == 0:
            of.buffer.extend(line)
        elif len(res) == 1:
            if res[0] != 0:
                of.buffer.extend(line[:res[0]])
                pointer = res[0]
                of.batch_size, of.file1, of.count = of.file_write(of.batch_size, of.file1, of.count, of.buffer)
                of.buffer.clear()
            else:
                of.batch_size, of.file1, of.count = of.file_write(of.batch_size, of.file1, of.count, of.buffer)
                of.buffer.clear()
                pointer = 0
            of.buffer.extend(line[pointer:])
        else:
            if res[0] != 0:
                of.buffer.extend(line[:res[0]])
                pointer = res[0]
                of.batch_size, of.file1, of.count = of.file_write(of.batch_size, of.file1, of.count, of.buffer)
                of.buffer.clear()
            else:
                of.batch_size, of.file1, of.count = of.file_write(of.batch_size, of.file1, of.count, of.buffer)
                of.buffer.clear()
                pointer = 0
            for i in range(len(res) - 1):
                of.buffer.extend(line[pointer:res[i + 1]])
                pointer = res[i + 1]
                of.batch_size, of.file1, of.count = of.file_write(of.batch_size, of.file1, of.count, of.buffer)
                of.buffer.clear()
            of.buffer.extend(line[pointer:])

    async def _read_stream(self, stream, cb):
        while True:
            line = await stream.readline()
            if line:
                cb(line)
            else:
                break

    async def _stream_subprocess(self, cmd, stdout_cb, stderr_cb, lb):
        try:
            process = await asyncio.create_subprocess_shell(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            await asyncio.wait(
                [
                    self._read_stream(process.stdout, stdout_cb),
                    self._read_stream(process.stderr, stderr_cb),
                ]
            )
            rc = await process.wait()
            if lb == '0':
                of.file1.write(of.buffer)
                file = open("end.txt", "wt")
                file.write("s")
                file.close()

            return process.pid, rc
        except OSError as e:
            # the program will hang if we let any exception propagate
            return e

    def execute(self, *aws):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        #loop = asyncio.get_event_loop()
        rc = loop.run_until_complete(asyncio.gather(*aws))
        loop.close()
        return rc

    def printer(self, label):
        def pr(*args, **kw):
            if label == '0.stdout':
                self.proc_ffmpeg(*args)
            if label == '1.stdout':
                self.proc_jm(*args)
            if label == '1.stderr':
                print(*args)

        return pr

    def name_it(self, start=0, template="{}"):
        while True:
            yield template.format(start)
            start += 1

    def runners(self, cmds):
        next_name = self.name_it().__next__
        for cmd in cmds:
            name = next_name()
            out = self.printer(f"{name}.stdout")
            err = self.printer(f"{name}.stderr")
            yield self._stream_subprocess(cmd, out, err, "{}".format(name))

    def read_model(self, rowData):
        nlst = []
        nlst.append(rowData)
        dfS = pd.DataFrame(nlst)
        X_test = of.loaded_cs.transform(dfS)
        return float(of.loaded_model.predict(X_test) * 100)


class CustomMainWindow(QMainWindow):
    def __init__(self):
        super(CustomMainWindow, self).__init__()

        # Define the geometry of the main window
        self.setFixedSize(1000, 450)
        self.setGeometry(300, 300, 800, 400)
        self.setWindowTitle("VQM")
        # Create FRAME_A
        self.FRAME_A = QFrame(self)
        self.FRAME_A.setStyleSheet("QWidget { background-color: %s }" % QColor(210,210,235,255).name())
        self.LAYOUT_A = QGridLayout()
        self.FRAME_A.setLayout(self.LAYOUT_A)
        self.setCentralWidget(self.FRAME_A)

        # add frame B
        self.FRAME_B = QFrame(self)
        self.FRAME_B.setStyleSheet("QWidget { background-color: %s }" % QColor(210,210,220,255).name())
        self.LAYOUT_B = QGridLayout()
        self.FRAME_B.setLayout(self.LAYOUT_B)
        self.LAYOUT_A.addWidget(self.FRAME_B, *(0, 0))
        # Place the zoom button
        self.zoomBtn = QPushButton(text='load')
        self.zoomBtn.setFixedSize(50, 25)
        self.zoomBtn.clicked.connect(self.zoomBtnAction)
        self.LAYOUT_B.addWidget(self.zoomBtn, *(2, 0))
        # Place the stop button
        self.stopBtn = QPushButton(text='stop')
        self.stopBtn.setFixedSize(50, 25)
        self.stopBtn.clicked.connect(self.stopBtnAction)
        self.LAYOUT_B.addWidget(self.stopBtn, *(2, 1))
        #place radio_irib
        self.radio_irib = QRadioButton("irib")
        self.LAYOUT_B.addWidget(self.radio_irib, *(3,0))
        # place lbl_frameRate
        self.lbl_frameRate = QLabel("")
        self.lbl_frameRate.setFixedSize(50, 25)
        self.LAYOUT_B.addWidget(self.lbl_frameRate, *(3, 1))
        # add textbox
        self.txt_width = QLineEdit()
        self.txt_width.setFixedSize(300, 25)
        self.LAYOUT_B.addWidget(self.txt_width, *(1, 0))
        #place lbl_video
        self.lbl_video = QLabel("")
        self.LAYOUT_B.addWidget(self.lbl_video, *(0, 0))
        self.lbl_video.setFixedSize(352, 288)


        # Place the matplotlib figure
        self.myFig = CustomFigCanvas()
        self.LAYOUT_A.addWidget(self.myFig, *(0,1))
        self.myFig.setFixedSize(600, 400)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.display_frame)
        self.worker = WorkerThread()
        self.worker.finished.connect(self.onfinish)
        self.show()
        return

    def zoomBtnAction(self):
        self.zoomBtn.setStyleSheet("QPushButton: { background-color: red }")
        root = tk.Tk()
        root.withdraw()
        if self.radio_irib.isChecked():
            print("irib selected")
            url = irib.geturl()
            self.worker.url_get(url)
            self.worker.start()
        else:
            print("local host selected")
            url = self.txt_width.text()
            self.worker.url_get(url)
            self.worker.start()

        self.timer.start(35)

        return

    def addData_callbackFunc(self, value, data):
        self.myFig.addData(value)
        self.lbl_video.setPixmap(data)
        QCoreApplication.processEvents()

        return

    def read_YUV420(self, reader, rows, cols):
        Y_buf = reader.read(cols * rows)
        gray = np.reshape(np.frombuffer(Y_buf, dtype=np.uint8), [rows, cols])
        U_buf = reader.read(cols // 2 * rows // 2)
        img_U = np.reshape(np.frombuffer(U_buf, dtype=np.uint8), [rows // 2, cols // 2])
        V_buf = reader.read(cols // 2 * rows // 2)
        img_V = np.reshape(np.frombuffer(V_buf, dtype=np.uint8), [rows // 2, cols // 2])
        enlarge_U = cv2.resize(img_U, (0, 0), fx=2.0, fy=2.0)
        enlarge_V = cv2.resize(img_V, (0, 0), fx=2.0, fy=2.0)
        img_YUV = cv2.merge([gray, enlarge_U, enlarge_V])
        dst = cv2.cvtColor(img_YUV, cv2.COLOR_YUV2RGB)
        return dst

    def display_frame(self):
        global mylst_index
        global globalfinish
        if len(of.lst_prediction) == 0:
            print("No data is generated yet!")
        else:
            if len(of.lst_prediction) > mylst_index:

                data = of.lst_prediction[mylst_index]
                self.myFig.addData(data)

                reader = open("out" + str(mylst_index).zfill(4) + ".yuv", 'rb')
                image = self.read_YUV420(reader, of.height, of.width)
                reader.close()
                yourQImage = qimage2ndarray.array2qimage(image)
                pixmap = QPixmap(yourQImage)
                img = pixmap.scaled(352, 288)
                self.lbl_video.setPixmap(img)
                mylst_index += 1
                t1 = time.time()
                global start
                self.lbl_frameRate.setText(str(1/(t1 - start)))
                start = t1
                #print("showing data")
            elif len(of.lst_prediction) < mylst_index and globalfinish == 1:
                self.onfinishJob()
                self.timer.stop()
            else:
                print("Wait, list is not filled")

    def onfinish(self):
        print("finished")
        global globalfinish
        globalfinish = 1

    def onfinishJob(self):
        dir_name = "/Users/shima/PycharmProjects/VQM"
        test = os.listdir(dir_name)
        for item in test:
            if item.endswith(".264"):
                try:
                    os.remove(os.path.join(dir_name, item))
                    print("removed")
                except:
                    print("can't remove the file")
            if item.endswith(".yuv"):
                try:
                    os.remove(os.path.join(dir_name, item))
                    print("removed")
                except:
                    print("can't remove the file")
        try:
            os.remove("end.txt")
        except:
            print("can't remove end.txt")

    def stopBtnAction(self):
        self.worker.exit()
        self.timer.stop()
        self.onfinishJob()
        sys.exit()


class CustomFigCanvas(FigureCanvas, TimedAnimation):
    def __init__(self):
        self.addedData = []
        # The data
        self.xlim = 300
        self.n = np.linspace(0, self.xlim - 1, self.xlim)
        self.y = (self.n * 0.0) + 50
        # The window
        self.fig = Figure(figsize=(5,5), dpi=100)
        self.ax1 = self.fig.add_subplot(111)
        # self.ax1 settings
        self.ax1.set_xlabel('frames')
        self.ax1.set_ylabel('quality')
        self.line1 = Line2D([], [], color='blue')
        self.line1_tail = Line2D([], [], color='red', linewidth=2)
        self.line1_head = Line2D([], [], color='red', marker='o', markeredgecolor='r')
        self.ax1.add_line(self.line1)
        self.ax1.add_line(self.line1_tail)
        self.ax1.add_line(self.line1_head)
        self.ax1.set_xlim(0, self.xlim - 1)
        self.ax1.set_ylim(0, 100)
        FigureCanvas.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval = 50, blit = True)
        return

    def new_frame_seq(self):
        return iter(range(self.n.size))

    def _init_draw(self):
        lines = [self.line1, self.line1_tail, self.line1_head]
        for l in lines:
            l.set_data([], [])
        return

    def addData(self, value):
        self.addedData.append(value)
        return

    def _step(self, *args):
        # Extends the _step() method for the TimedAnimation class.
        try:
            TimedAnimation._step(self, *args)
        except Exception as e:
            self.abc += 1
            print(str(self.abc))
            TimedAnimation._stop(self)
            pass
        return

    def _draw_frame(self, framedata):
        margin = 2
        while len(self.addedData) > 0:
            self.y = np.roll(self.y, -1)
            self.y[-1] = self.addedData[0]
            del(self.addedData[0])

        self.line1.set_data(self.n[0: self.n.size - margin ], self.y[0: self.n.size - margin ])
        self.line1_tail.set_data(np.append(self.n[-10:-1 - margin], self.n[-1 - margin]), np.append(self.y[-10:-1 - margin], self.y[-1 - margin]))
        self.line1_head.set_data(self.n[-1 - margin], self.y[-1 - margin])
        self._drawn_artists = [self.line1, self.line1_tail, self.line1_head]
        return


class Communicate(QObject):
    data_signal = pyqtSignal(float, object)


if __name__== '__main__':
    app = QApplication(sys.argv)

    QApplication.setStyle(QStyleFactory.create("Fusion"))
    myGUI = CustomMainWindow()
    sys.exit(app.exec_())
