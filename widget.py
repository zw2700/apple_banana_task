import time
from datetime import datetime
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QDialog, QGraphicsOpacityEffect
from PyQt5.QtCore import QTimer, Qt, QObject, QThread, pyqtSignal, QThreadPool, QRunnable
from PyQt5.QtGui import QImage, QPixmap
import pandas as pd
from randompicture import *
import pyfirmata
import serial.tools.list_ports
from PIL import Image

class WorkerSignals(QObject):
    """worker class to enable PyQt multithreading"""
    finished = pyqtSignal()
    choice = pyqtSignal(int)
    '''
    def __init__(self):
        super().__init__()
        
        # initialize Arduino board
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            if "usbmodem" in p.name:
                port = p.device
                
        self.board = pyfirmata.Arduino(port)
        it = pyfirmata.util.Iterator(self.board)
        it.start()
        self.board.digital[2].mode = pyfirmata.INPUT

    def run(self):
        """ detect arduino """
        while True:
            touchbar = self.board.digital[2].read()
            if touchbar is True:
                self.choice.emit(1)
                break
            self.finished.emit()
    '''

class Worker(QRunnable):
    def __init__(self):
        super().__init__()
        
        # initialize Arduino board
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            if "usbmodem" in p.name:
                port = p.device
                
        self.board = pyfirmata.Arduino(port)
        it = pyfirmata.util.Iterator(self.board)
        it.start()
        self.board.digital[2].mode = pyfirmata.INPUT
        
        self.signals = WorkerSignals()
    
    def run(self):
        """ detect arduino """
        while True:
            touchbar = self.board.digital[2].read()
            if touchbar is True:
                self.signals.choice.emit(1)
                break
            self.signals.finished.emit()

