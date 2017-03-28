# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/me/git/network-computing/Client/status.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Status(object):
    def setupUi(self, Status):
        Status.setObjectName("Status")
        Status.resize(400, 300)
        Status.setSizeGripEnabled(True)
        self.textBrowser = QtWidgets.QTextBrowser(Status)
        self.textBrowser.setGeometry(QtCore.QRect(70, 20, 256, 192))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.textBrowser.setFont(font)
        self.textBrowser.setObjectName("textBrowser")
        self.pushButton = QtWidgets.QPushButton(Status)
        self.pushButton.setGeometry(QtCore.QRect(140, 240, 107, 35))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(Status)
        self.pushButton.clicked.connect(Status.close)
        QtCore.QMetaObject.connectSlotsByName(Status)

    def retranslateUi(self, Status):
        _translate = QtCore.QCoreApplication.translate
        Status.setWindowTitle(_translate("Status", "状态"))
        self.pushButton.setText(_translate("Status", "确定"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Status = QtWidgets.QDialog()
    ui = Ui_Status()
    ui.setupUi(Status)
    Status.show()
    sys.exit(app.exec_())

