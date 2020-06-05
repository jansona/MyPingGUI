#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
MyPing GUI Version

author: ybg
github: https://github.com/jansona/MyPing 
last edited: May 2020
"""

import sys
import threading
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, 
    QTextEdit, QGridLayout, QApplication, QPushButton, QVBoxLayout)
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QTextCursor
from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal
from MyPing.utils import PingUtil
from MyPing.opts import PingOptions


class EmittingStream(QtCore.QObject):  
        _msg_signal = QtCore.pyqtSignal(str)  #定义一个发送str的信号

        def write(self, text):
            self._msg_signal.emit(str(text))  


class MyPingGUI(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.ping_util = PingUtil()
        self.initUI()

    def __draw_widget(self):

        host_label = QLabel('Host')
        patch_size_label = QLabel('Data size(bytes)')
        ping_num_label = QLabel('Ping times')
        # result_label = QLabel('Result')

        self.host_edit = QLineEdit()
        self.patch_size_edit = QLineEdit()
        self.ping_num_edit = QLineEdit()
        self.result_edit = QTextEdit()

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(host_label, 1, 0)
        grid.addWidget(self.host_edit, 1, 1)

        grid.addWidget(patch_size_label, 2, 0)
        grid.addWidget(self.patch_size_edit, 2, 1)

        grid.addWidget(ping_num_label, 3, 0)
        grid.addWidget(self.ping_num_edit, 3, 1)

        # grid.addWidget(result_label, 4, 0)
        # grid.addWidget(self.result_edit, 4, 0, 6, 1)

        self.send_button = QPushButton('Send')
        
        vbox = QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addWidget(self.result_edit)
        vbox.addWidget(self.send_button)
        
        self.setLayout(vbox)

    def __set_widget_attr(self):

        self.host_edit.setText('www.stanford.edu')
        self.patch_size_edit.setValidator(QIntValidator(self))
        self.patch_size_edit.setText('2052')
        self.ping_num_edit.setValidator(QIntValidator(self))
        self.ping_num_edit.setText('3')
        self.result_edit.setReadOnly(True)
        sys.stdout = EmittingStream(_msg_signal=self.__output_written)
        sys.stderr = EmittingStream(_msg_signal=self.__output_written)  

        self.send_button.clicked.connect(self.__send_packet)

    def __send_packet(self):

        def send_threading_func():
            self.send_button.setEnabled(False)

            opt = PingOptions()
            opt.host = self.host_edit.text()
            opt.packet_size = int(self.patch_size_edit.text())
            opt.ping_times = int(self.ping_num_edit.text())
            
            self.ping_util.ping(opt)

            self.send_button.setEnabled(True)

        t = threading.Thread(target=send_threading_func, name='funciton', daemon=True)
        t.start()

    def __output_written(self, text):  
        cursor = self.result_edit.textCursor()  
        cursor.movePosition(QTextCursor.End)  
        cursor.insertText(text)  
        self.result_edit.setTextCursor(cursor)  
        self.result_edit.ensureCursorVisible()  
        
    def initUI(self):

        self.__draw_widget()
        self.__set_widget_attr()
        
        self.setGeometry(200, 200, 800, 600)
        self.setWindowTitle('My Ping')    
        self.show()
        
        
if __name__ == '__main__':
    
    appctxt = ApplicationContext()
    ex = MyPingGUI()
    exit_code = appctxt.app.exec_() 
    sys.exit(exit_code)