class Widget(QWidget):
    """widget class, full content for gui"""
    def __init__(self):
        super(Widget, self).__init__()
        # set background color
        self.setStyleSheet("QWidget{background-color:black}QPushButton{background-color:gray;color:black}")
        # define layout
        self.vlyt = QVBoxLayout(self)
        self.hlyt = QHBoxLayout(self)
        # define pushbutton
        self.btn_pause = QPushButton(self)
        self.btn_save = QPushButton(self)
        self.btn_pause.setFixedSize(100, 35)
        self.btn_save.setFixedSize(100, 35)
        self.btn_pause.hide()  # 不显示按钮
        self.btn_save.hide()   # 不显示按钮

        self.btn_pause.setText("CLICK TO PAUSE")
        self.btn_save.setText("SAVE")

        # define label to show the num
        self.text_lbl = QLabel()
        self.text_lbl.setStyleSheet("background-color:gray;color:yellow;font:25px")
        self.text_lbl.setFixedSize(35, 35)
        self.text_lbl.setAlignment(Qt.AlignCenter)
        self.text_lbl.move(0, 0)
        self.text_lbl.hide()

        # set layout
        self.hlyt.addWidget(self.text_lbl)
        self.hlyt.addStretch()
        self.hlyt.addWidget(self.btn_pause)
        self.hlyt.addWidget(self.btn_save)
        self.vlyt.addLayout(self.hlyt)
        self.vlyt.addStretch()

        self.setLayout(self.vlyt)

        # # define timer to show picture
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.setSingleShot(True)

        # define time to show num
        self.timer_num = QTimer()
        self.count = 0  # calculate time to hide num

        # flag for run
        self.flag = True
        # picture label
        self.lbl = QLabel(self)
        # self.lbl.setFixedSize(200, 200)
        self.lbl.setScaledContents(True)
        
        # initialize image position and size
        self.x = 0
        self.y = 0
        self.lbl_width = 0
        self.lbl_height = 0
        
        # initialize pause timestamp
        self.pausetime = 5
        
        # use opacity effect to create black screen
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(0)
        self.lbl.setGraphicsEffect(self.opacity_effect)

        # current picture content
        self.currContent = ""

        # result list
        self.resLst = []
        
        self.dict = {'apple':1,'banana':2}
        
        # initialize Arduino board
        self.init_arduino()

        # first start flag
        self.firstStart = True

        # signal and slot
        self.btn_pause.clicked.connect(self.slot_pause)
        self.btn_save.clicked.connect(self.slot_save)
        self.timer.timeout.connect(self.slot_timeout)
        self.timer_num.timeout.connect(self.slot_num_timeout)
        
        self.threadpool = QThreadPool()
        
        # start loop
        self.slot_timeout()
        
        # init start
        self.timer_num.start(100)  # 100ms
        
    def init_arduino(self):
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            if "usbmodem" in p.name:
                port = p.device
        
        self.board = pyfirmata.Arduino(port)
        it = pyfirmata.util.Iterator(self.board)
        it.start()

    def slot_pause(self):
        self.flag = not self.flag
        if self.flag:  # start
            self.btn_pause.setText("CLICK TO PAUSE")
            self.pressFlag = True
        else:  # pause
            self.btn_pause.setText("CLICK TO START")
            self.timer.stop()

    def slot_save(self):
        print('save...')
        df = pd.DataFrame(self.resLst, columns=[['answer', 'result', 'takeTime', 'position-X','position-Y','size-width','size-height','originPicture']])
        df.to_csv('./result/{}.txt'.format(datetime.now().strftime('%Y-%m-%d_%H-%M-%S')), index=False)
    
    def slot_timeout(self):
        if self.flag:  # calculate time
            self.board.digital[13].write(0)
            self.showAPicture()
            self.pressTime = time.time()
            self.pressFlag = True
            self.detect_arduino()

    def slot_num_timeout(self):
        if self.count >= 1000:
            if self.text_lbl.isVisible():
                self.text_lbl.hide()
            self.count = 1000
        else:
            self.count += 100

    def keyPressEvent(self, evt):
        """overload key press event"""
        if evt.key() == Qt.Key_P:
            self.count = 0
            if self.text_lbl.isHidden():
                self.text_lbl.show()
            self.text_lbl.setText('P')
            self.slot_pause()
            return
        if evt.key() == Qt.Key_S:
            self.count = 0
            if self.text_lbl.isHidden():
                self.text_lbl.show()
            self.text_lbl.setText('S')
            self.slot_save()
            return

        if not self.pressFlag:
            return

        if not self.flag:
            return
        
        if evt.key() == Qt.Key_1:
            self.count = 0
            if self.text_lbl.isHidden():
                self.text_lbl.show()
            self.text_lbl.setText('1')

            if 'apple' in self.currContent:
                self.resLst.append(['apple', True, time.time()-self.pressTime, self.currContent])
            else:
                self.resLst.append(['apple', False, time.time()-self.pressTime, self.currContent])
            print(self.resLst[-1])
            self.timer.stop()
            self.timer.start()
            self.pressFlag = False

        elif evt.key() == Qt.Key_2:
            self.count = 0
            if self.text_lbl.isHidden():
                self.text_lbl.show()
            self.text_lbl.setText('2')

            if 'banana' in self.currContent:
                self.resLst.append(['banana', True, time.time()-self.pressTime, self.currContent])
            else:
                self.resLst.append(['banana', False, time.time()-self.pressTime, self.currContent])

            print(self.resLst[-1])

            self.timer.stop()
            self.timer.start()
            self.pressFlag = False

    def closeEvent(self, evt):
        self.timer.stop()
        self.slot_save()
        
    def showAPicture(self):
        self.opacity_effect.setEnabled(False)
        self.currContent = get_picture()
        self.lbl.setPixmap(QPixmap(QImage(self.currContent)))
        img = Image.open(self.currContent)
        width,height = img.width, img.height
        self.lbl_width, self.lbl_height = generate_size(width,height)
        self.lbl.resize(self.lbl_width, self.lbl_height)
        self.x, self.y = get_position(self.width(), self.height(), self.lbl_width, self.lbl_height)
        self.lbl.move(self.x, self.y)
    
    def detect_arduino(self):
        
        if not self.pressFlag:
            return

        if not self.flag:
            return
            
        #self.thread = QThread()
        #self.threadpool = QThreadPool()
        #print(QThreadPool.globalInstance().maxThreadCount())
        self.worker = Worker()
        #self.worker.moveToThread(self.thread)
        
        #self.thread.started.connect(self.worker.run)
        #self.worker.signals.finished.connect(self.thread.quit)
        #self.worker.signals.finished.connect(self.worker.deleteLater)
        #self.thread.finished.connect(self.thread.deleteLater)
        self.worker.signals.choice.connect(self.choice_response)
        
        #self.thread.start()
        self.threadpool.start(self.worker)
        
        '''
        while True:
            touchbar = self.board.digital[2].read()
            if touchbar is True:
                self.count = 0
                if self.text_lbl.isHidden():
                    self.text_lbl.show()
                self.text_lbl.setText('1')

                if 'apple' in self.currContent:
                    self.resLst.append(['apple', True, time.time()-self.pressTime, self.currContent])
                else:
                    self.resLst.append(['apple', False, time.time()-self.pressTime, self.currContent])
                print(self.resLst[-1])
                self.timer.stop()
                self.timer.start()
                self.pressFlag = False
        '''
    
    def choice_response(self,choice):
        ''' given a choice of 1 or 2, make corresponding responses'''
        self.count = 0
        if self.text_lbl.isHidden():
            self.text_lbl.show()
        self.text_lbl.setText(str(choice))
        
        temp = ['apple', True, time.time()-self.pressTime, self.x, self.y, self.lbl_width, self.lbl_height,self.currContent]
        
        if 'banana' in self.currContent:
            temp[0] = 'banana'
        
        if self.dict[temp[0]] != choice:
            temp[1] = False
        
        print(temp)
        
        if temp[1]:
            self.board.digital[13].write(1)
            
        self.resLst.append(temp)
        self.opacity_effect.setEnabled(True)
        time.sleep(self.pausetime)
        self.timer.stop()
        self.timer.start()
        self.pressFlag = False
        
class CDialog(QDialog):
    """start gui"""
    def __init__(self):
        super(CDialog, self).__init__()
        self.setFixedSize(300, 200)
        self.setStyleSheet("QWidget{background-color:black}QPushButton{background-color:lightGray;color:blue}")
        self.btn_exit = QPushButton(self)
        self.btn_1 = QPushButton(self)
        self.btn_2 = QPushButton(self)

        self.btn_exit.setFixedSize(50, 30)
        self.btn_1.setFixedSize(100, 30)
        self.btn_2.setFixedSize(180, 30)

        # set text
        self.btn_exit.setText("EXIT")
        self.btn_1.setText('[Space] Start')
        self.btn_2.setText('[S] Start in simulation mode')

        # set position
        self.btn_exit.move(200, 150)
        self.btn_1.move(0, 80)
        self.btn_2.move(110, 80)

        # tip
        self.lbl = QLabel(self)
        self.lbl.setFixedSize(250, 20)
        self.lbl.move(0, 0)
        self.lbl.setText('Press [P] to pause')
        self.lbl.setStyleSheet('color:yellow')

        # signal and slot
        self.btn_exit.clicked.connect(self.reject)
        self.btn_2.clicked.connect(self.accept)

    def keyPressEvent(self, evt):
        if evt.key() == Qt.Key_2 or evt.key() == Qt.Key_S:
            self.accept()
