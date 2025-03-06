import sys
import os
import re
import camelot
import pandas as pd

from PyQt5 import QtCore, QtGui, QtWidgets

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
        if len(raw) >= 2:
            commodity_code = raw[:-2]
        else:
            commodity_code = raw
    pattern_gross = re.compile(r"35 Gross Mass \(Kg\)[A-Za-z]*(\d+\.\d+)", re.IGNORECASE)
    match_gross = pattern_gross.search(text)
    if match_gross:
        gross_mass = match_gross.group(1)
    return commodity_code, gross_mass

def parse_all_numbers(text):
    text = text.replace('\n', ' ')
    nums = re.findall(r"[\d,\.]+", text)
    cleaned = []
    for val in nums:
        if val.replace(',', '').replace('.', '') == '42':
            continue
        cleaned.append(val)
    return cleaned

def parse_item_price(text):
    found = parse_all_numbers(text)
    return found[-1] if found else ""

def extract_filtered_data_with_following_rows(pdf_path, rows_after=4):
    try:
        tables = camelot.read_pdf(
            pdf_path,
            pages="all",
            flavor="lattice",  # or 'stream'
            strip_text="\n",
            line_scale=40
        )
        patterns = ["31 Packages", "Description of Goods"]
        all_data_rows = []
        for table_index, table in enumerate(tables):
            df = table.df
            df.columns = [f"col_{i}" for i in range(len(df.columns))]
            match_mask = df.apply(
                lambda row: row.astype(str).str.contains("|".join(patterns), na=False, case=False).any(),
                axis=1
            )
            match_indices = match_mask[match_mask].index
            for match_index in match_indices:
                start_index = match_index
                end_index = match_index + rows_after + 1
                if end_index > len(df):
                    end_index = len(df)
                matched_block = df.iloc[start_index:end_index]
                # Parse container number & description from col_1
                col1_lines = matched_block["col_1"].dropna().astype(str).tolist()
                filtered_lines = []
                for line in col1_lines:
                    if line.strip().lower() == "marks":
                        continue
                    filtered_lines.append(line)
                col1_text = " ".join(filtered_lines).strip()
                col1_text = re.sub(r"(?i)(1Z[A-Za-z0-9]+)(marks)", r"\1 Marks", col1_text)
                container_number, description = parse_marks_and_description(col1_text)
                # Parse commodity code & gross mass from col_12
                if "col_12" in matched_block.columns:
                    col12_text = " ".join(matched_block["col_12"].dropna().astype(str)).strip()
                else:
                    col12_text = ""
                commodity_code, gross_mass = parse_commodity_and_grossmass(col12_text)
                # Parse item price from col_16
                if "col_16" in matched_block.columns:
                    col16_text = " ".join(matched_block["col_16"].dropna().astype(str)).strip()
                else:
                    col16_text = ""
                item_price = parse_item_price(col16_text)
                if not item_price:
                    combined_text = col12_text + " " + col16_text
                    combined_nums = parse_all_numbers(combined_text)
                    if combined_nums:
                        if gross_mass in combined_nums:
                            combined_nums.remove(gross_mass)
                        if combined_nums:
                            item_price = combined_nums[-1]
                data_dict = {
                    "Marks & Nosof Packages": container_number,
                    "Description": description,
                    "Commodity_Code": commodity_code,
                    "Gross_Mass": gross_mass,
                    "Item_Price": item_price
                }
                all_data_rows.append(data_dict)
        if all_data_rows:
            return pd.DataFrame(all_data_rows)
        else:
            return None
    except Exception as e:
        raise RuntimeError(f"Failed to process the PDF: {e}")

#############################################################################
#                   PyQt Worker Thread (for background processing)         #
#############################################################################

class ProcessPDFThread(QtCore.QThread):
    # This signal carries (dataframe, error_message)
    finished = QtCore.pyqtSignal(pd.DataFrame, str)
    
    def __init__(self, pdf_path, parent=None):
        super().__init__(parent)
        self.pdf_path = pdf_path

    def run(self):
        try:
            df = extract_filtered_data_with_following_rows(self.pdf_path)
            if df is None or df.empty:
                self.finished.emit(pd.DataFrame(), "No matching data found.")
            else:
                self.finished.emit(df, "")
        except Exception as e:
            self.finished.emit(pd.DataFrame(), str(e))

