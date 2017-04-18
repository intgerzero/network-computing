#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
reference:
http://blog.sina.com.cn/s/blog_9b78c91101019o93.html
"""

import sys
import time
from control import Control
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (QApplication, QDialog, QSizePolicy,
        QMainWindow, QPushButton, QGridLayout, QVBoxLayout,
        QLabel, QLineEdit, QDialogButtonBox, QSpacerItem)

class Dialog(QDialog):
    
    def __init__(self, flag, parent=None):
        self.flag = flag
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.resize(240, 200)
        
        grid = QGridLayout()
        
        self.amountLabel = QLabel("金额", self)
        self.amountEdit  = QLineEdit(self)
        grid.addWidget(self.amountLabel, 0, 0, 1, 1)
        grid.addWidget(self.amountEdit, 0, 1, 1, 1)

        if self.flag == 'transfer':
            self.transferedLabel = QLabel("转入账户", self)
            self.transferedEdit = QLineEdit(self)
            grid.addWidget(self.transferedLabel, 1, 0, 1, 1)
            grid.addWidget(self.transferedEdit, 1, 1, 1, 1)

        buttonBox = QDialogButtonBox(self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(grid)

        spacerItem = QSpacerItem(20, 48, QSizePolicy.Minimum,
                QSizePolicy.Expanding)
        layout.addItem(spacerItem)

        layout.addWidget(buttonBox)

        self.setLayout(layout)

    def amount(self):
        return self.amountEdit.text()

    def transfered(self):
        return self.transferedEdit.text()

class Ui_main(QMainWindow):

    def __init__(self, control):
        self.control = control
        self.listPrint = list()
        super().__init__()
        self.initUI()

    def initUI(self):
        self.depositButton  = QPushButton("存款", self)
        self.withdrawButton = QPushButton("取款", self)
        self.transferButton = QPushButton("转账", self)
        self.printoutButton = QPushButton("打印清单", self)

        self.depositButton.setGeometry(40, 70, 110, 35)
        self.withdrawButton.setGeometry(250, 70, 110, 35)
        self.transferButton.setGeometry(40, 140, 110, 35)
        self.printoutButton.setGeometry(250, 140, 110, 35)

        self.depositButton.clicked.connect(self.deposit)
        self.withdrawButton.clicked.connect(self.withdraw)
        self.transferButton.clicked.connect(self.transfer)
        self.printoutButton.clicked.connect(self.printout)

        self.resize(400, 300)
        self.setWindowTitle("业务")
        self.show()

    def deposit(self):
        result = {'timestamp': time.asctime(), 'type': 'deposit'}
        dialog = Dialog('deposit', self)
        if dialog.exec_():
            amount = dialog.amount()
            try:
                amount = float(amount)
                if amount < 0:
                    self.statusBar().showMessage("请输入正数")
                else:
                    result['amount'] = amount
                    self.statusBar().showMessage("正在处理...")
                    resp = self.control.deposit(amount)
                    
                    print(resp)
                    if resp[0] == True:
                        result['result'] = 'success'
                        self.statusBar().showMessage("deposit {:.2f} sucessfully.".format(amount))
                    else:
                        result['result'] = 'fail'
                        self.statusBar().showMessage("deposit {:.2f} failed. Reason: {}".format(amount, resp[1]))
                    self.listPrint.append(result)
            except ValueError:
                self.statusBar().showMessage("请输入有效正数")
            except Exception as e:
                self.statusBar().showMessage(str(e))

        dialog.destroy()

    def withdraw(self):
        result = {'timestamp': time.asctime(), 'type': 'withdraw'}
        dialog = Dialog('withdraw',self)
        if dialog.exec_():
            amount = dialog.amount()
            result['amount'] = amount
            self.statusBar().showMessage("正在处理...")
            print(amount)
            result['result'] = '0' # 结果

        dialog.destroy()
        self.listPrint.append(result)

    def transfer(self):
        result = {'timestamp': time.asctime(), 'type': 'deposit'}
        dialog = Dialog('transfer',self)
        if dialog.exec_():
            amount = dialog.amount()
            transfered = dialog.transfered()
            result['amount'] = amount
            result['transfered'] = transfered
            self.statusBar().showMessage("正在处理...")
            print(amount, transfered)

        dialog.destroy()
        self.listPrint.add(result)

    def printout(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    uiMain = Ui_main()
    sys.exit(app.exec_())
