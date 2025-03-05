import sys
import re
import camelot
import pandas as pd

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox

#############################################################################
#                           Parsing / Logic Functions                        #
#############################################################################

def parse_marks_and_description(text):
    match_1z = re.search(r"(?i)(1Z[A-Za-z0-9]+)(?![A-Za-z0-9])", text)
    if match_1z:
        container_number = match_1z.group(0).strip()
        container_number = re.sub(r"(?i)of$", "", container_number).strip()
    else:
        match_container = re.search(r"(?i)Number and kind\s*(\S+)", text)
        if match_container:
            container_number = match_container.group(1).strip()
        else:
            container_number = ""

    match_desc = re.search(r"(?i)Description:\s*(.+)", text)
    if match_desc:
        description = match_desc.group(1).strip()
    else:
        description = ""

    return container_number, description

def parse_commodity_and_grossmass(text):
    commodity_code = ""
    gross_mass = ""

    pattern_commodity = re.compile(r"33 Commodity \(HS\) Code(\d+)", re.IGNORECASE)
    match_com = pattern_commodity.search(text)
    if match_com:
        raw = match_com.group(1)
        commodity_code = raw[:-2] if len(raw) >= 2 else raw

    pattern_gross = re.compile(r"35 Gross Mass \(Kg\)[A-Za-z]*(\d+\.\d+)", re.IGNORECASE)
    match_gross = pattern_gross.search(text)
    if match_gross:
        gross_mass = match_gross.group(1)

    return commodity_code, gross_mass

def extract_filtered_data(pdf_path):
    try:
        tables = camelot.read_pdf(pdf_path, pages="all", flavor="lattice", strip_text="\n", line_scale=40)
        patterns = ["31 Packages", "Description of Goods"]
        all_data_rows = []

        for table in tables:
            df = table.df
            df.columns = [f"col_{i}" for i in range(len(df.columns))]

            match_mask = df.apply(lambda row: row.astype(str).str.contains("|".join(patterns), na=False, case=False).any(), axis=1)
            match_indices = match_mask[match_mask].index

            for match_index in match_indices:
                start_index = match_index
                end_index = match_index + 4 + 1
                end_index = min(end_index, len(df))

                matched_block = df.iloc[start_index:end_index]
                col1_text = " ".join(matched_block["col_1"].dropna().astype(str)).strip()
                container_number, description = parse_marks_and_description(col1_text)

                col12_text = " ".join(matched_block["col_12"].dropna().astype(str)).strip() if "col_12" in matched_block.columns else ""
                commodity_code, gross_mass = parse_commodity_and_grossmass(col12_text)

                data_dict = {
                    "Marks & Nosof Packages": container_number,
                    "Description": description,
                    "Commodity_Code": commodity_code,
                    "Gross_Mass": gross_mass
                }
                all_data_rows.append(data_dict)

        return pd.DataFrame(all_data_rows) if all_data_rows else None
    except Exception as e:
        raise RuntimeError(f"Failed to process the PDF: {e}")

#############################################################################
#                           PyQt Dialog UI with Logic                        #
#############################################################################

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)

        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(20, 240, 161, 28))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.select_pdf)

        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setGeometry(QtCore.QRect(220, 240, 161, 28))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setEnabled(False)
        self.pushButton_2.clicked.connect(self.save_result)

        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(100, 40, 211, 20))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label.setFont(font)
        self.label.setText("Extract Invoice Data")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")

        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(20, 90, 360, 91))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")

        self.progressBar = QtWidgets.QProgressBar(Dialog)
        self.progressBar.setGeometry(QtCore.QRect(130, 190, 118, 23))
        self.progressBar.setVisible(False)
        self.progressBar.setObjectName("progressBar")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        self.pdf_path = None
        self.dataframe = None

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "PDF to Excel Converter"))
        self.pushButton.setText(_translate("Dialog", "Select PDF to Convert"))
        self.pushButton_2.setText(_translate("Dialog", "Download Result"))
        self.label_2.setText(_translate("Dialog",
            "1. Click 'Select PDF & Convert' to pick a PDF.\n"
            "2. Wait for processing to finish.\n"
            "3. Click 'Download Result' to choose a location to save the Excel file."
        ))

    def select_pdf(self):
        pdf_file, _ = QFileDialog.getOpenFileName(None, "Select PDF File", "", "PDF Files (*.pdf);;All Files (*)")
        if not pdf_file:
            return

        self.pdf_path = pdf_file
        self.label_2.setText("Processing, please wait...")
        self.progressBar.setVisible(True)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(0)  # Indeterminate progress

        try:
            self.dataframe = extract_filtered_data(self.pdf_path)
            self.progressBar.setVisible(False)

            if self.dataframe is None or self.dataframe.empty:
                self.label_2.setText("No matching data found.")
                QMessageBox.warning(None, "No Data", "No matching data found.")
                return

            self.label_2.setText("Processing complete! Click 'Download Result' to save.")
            self.pushButton_2.setEnabled(True)

        except Exception as e:
            self.progressBar.setVisible(False)
            QMessageBox.critical(None, "Error", str(e))
            self.label_2.setText("Error: Failed to process PDF.")

    def save_result(self):
        if self.dataframe is None or self.dataframe.empty:
            QMessageBox.warning(None, "No Data", "No data to download.")
            return

        save_file, _ = QFileDialog.getSaveFileName(None, "Save Excel File", "", "Excel Files (*.xlsx);;All Files (*)")
        if not save_file:
            return

        try:
            self.dataframe.to_excel(save_file, index=False)
            QMessageBox.information(None, "Success", f"File saved to:\n{save_file}")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Unable to save file: {str(e)}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