#############################################################################
#                     Designer-Generated UI Class (Extract Invoice Data)     #
#############################################################################

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(500, 400)
        
        self.SelectPDFbutton = QtWidgets.QPushButton(Dialog)
        self.SelectPDFbutton.setGeometry(QtCore.QRect(20, 300, 200, 35))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.SelectPDFbutton.setFont(font)
        self.SelectPDFbutton.setObjectName("SelectPDFbutton")
        
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setGeometry(QtCore.QRect(240, 300, 200, 35))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(50, 20, 400, 30))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(20, 80, 460, 100))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        
        self.progressBar = QtWidgets.QProgressBar(Dialog)
        self.progressBar.setGeometry(QtCore.QRect(140, 250, 200, 20))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        
        self.pushButton_3 = QtWidgets.QPushButton(Dialog)
        self.pushButton_3.setGeometry(QtCore.QRect(10, 10, 80, 30))
        self.pushButton_3.setObjectName("pushButton_3")
        
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Extract Invoice Data"))
        self.label.setText(_translate("Dialog", "Extract Invoice Data"))
        self.label_2.setText(_translate("Dialog", 
            "1. Click 'Select PDF & Convert' to pick a PDF.\n"
            "2. Wait for processing to finish.\n"
            "3. Click 'Download Result' to choose a location to save the Excel file."
        ))
        self.SelectPDFbutton.setText(_translate("Dialog", "Select PDF to Convert"))
        self.pushButton_2.setText(_translate("Dialog", "Download Result"))
        self.pushButton_3.setText(_translate("Dialog", "Back"))

#############################################################################
#                Main Dialog Class that Integrates UI & PDF Logic            #
#############################################################################

class PDFToExcelDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.pdf_path = None
        self.dataframe = None

        # Add a status label for messages (positioned below the instruction label)
        self.status_label = QtWidgets.QLabel(self)
        self.status_label.setGeometry(QtCore.QRect(20, 210, 460, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.status_label.setFont(font)
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setText("")

        # Connect the UI buttons to our methods
        self.ui.SelectPDFbutton.clicked.connect(self.on_select_pdf)
        self.ui.pushButton_2.clicked.connect(self.on_download)
        self.ui.pushButton_3.clicked.connect(self.on_back)

    def on_select_pdf(self):
        print("Select PDF button clicked.")
        pdf_file, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select PDF File", "", "PDF Files (*.pdf);;All Files (*)"
        )
        if not pdf_file:
            print("No file selected.")
            return
        self.pdf_path = pdf_file
        self.status_label.setText("Processing, please wait...")
        self.ui.progressBar.setVisible(True)
        self.ui.progressBar.setValue(0)
        self.ui.progressBar.setMaximum(0)  # Set to indeterminate mode
        self.ui.SelectPDFbutton.setEnabled(False)
        self.ui.pushButton_2.setEnabled(False)
        self.thread = ProcessPDFThread(pdf_path=self.pdf_path)
        self.thread.finished.connect(self.on_process_finished)
        self.thread.start()
        print("PDF processing thread started.")

    def on_process_finished(self, df, error_message):
        print("Process finished. Error message:", error_message)
        self.ui.progressBar.setVisible(False)
        self.ui.SelectPDFbutton.setEnabled(True)
        if error_message:
            self.status_label.setText(f"Error: {error_message}")
            QtWidgets.QMessageBox.critical(self, "Error", error_message)
            return
        if df.empty:
            self.status_label.setText("No matching data found.")
            return
        self.dataframe = df
        self.status_label.setText("Processing Complete! Click 'Download Result'.")
        self.ui.pushButton_2.setEnabled(True)

    def on_download(self):
        if self.dataframe is None or self.dataframe.empty:
            QtWidgets.QMessageBox.warning(self, "No Data", "No data to download.")
            return
        save_file, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Excel File", "", "Excel Files (*.xlsx);;All Files (*)"
        )
        if not save_file:
            return
        try:
            self.dataframe.to_excel(save_file, index=False)
            QtWidgets.QMessageBox.information(self, "Success", f"File saved to:\n{save_file}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Unable to save file: {str(e)}")

    def on_back(self):
        # Close the dialog (or integrate navigation as needed)
        self.close()

#############################################################################
#                               Main Entry                                  #
#############################################################################

def main():
    app = QtWidgets.QApplication(sys.argv)
    dialog = PDFToExcelDialog()
    dialog.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
