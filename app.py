import sys
from PyQt5 import QtWidgets
from main import Ui_Dialog as Ui_MainWindow         # Main Page UI (from main.py)
from CompareCargoManifests import CompareCargoPage     # Custom Compare Cargo widget
from ExtractInvoiceData import PDFToExcelDialog        # Integrated Extract Invoice dialog

class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(600, 500)
        # Create QStackedWidget to hold multiple pages
        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        # Create pages:
        self.main_page = QtWidgets.QWidget()
        self.compare_page = CompareCargoPage()      # Use our custom Compare Cargo widget
        self.extract_page = PDFToExcelDialog()        # Use integrated Extract Invoice dialog

        # Set up UI for Main page
        self.main_ui = Ui_MainWindow()
        self.main_ui.setupUi(self.main_page)
        
        # Add pages to the QStackedWidget
        self.stack.addWidget(self.main_page)      # Index 0: Main Page
        self.stack.addWidget(self.compare_page)     # Index 1: Compare Cargo Page
        self.stack.addWidget(self.extract_page)     # Index 2: Extract Invoice Page

        # Connect navigation buttons:
        self.main_ui.Extractinvoicbutton.clicked.connect(lambda: self.switch_page(2))
        self.main_ui.pushButton_2.clicked.connect(lambda: self.switch_page(1))
        self.compare_page.pushButton_back.clicked.connect(lambda: self.switch_page(0))
        self.extract_page.ui.pushButton_3.clicked.connect(lambda: self.switch_page(0))

        # Apply dark theme style sheet globally
        self.apply_dark_theme()

    def apply_dark_theme(self):
        dark_theme = """
        QWidget {
            background-color: #2B2B2B;
            color: #FFFFFF;
        }
        QPushButton {
            background-color: #9E4FFF;
            border-radius: 4px;
            padding: 6px;
            color: #FFFFFF;
        }
        QPushButton:hover {
            background-color: #7C3CCC;
        }
        QLabel {
            color: #FFFFFF;
        }
        QProgressBar {
            background-color: #3A3A3A;
            border-radius: 4px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #9E4FFF;
        }
        QTableView {
            background-color: #3A3A3A;
            alternate-background-color: #2B2B2B;
            color: #FFFFFF;
        }
        """
        self.setStyleSheet(dark_theme)

    def switch_page(self, index):
        """Switch between pages using QStackedWidget."""
        self.stack.setCurrentIndex(index)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
