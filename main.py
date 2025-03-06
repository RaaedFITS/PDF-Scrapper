from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(428, 330)
        
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setEnabled(True)
        self.label.setGeometry(QtCore.QRect(120, 30, 181, 51))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setLineWidth(2)
        self.label.setAlignment(QtCore.Qt.AlignCenter)  # ✅ Fixed syntax
        self.label.setObjectName("label")
        
        self.Extractinvoicbutton = QtWidgets.QPushButton(Dialog)
        self.Extractinvoicbutton.setGeometry(QtCore.QRect(0, 180, 200, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.Extractinvoicbutton.setFont(font)
        self.Extractinvoicbutton.setObjectName("Extractinvoicbutton")

        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setGeometry(QtCore.QRect(220, 180, 200, 41))
        self.pushButton_2.setMaximumSize(QtCore.QSize(16777215, 16777215))  # ✅ Fixed invalid max size
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Main Window"))
        self.label.setText(_translate("Dialog", "XtractPDF"))
        self.Extractinvoicbutton.setText(_translate("Dialog", "Extract Invoice Data"))
        self.pushButton_2.setText(_translate("Dialog", "Compare Cargo Manifests"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QWidget()  # ✅ Ensure consistency with QWidget
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
