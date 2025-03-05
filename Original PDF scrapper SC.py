import sys
import os
import re
import camelot
import pandas as pd

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar,
    QFileDialog, QMessageBox
)

#############################################################################
#                           Parsing / Logic Functions                        #
#                         (With updated regex)                               #
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

    # UPDATED: Capture everything after "Description:" instead of just one word
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
    """
    Helper function to find *all* numeric tokens (e.g. 31.80, 12,000, 39.60)
    and skip a token if it collapses to '42'.
    Returns a list of all valid numeric tokens (strings).
    """
    text = text.replace('\n', ' ')
    nums = re.findall(r"[\d,\.]+", text)
    cleaned = []
    for val in nums:
        # Skip anything that is '42' once commas/dots are removed
        if val.replace(',', '').replace('.', '') == '42':
            continue
        cleaned.append(val)
    return cleaned

def parse_item_price(text):
    """
    Tries to parse an item price from the given column text by returning
    the *last* numeric token. Skips standalone '42'.
    """
    found = parse_all_numbers(text)
    return found[-1] if found else ""

def extract_filtered_data_with_following_rows(pdf_path, rows_after=4):
    """
    Same as your original function but uses PyQt's QMessageBox on error
    """
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
                lambda row: row.astype(str).str.contains("|".join(patterns),
                                                         na=False,
                                                         case=False).any(),
                axis=1
            )
            match_indices = match_mask[match_mask].index

            for match_index in match_indices:
                start_index = match_index
                end_index = match_index + rows_after + 1
                if end_index > len(df):
                    end_index = len(df)

                matched_block = df.iloc[start_index:end_index]

                # -- col_1: parse container + description
                col1_lines = matched_block["col_1"].dropna().astype(str).tolist()
                filtered_lines = []
                for line in col1_lines:
                    if line.strip().lower() == "marks":
                        continue
                    filtered_lines.append(line)

                col1_text = " ".join(filtered_lines).strip()
                col1_text = re.sub(r"(?i)(1Z[A-Za-z0-9]+)(marks)", r"\1 Marks", col1_text)
                container_number, description = parse_marks_and_description(col1_text)

                # -- col_12: commodity + gross mass
                if "col_12" in matched_block.columns:
                    col12_text = " ".join(matched_block["col_12"].dropna().astype(str)).strip()
                else:
                    col12_text = ""
                commodity_code, gross_mass = parse_commodity_and_grossmass(col12_text)

                # -- col_16: item price
                if "col_16" in matched_block.columns:
                    col16_text = " ".join(matched_block["col_16"].dropna().astype(str)).strip()
                else:
                    col16_text = ""
                item_price = parse_item_price(col16_text)

                # Fallback if no item_price
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
#                       PyQt Worker Thread (for background)                  #
#############################################################################

class ProcessPDFThread(QThread):
    # Signal that carries either the resulting DataFrame or an error
    finished = pyqtSignal(pd.DataFrame, str)  # (dataframe, error_message)

    def __init__(self, pdf_path, parent=None):
        super().__init__(parent)
        self.pdf_path = pdf_path

    def run(self):
        """
        The actual thread function that processes the PDF.
        We catch exceptions and emit them via the finished signal.
        """
        try:
            df = extract_filtered_data_with_following_rows(self.pdf_path)
            if df is None or df.empty:
                # No matching data found
                self.finished.emit(pd.DataFrame(), "No matching data found.")
            else:
                self.finished.emit(df, "")  # no error
        except Exception as e:
            self.finished.emit(pd.DataFrame(), str(e))

#############################################################################
#                          The Main PyQt Window                              #
#############################################################################

class PDFToExcelApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF to Excel Converter (PyQt Dark Mode)")
        self.resize(500, 350)

        self.pdf_path = None
        self.dataframe = None  # Will store the final DataFrame

        # --- Central widget/layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main vertical layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header label
        self.header_label = QLabel("PDF to Excel Converter")
        self.header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        main_layout.addWidget(self.header_label, alignment=Qt.AlignCenter)

        # Instructions
        instructions_text = (
            "1. Click 'Select PDF & Convert' to pick a PDF.\n"
            "2. Wait for processing to finish.\n"
            "3. Click 'Download Result' to choose a location to save the Excel file."
        )
        self.instructions_label = QLabel(instructions_text)
        self.instructions_label.setStyleSheet("color: #CCCCCC;")
        main_layout.addWidget(self.instructions_label, alignment=Qt.AlignCenter)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #AAAAAA;")
        main_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # Indeterminate
        main_layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        main_layout.addLayout(buttons_layout)

        # Button: Select PDF & Convert
        self.select_button = QPushButton("Select PDF & Convert")
        self.select_button.clicked.connect(self.on_select_pdf)
        buttons_layout.addWidget(self.select_button)

        # Button: Download Result
        self.download_button = QPushButton("Download Result")
        self.download_button.setEnabled(False)  # Disabled until done
        self.download_button.clicked.connect(self.on_download)
        buttons_layout.addWidget(self.download_button)

        # Apply a dark mode style sheet with purple accent
        self.set_dark_mode_styles()

    def set_dark_mode_styles(self):
        """
        A simple dark theme with purple accents for buttons and progress bar.
        """
        dark_bg = "#2B2B2B"
        lighter_bg = "#3A3A3A"
        purple_btn = "#9E4FFF"
        purple_hover = "#7C3CCC"
        text_color = "#FFFFFF"

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {dark_bg};
            }}
            QWidget {{
                background-color: {dark_bg};
                color: {text_color};
            }}
            QPushButton {{
                background-color: {purple_btn};
                border-radius: 4px;
                padding: 6px;
                color: #FFFFFF;
            }}
            QPushButton:hover {{
                background-color: {purple_hover};
            }}
            QLabel {{
                color: #FFFFFF;
            }}
            QProgressBar {{
                text-align: center;
                background-color: {lighter_bg};
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {purple_btn};
            }}
        """)

    ########################################################################
    #                           Button Callbacks                            #
    ########################################################################

    def on_select_pdf(self):
        """
        Let user pick a PDF file. Then start parsing in a separate thread.
        """
        pdf_file, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf);;All Files (*)")
        if not pdf_file:
            return  # user cancelled

        self.pdf_path = pdf_file
        self.status_label.setText("Processing, please wait...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)  # reset
        # Indeterminate mode means max=0 in Qt
        self.progress_bar.setMaximum(0)

        # Disable buttons during processing
        self.select_button.setEnabled(False)
        self.download_button.setEnabled(False)

        # Start background thread
        self.thread = ProcessPDFThread(pdf_path=self.pdf_path)
        self.thread.finished.connect(self.on_process_finished)
        self.thread.start()

    def on_process_finished(self, df, error_message):
        """
        Called when the background thread finishes. 
        df: DataFrame (possibly empty)
        error_message: string (empty if no error)
        """
        self.progress_bar.setVisible(False)
        self.select_button.setEnabled(True)

        if error_message:
            # An error or some message
            self.status_label.setText(f"Error: {error_message}")
            QMessageBox.critical(self, "Error", error_message)
            return

        if df.empty:
            # "No matching data found." or truly empty
            self.status_label.setText("No matching data found. Nothing to download.")
            return

        # Otherwise, success
        self.dataframe = df
        self.status_label.setText("Processing Complete! You can now download the result.")
        self.download_button.setEnabled(True)

    def on_download(self):
        """
        Let user pick a save location, then save the DataFrame to Excel.
        """
        if self.dataframe is None or self.dataframe.empty:
            QMessageBox.warning(self, "No Data", "No data to download.")
            return

        save_file, _ = QFileDialog.getSaveFileName(
            self,
            "Save Excel File",
            "",
            "Excel Files (*.xlsx);;All Files (*)"
        )
        if not save_file:
            return

        try:
            self.dataframe.to_excel(save_file, index=False)
            QMessageBox.information(self, "Success", f"File saved to:\n{save_file}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unable to save file: {str(e)}")

#############################################################################
#                                Main Entry                                 #
#############################################################################

def main():
    app = QApplication(sys.argv)
    window = PDFToExcelApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
