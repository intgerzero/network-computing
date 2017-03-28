# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/me/git/network-computing/Client/login.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from Ui_main import Ui_Login

class Ui_Login(object):
    def setupUi(self, Login):
        Login.setObjectName("Login")
        Login.resize(400, 300)
        Login.setSizeGripEnabled(True)
        self.bankcardText = QtWidgets.QPlainTextEdit(Login)
        self.bankcardText.setGeometry(QtCore.QRect(140, 60, 221, 41))
        self.bankcardText.setPlainText("")
        self.bankcardText.setObjectName("bankcardText")
        self.passwdText = QtWidgets.QPlainTextEdit(Login)
        self.passwdText.setGeometry(QtCore.QRect(140, 150, 221, 41))
        self.passwdText.setPlainText("")
        self.passwdText.setObjectName("passwdText")
        self.bankcard = QtWidgets.QLabel(Login)
        self.bankcard.setGeometry(QtCore.QRect(30, 70, 81, 25))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.bankcard.setFont(font)
        self.bankcard.setObjectName("bankcard")
        self.password = QtWidgets.QLabel(Login)
        self.password.setGeometry(QtCore.QRect(40, 160, 71, 25))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.password.setFont(font)
        self.password.setTextFormat(QtCore.Qt.AutoText)
        self.password.setScaledContents(False)
        self.password.setAlignment(QtCore.Qt.AlignCenter)
        self.password.setObjectName("password")
        self.pushButton = QtWidgets.QPushButton(Login)
        self.pushButton.setGeometry(QtCore.QRect(240, 220, 107, 35))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(Login)
        self.pushButton_2.setGeometry(QtCore.QRect(70, 220, 107, 35))
        self.pushButton_2.setObjectName("pushButton_2")

        self.retranslateUi(Login)
        self.pushButton_2.clicked.connect(Login.close)
        self.pushButton.clicked.connect(Login.update)
        QtCore.QMetaObject.connectSlotsByName(Login)

    def retranslateUi(self, Login):
        _translate = QtCore.QCoreApplication.translate
        Login.setWindowTitle(_translate("Login", "登录"))
        self.bankcard.setText(_translate("Login", "银行卡号"))
        self.password.setText(_translate("Login", "密码"))
        self.pushButton.setText(_translate("Login", "登录"))
        self.pushButton_2.setText(_translate("Login", "取消"))

    @pyqtSlot()
    def on_pushButton_clocked(self):
        self.accept()
        dlg = Ui_Login()
        dlg.show()
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Login = QtWidgets.QDialog()
    ui = Ui_Login()
    ui.setupUi(Login)
    Login.show()
    sys.exit(app.exec_())

