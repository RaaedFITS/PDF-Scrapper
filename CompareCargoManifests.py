import pdfplumber
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets

# --- Helper Functions ---

def extract_all_tables(pdf_path):
    """
    Reads ALL pages from the PDF and extracts the FIRST table found on each page.
    Concatenates them into one DataFrame.
    Returns an empty DataFrame if no tables are found.
    """
    all_dfs = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                df = pd.DataFrame(table[1:], columns=table[0])
                all_dfs.append(df)
    if not all_dfs:
        print(f"No tables found in {pdf_path}. Returning empty DataFrame.")
        return pd.DataFrame()
    return pd.concat(all_dfs, ignore_index=True)

def clean_cell(value):
    """Replace literal '\\n' with a space and strip whitespace."""
    if isinstance(value, str):
        return value.replace('\\n', ' ').strip()
    return value

# --- Custom Widget: CompareCargoPage ---
class CompareCargoPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        # File paths
        self.parent_pdf_1 = None
        self.parent_pdf_2 = None
        self.child_pdf = None
        self.df_final = None

        # Additional labels to show the selected file names
        self.parent1_filename_label = QtWidgets.QLabel(self)
        self.parent1_filename_label.setGeometry(QtCore.QRect(330, 70, 250, 30))
        self.parent1_filename_label.setText("")
        self.parent2_filename_label = QtWidgets.QLabel(self)
        self.parent2_filename_label.setGeometry(QtCore.QRect(330, 120, 250, 30))
        self.parent2_filename_label.setText("")
        self.child_filename_label = QtWidgets.QLabel(self)
        self.child_filename_label.setGeometry(QtCore.QRect(330, 170, 250, 30))
        self.child_filename_label.setText("")

        # Disable the Run and Download buttons initially
        self.pushButton_6.setEnabled(False)
        self.pushButton_4.setEnabled(False)

        # Connect buttons to methods
        self.pushButton.clicked.connect(self.select_parent1)
        self.pushButton_3.clicked.connect(self.select_parent2)
        self.pushButton_5.clicked.connect(self.select_child)
        self.pushButton_6.clicked.connect(self.run_merge)
        self.pushButton_4.clicked.connect(self.download_result)
        self.pushButton_back.clicked.connect(self.on_back)

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(600, 450)  # Increased size

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
        self.pushButton.setStyleSheet(
            "border-radius: 10px; background-color: #9E4FFF; color: white;"
        )

        # Add Parent 2
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(50, 120, 120, 30))
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.pushButton_3 = QtWidgets.QPushButton(Dialog)
        self.pushButton_3.setGeometry(QtCore.QRect(200, 120, 120, 30))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setStyleSheet(
            "border-radius: 10px; background-color: #9E4FFF; color: white;"
        )

        # Add Child Manifest
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(50, 170, 120, 30))
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.pushButton_5 = QtWidgets.QPushButton(Dialog)
        self.pushButton_5.setGeometry(QtCore.QRect(200, 170, 120, 30))
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_5.setStyleSheet(
            "border-radius: 10px; background-color: #9E4FFF; color: white;"
        )

        # Table for Comparing (output)
        self.tableView = QtWidgets.QTableView(Dialog)
        self.tableView.setGeometry(QtCore.QRect(50, 220, 500, 120))
        self.tableView.setObjectName("tableView")

        # Download Button
        self.pushButton_4 = QtWidgets.QPushButton(Dialog)
        self.pushButton_4.setGeometry(QtCore.QRect(50, 390, 500, 30))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.setStyleSheet(
            "border-radius: 10px; background-color: #9E4FFF; color: white;"
        )

        # Run Button
        self.pushButton_6 = QtWidgets.QPushButton(Dialog)
        self.pushButton_6.setGeometry(QtCore.QRect(50, 430, 500, 40))
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_6.setStyleSheet(
            "border-radius: 10px; background-color: #9E4FFF; color: white;"
        )

        # Back Button
        self.pushButton_back = QtWidgets.QPushButton(Dialog)
        self.pushButton_back.setGeometry(QtCore.QRect(10, 10, 80, 30))
        self.pushButton_back.setObjectName("pushButton_back")


        # Status label for messages (if needed, can be repositioned)
        self.status_label = QtWidgets.QLabel(Dialog)
        self.status_label.setGeometry(QtCore.QRect(50, 350, 500, 30))
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setObjectName("status_label")
        self.status_label.setText("")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Compare Cargo Manifests"))
        self.label_2.setText(_translate("Dialog", "Compare Cargo Manifests"))
        self.label.setText(_translate("Dialog", "Add Parent 1"))
        self.label_4.setText(_translate("Dialog", "Add Parent 2"))
        self.label_3.setText(_translate("Dialog", "Child Manifest"))
        self.pushButton.setText(_translate("Dialog", "Select File"))
        self.pushButton_3.setText(_translate("Dialog", "Select File"))
        self.pushButton_5.setText(_translate("Dialog", "Select File"))
        self.pushButton_4.setText(_translate("Dialog", "Download"))
        self.pushButton_6.setText(_translate("Dialog", "Run"))
        self.pushButton_back.setText(_translate("Dialog", "Back"))
        # Make Run and Download buttons consistent
        btn_style = "background-color: #9E4FFF; color: white; border-radius: 4px; padding: 6px;"
        self.pushButton_4.setStyleSheet(btn_style)
        self.pushButton_6.setStyleSheet(btn_style)

    def update_run_button_state(self):
        # Enable the Run button only if all files are selected
        if self.parent_pdf_1 and self.parent_pdf_2 and self.child_pdf:
            self.pushButton_6.setEnabled(True)
        else:
            self.pushButton_6.setEnabled(False)

    # --- File Selection Methods ---
    def select_parent1(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Parent PDF 1", "", "PDF Files (*.pdf);;All Files (*)"
        )
        if file:
            self.parent_pdf_1 = file
            self.parent1_filename_label.setText(file.split("/")[-1])
            self.status_label.setText("Parent PDF 1 selected.")
            self.update_run_button_state()

    def select_parent2(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Parent PDF 2", "", "PDF Files (*.pdf);;All Files (*)"
        )
        if file:
            self.parent_pdf_2 = file
            self.parent2_filename_label.setText(file.split("/")[-1])
            self.status_label.setText("Parent PDF 2 selected.")
            self.update_run_button_state()

    def select_child(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Child PDF", "", "PDF Files (*.pdf);;All Files (*)"
        )
        if file:
            self.child_pdf = file
            self.child_filename_label.setText(file.split("/")[-1])
            self.status_label.setText("Child PDF selected.")
            self.update_run_button_state()

    # --- Run and Merge Logic ---
    def run_merge(self):
        # Double-check that all files are selected
        if not (self.parent_pdf_1 and self.parent_pdf_2 and self.child_pdf):
            QtWidgets.QMessageBox.warning(self, "Missing Files", "Please select all required files.")
            return
        self.status_label.setText("Processing PDFs...")
        try:
            df_parent_1 = extract_all_tables(self.parent_pdf_1)
            df_parent_2 = extract_all_tables(self.parent_pdf_2)
            df_parent = pd.concat([df_parent_1, df_parent_2], ignore_index=True)
            df_child = extract_all_tables(self.child_pdf)
            if df_parent.empty:
                QtWidgets.QMessageBox.critical(self, "Error", "Parent PDFs produced no data.")
                self.status_label.setText("Parent PDFs produced no data.")
                return
            if df_child.empty:
                self.status_label.setText("Child PDF produced no data. Proceeding with parent data only.")
            df_parent = df_parent.apply(lambda col: col.map(clean_cell))
            df_child = df_child.apply(lambda col: col.map(clean_cell))
            rename_parent = {}
            if "HAWB\nNumber" in df_parent.columns:
                rename_parent["HAWB\nNumber"] = "HAWB"
            if "Origin" not in df_parent.columns:
                candidate_origin = [col for col in df_parent.columns if "origin" in col.lower()]
                if len(candidate_origin) == 1:
                    rename_parent[candidate_origin[0]] = "Origin"
            df_parent.rename(columns=rename_parent, inplace=True)
            rename_child = {}
            if "HAWB\nShipment" in df_child.columns:
                rename_child["HAWB\nShipment"] = "HAWB"
            if "Secondary Tracking Numbers" in df_child.columns:
                rename_child["Secondary Tracking Numbers"] = "secondary"
            df_child.rename(columns=rename_child, inplace=True)
            if "HAWB" not in df_parent.columns:
                QtWidgets.QMessageBox.critical(self, "Error", "No 'HAWB' column found in parent.")
                self.status_label.setText("Error: No 'HAWB' column in parent.")
                return
            if not df_child.empty and "HAWB" not in df_child.columns:
                QtWidgets.QMessageBox.critical(self, "Error", "No 'HAWB' column found in child.")
                self.status_label.setText("Error: No 'HAWB' column in child.")
                return
            df_merged = pd.merge(
                df_parent,
                df_child,
                on="HAWB",
                how="left",
                suffixes=("_parent", "_child")
            )
            if "Origin" not in df_merged.columns:
                df_merged["Origin"] = df_parent.set_index("HAWB")["Origin"].reindex(df_merged["HAWB"]).values
            if "secondary" not in df_merged.columns:
                df_merged["secondary"] = ""
            final_rows = []
            for _, row in df_merged.iterrows():
                row_dict = row.to_dict()
                sec_str = row_dict.get("secondary", "")
                if pd.isna(sec_str):
                    sec_str = ""
                secondary_list = [s.strip() for s in sec_str.split(",") if s.strip()]
                total_copies = len(secondary_list) + 1
                for i in range(total_copies):
                    new_row = row_dict.copy()
                    if i == 0:
                        new_row["Type"] = "Master"
                    else:
                        new_row["Type"] = "Baby"
                        idx_in_sec = i - 1
                        if idx_in_sec < len(secondary_list):
                            new_row["HAWB"] = secondary_list[idx_in_sec]
                        else:
                            new_row["HAWB"] = ""
                    final_rows.append(new_row)
            df_expanded = pd.DataFrame(final_rows)
            parent_columns_order = [
                "Origin",
                "#",
                "HAWB",
                "Pcs",
                "Weight",
                "Shipper Details",
                "Dest",
                "Bill\nTerm",
                "Consignee Details",
                "Description\nof Goods",
                "Total\nValue",
                "Total\nValue(LKR)"
            ]
            final_cols = parent_columns_order + ["Type"]
            existing_cols = [c for c in final_cols if c in df_expanded.columns]
            self.df_final = df_expanded[existing_cols]
            self.status_label.setText("Processing Complete! Click 'Download' to save the Excel file.")
            self.pushButton_4.setEnabled(True)
            self.update_table_view(df_expanded)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Processing failed: {str(e)}")
            self.status_label.setText(f"Error: {str(e)}")

    def update_table_view(self, df):
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(df.columns.tolist())
        for _, row in df.iterrows():
            items = [QtGui.QStandardItem(str(val)) for val in row]
            model.appendRow(items)
        self.tableView.setModel(model)
        self.tableView.resizeColumnsToContents()

    def download_result(self):
        if self.df_final is None or self.df_final.empty:
            QtWidgets.QMessageBox.warning(self, "No Data", "No data to download.")
            return
        save_file, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Excel File", "", "Excel Files (*.xlsx);;All Files (*)"
        )
        if not save_file:
            return
        try:
            self.df_final.to_excel(save_file, index=False)
            QtWidgets.QMessageBox.information(self, "Success", f"File saved to:\n{save_file}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Unable to save file: {str(e)}")

    def on_back(self):
        self.close()
