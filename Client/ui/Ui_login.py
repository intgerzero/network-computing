# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/me/git/network-computing/Client/login.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Login(object):
    def setupUi(self, Login):
        Login.setObjectName("Login")
        Login.resize(400, 300)
        Login.setSizeGripEnabled(True)
        self.bankcardText = QtWidgets.QPlainTextEdit(Login)
        self.bankcardText.setGeometry(QtCore.QRect(140, 110, 221, 41))
        self.bankcardText.setPlainText("")
        self.bankcardText.setObjectName("bankcardText")
        self.passwdText = QtWidgets.QPlainTextEdit(Login)
        self.passwdText.setGeometry(QtCore.QRect(140, 170, 221, 41))
        self.passwdText.setPlainText("")
        self.passwdText.setObjectName("passwdText")
        self.bankcard = QtWidgets.QLabel(Login)
        self.bankcard.setGeometry(QtCore.QRect(30, 120, 81, 25))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.bankcard.setFont(font)
        self.bankcard.setObjectName("bankcard")
        self.password = QtWidgets.QLabel(Login)
        self.password.setGeometry(QtCore.QRect(40, 180, 71, 25))
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
        self.pushButton.setGeometry(QtCore.QRect(240, 240, 107, 35))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(Login)
        self.pushButton_2.setGeometry(QtCore.QRect(60, 240, 107, 35))
        self.pushButton_2.setObjectName("pushButton_2")
        self.bankcardText_2 = QtWidgets.QPlainTextEdit(Login)
        self.bankcardText_2.setGeometry(QtCore.QRect(140, 60, 221, 41))
        self.bankcardText_2.setPlainText("")
        self.bankcardText_2.setObjectName("bankcardText_2")
        self.bankcardText_3 = QtWidgets.QPlainTextEdit(Login)
        self.bankcardText_3.setGeometry(QtCore.QRect(140, 10, 221, 41))
        self.bankcardText_3.setPlainText("")
        self.bankcardText_3.setObjectName("bankcardText_3")
        self.bankcard_2 = QtWidgets.QLabel(Login)
        self.bankcard_2.setGeometry(QtCore.QRect(30, 20, 81, 25))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.bankcard_2.setFont(font)
        self.bankcard_2.setObjectName("bankcard_2")
        self.bankcard_3 = QtWidgets.QLabel(Login)
        self.bankcard_3.setGeometry(QtCore.QRect(40, 70, 81, 25))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.bankcard_3.setFont(font)
        self.bankcard_3.setObjectName("bankcard_3")

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
        self.bankcard_2.setText(_translate("Login", "银行卡号"))
        self.bankcard_3.setText(_translate("Login", "银行卡号"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Login = QtWidgets.QDialog()
    ui = Ui_Login()
    ui.setupUi(Login)
    Login.show()
    sys.exit(app.exec_())

