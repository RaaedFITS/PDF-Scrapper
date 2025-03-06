import sys
from PyQt5 import QtWidgets
from main import Ui_Dialog as Ui_MainWindow         # Main Page UI (from main.py)
from CompareCargoManifests import Ui_Dialog as Ui_CompareCargo   # Compare Cargo UI (from CompareCargoManifests.py)
from ExtractInvoiceData import PDFToExcelDialog        # Integrated Extract Invoice dialog from ExtractInvoiceData.py

class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        # Create QStackedWidget to hold multiple pages
        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        # Create pages for Main and Compare Cargo using the raw UI,
        # and use the integrated dialog (with PDF logic) for Extract Invoice.
        self.main_page = QtWidgets.QWidget()
        self.compare_page = QtWidgets.QWidget()
        self.extract_page = PDFToExcelDialog()  # Use the integrated class from ExtractInvoiceData.py

        # Set up UI for Main and Compare pages
        self.main_ui = Ui_MainWindow()
        self.main_ui.setupUi(self.main_page)
        self.compare_ui = Ui_CompareCargo()
        self.compare_ui.setupUi(self.compare_page)
        
        # Add pages to the QStackedWidget
        self.stack.addWidget(self.main_page)      # Index 0: Main Page
        self.stack.addWidget(self.compare_page)     # Index 1: Compare Cargo Page
        self.stack.addWidget(self.extract_page)     # Index 2: Extract Invoice Page

        # Connect navigation buttons:
        # From Main page:
        self.main_ui.Extractinvoicbutton.clicked.connect(lambda: self.switch_page(2))
        self.main_ui.pushButton_2.clicked.connect(lambda: self.switch_page(1))
        # From Compare Cargo page:
        self.compare_ui.pushButton_back.clicked.connect(lambda: self.switch_page(0))
        # From Extract Invoice page (use the integrated dialog’s UI):
        self.extract_page.ui.pushButton_3.clicked.connect(lambda: self.switch_page(0))

    def switch_page(self, index):
        """Switch between pages using QStackedWidget."""
        self.stack.setCurrentIndex(index)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
