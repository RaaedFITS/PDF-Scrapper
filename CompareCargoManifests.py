from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(600, 450)  # ✅ Increased size

        # Title Label
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(150, 10, 300, 40))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")

        # Add Parent 1
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(50, 70, 120, 30))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")

        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(200, 70, 120, 30))
        self.pushButton.setObjectName("pushButton")

        # Add Parent 2
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(50, 120, 120, 30))
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")

        self.pushButton_3 = QtWidgets.QPushButton(Dialog)
        self.pushButton_3.setGeometry(QtCore.QRect(200, 120, 120, 30))
        self.pushButton_3.setObjectName("pushButton_3")

        # Add Child Manifest
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(50, 170, 120, 30))
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")

        self.pushButton_5 = QtWidgets.QPushButton(Dialog)
        self.pushButton_5.setGeometry(QtCore.QRect(200, 170, 120, 30))
        self.pushButton_5.setObjectName("pushButton_5")

        # Table for Comparing
        self.tableView = QtWidgets.QTableView(Dialog)
        self.tableView.setGeometry(QtCore.QRect(50, 220, 500, 120))
        self.tableView.setObjectName("tableView")

        # Download Button
        self.pushButton_4 = QtWidgets.QPushButton(Dialog)
        self.pushButton_4.setGeometry(QtCore.QRect(250, 360, 100, 30))
        self.pushButton_4.setObjectName("pushButton_4")

        # Run Button
        self.pushButton_6 = QtWidgets.QPushButton(Dialog)
        self.pushButton_6.setGeometry(QtCore.QRect(50, 400, 500, 40))
        self.pushButton_6.setObjectName("pushButton_6")

        # ✅ Add Back Button
        self.pushButton_back = QtWidgets.QPushButton(Dialog)
        self.pushButton_back.setGeometry(QtCore.QRect(10, 10, 80, 30))  # Top-left position
        self.pushButton_back.setObjectName("pushButton_back")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Compare Cargo Manifests"))
        self.label.setText(_translate("Dialog", "Add Parent 1"))
        self.label_2.setText(_translate("Dialog", "Compare Cargo Manifests"))
        self.label_3.setText(_translate("Dialog", "Child Manifest"))
        self.label_4.setText(_translate("Dialog", "Add Parent 2"))
        self.pushButton.setText(_translate("Dialog", "Select File"))
        self.pushButton_3.setText(_translate("Dialog", "Select File"))
        self.pushButton_5.setText(_translate("Dialog", "Select File"))
        self.pushButton_4.setText(_translate("Dialog", "Download"))
        self.pushButton_6.setText(_translate("Dialog", "Run"))
        self.pushButton_back.setText(_translate("Dialog", "Back"))  # ✅ Set text for Back Button
