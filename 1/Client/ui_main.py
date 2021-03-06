#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
reference:
http://blog.sina.com.cn/s/blog_9b78c91101019o93.html
"""

import sys
import time
import logging
from control import Control
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (QApplication, QDialog, QSizePolicy,
        QMainWindow, QPushButton, QGridLayout, QVBoxLayout,
        QLabel, QLineEdit, QDialogButtonBox, QSpacerItem, QMessageBox, QTextEdit)

log_fmt = '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
date_fmt = '%m-%d %H:%M:%S'
logging.basicConfig(filename='route.log',level=logging.INFO, format=log_fmt, datefmt=date_fmt)


class Dialog(QDialog):
    
    def __init__(self, flag, parent=None):
        self.flag = flag
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.resize(240, 200)
        self.setWindowTitle("")
        
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

    def transferred(self):
        return self.transferedEdit.text()

class Print_dialog(QDialog):

    def __init__(self, results):
        """
        results is tuple or list
        """
        self.results = results
        super().__init__()
        self.initUI()

    def initUI(self):
        self.resize(400, 300)
        self.setWindowTitle("交易清单")

        self.setSizeGripEnabled(True)
        self.logOutput = QTextEdit(self)
        self.logOutput.setReadOnly(True)
        #self.logOutput.setLineWrapMode(QTextEdit.NoWrap)
        self.logOutput.setGeometry(QtCore.QRect(10, 10, 380, 280))
        
        text = ""
        for result in self.results:
            for key in result.keys():
                text += "{}: {}\n".format(key, result[key])
            text += '\n'
        if text == "":
            text = "no trade histroy"
        self.logOutput.insertPlainText(text)

        self.show()


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
        self.printoutButton.clicked.connect(self.printout_all)

        self.resize(400, 300)
        self.setWindowTitle("业务")
        self.show()

    def deposit(self):
        result = {'timestamp': time.asctime(), 'type': 'deposit'}
        self._operation('deposit', result)

    def withdraw(self):
        result = {'timestamp': time.asctime(), 'type': 'withdraw'}
        self._operation('withdraw', result)

    def transfer(self):
        result = {'timestamp': time.asctime(), 'type': 'transfer'}
        self._operation('transfer', result)

    def _operation(self, type, result):
        dialog = Dialog(type, self)
        if dialog.exec_():
            amount = dialog.amount()
            # 输入检查, 留空
            try:
                amount = float(amount)
                if amount <= 0: # positive number
                    self.statusBar().showMessage("请输入正数")
                else:
                    result['amount'] = amount
                    self.statusBar().showMessage("正在处理...")
                    if type == 'deposit':
                        reply = self.control.deposit(amount)
                    elif type == 'withdraw':
                        reply = self.control.withdraw(amount)
                    elif type == 'transfer':
                        transferred = dialog.transferred()
                        result['transferred'] = transferred
                        reply = self.control.transfer(amount, transferred)
                    else:
                        self.statusBar().showMessage("error, unknow work type")
                        return

                    logging.debug("reply from control: {}".format(str(reply)))
                    if reply.get("status") != None and reply.get('sequence') == None: # TEST_POINT 导致的 bug 修正
                        if reply['status'] == True:
                            result['result'] = 'success'
                            self.statusBar().showMessage("{} {:.2f} sucessfully.".format(type, amount))
                        else:
                            result['result'] = 'fail'
                            self.statusBar().showMessage("{} {:.2f} failed. Reason: {}".format(type, amount, reply['msg']))
                    else:
                        result['result'] = 'fail'
                        self.statusBar().showMessage("{} {:.2f} failed. Unknow reason.".format(type, amount))
            except ValueError:
                result = '-1'
                result['result'] = 'fail'
                self.statusBar().showMessage("请输入有效正数")
            except Exception as e:
                result['result'] = 'fail'
                self.statusBar().showMessage(str(e))
            finally:
                printout = self.printout((result,))
                self.listPrint.append(result)

        dialog.destroy()

    def printout_all(self):
        self.print_dialog = Print_dialog(self.listPrint)

    def printout(self, results):
        reply = QMessageBox.question(self, '消息', '打印交易清单?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self.print_dialog = Print_dialog(results)
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    uiMain = Ui_main()
    sys.exit(app.exec_())
