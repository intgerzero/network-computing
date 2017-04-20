#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import logging
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QWidget, QDialog, QMainWindow, QLabel, QLineEdit, QPushButton,
        QTextEdit, QPlainTextEdit, QGridLayout, QApplication)
from control import Control
from ui_main import Ui_main

log_fmt = '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
date_fmt = '%m-%d %H:%M:%S'
logging.basicConfig(filename='control.log',level=logging.INFO, format=log_fmt, datefmt=date_fmt)

class Ui_login(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.address  = QLabel("地址", self)
        self.port     = QLabel("端口", self)
        self.bankcard = QLabel("银行卡号", self)
        self.password = QLabel("密码", self)
        self.address.setAlignment(QtCore.Qt.AlignCenter)
        self.port.setAlignment(QtCore.Qt.AlignCenter)
        self.bankcard.setAlignment(QtCore.Qt.AlignCenter)
        self.password.setAlignment(QtCore.Qt.AlignCenter)

        self.address.setGeometry(QtCore.QRect(30, 25, 80, 25))
        self.port.setGeometry(QtCore.QRect(30, 75, 80, 25))
        self.bankcard.setGeometry(QtCore.QRect(30, 125, 80, 25))
        self.password.setGeometry(QtCore.QRect(30, 185, 80, 25))

        self.addressEdit  = QLineEdit(self)
        self.portEdit     = QLineEdit(self)
        self.bankcardEdit = QLineEdit(self)
        self.passwordEdit = QLineEdit(self)
        self.passwordEdit.setEchoMode(QLineEdit.Password)

        self.okButton = QPushButton("登录", self)
        self.cancelButton = QPushButton("取消", self)

        self.addressEdit.setGeometry(QtCore.QRect(140, 15, 220, 40))
        self.portEdit.setGeometry(QtCore.QRect(140, 65, 220, 40))
        self.bankcardEdit.setGeometry(QtCore.QRect(140, 115, 220, 40))
        self.passwordEdit.setGeometry(QtCore.QRect(140, 175, 220, 40))
        
        self.okButton.setGeometry(QtCore.QRect(240, 230, 110, 35))
        self.cancelButton.setGeometry(QtCore.QRect(60, 230, 110, 35))

        self.okButton.clicked.connect(self.mainWindow)
        self.cancelButton.clicked.connect(self.close)

        self.resize(400, 300)
        self.setWindowTitle("登录")
        self.show()

    def mainWindow(self):
        config = {
                'address':  self.addressEdit.text(),
                'port':     self.portEdit.text(),
                'bankcard': self.bankcardEdit.text(),
                'password': self.passwordEdit.text()
        }
        
        # 输入检查
        flag = True
        for key in config.keys():
            if config[key] == "":
                flag = False
                self.statusBar().showMessage("Please input the {}.".format(key))
                break
            if key == 'port':
                try:
                    config[key] = int(config[key])
                except Exception as e:
                    self.statusBar().showMessage("Please input the right number at port")
                    break

        if flag:
            self.control = Control(**config)
            reply = self.control.login()
            self.statusBar().showMessage('{}'.format(reply['msg']))
            logging.debug("reply: {}".format(str(reply)))

            if reply['status'] == True: # login sucessfully
                self.close()
                self.main = Ui_main(self.control)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    uiLogin = Ui_login()
    sys.exit(app.exec_())
