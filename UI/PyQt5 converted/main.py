from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(600, 500)  # Updated size to 600x500

        # Title Label
        self.titleLabel = QtWidgets.QLabel(Dialog)
        self.titleLabel.setGeometry(QtCore.QRect(0, 20, 600, 60))
        font = QtGui.QFont()
        font.setPointSize(32)
        self.titleLabel.setFont(font)
        self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.titleLabel.setObjectName("titleLabel")

        # Instruction Label
        self.instructionLabel = QtWidgets.QLabel(Dialog)
        self.instructionLabel.setGeometry(QtCore.QRect(0, 100, 600, 40))
        font_instr = QtGui.QFont()
        font_instr.setPointSize(16)
        self.instructionLabel.setFont(font_instr)
        self.instructionLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.instructionLabel.setObjectName("instructionLabel")

        # Extract Invoice Data Button
        self.Extractinvoicbutton = QtWidgets.QPushButton(Dialog)
        self.Extractinvoicbutton.setGeometry(QtCore.QRect(50, 200, 220, 50))
        font_btn = QtGui.QFont()
        font_btn.setPointSize(12)
        self.Extractinvoicbutton.setFont(font_btn)
        self.Extractinvoicbutton.setObjectName("Extractinvoicbutton")
        self.Extractinvoicbutton.setStyleSheet(
            "border-radius: 25px; background-color: #9E4FFF; color: white;"
        )

        # Compare Cargo Manifests Button
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setGeometry(QtCore.QRect(330, 200, 220, 50))
        font_btn2 = QtGui.QFont()
        font_btn2.setPointSize(12)
        self.pushButton_2.setFont(font_btn2)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setStyleSheet(
            "border-radius: 25px; background-color: #9E4FFF; color: white;"
        )

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Main Window"))
        self.titleLabel.setText(_translate("Dialog", "XtractPDF"))
        self.instructionLabel.setText(_translate("Dialog", "Choose an option below to proceed"))
        self.Extractinvoicbutton.setText(_translate("Dialog", "Extract Invoice Data"))
        self.pushButton_2.setText(_translate("Dialog", "Compare Cargo Manifests"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QWidget()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
