from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the UI file
        ui_file = QFile("main.ui")  # Make sure 'main.ui' is in the same folder
        ui_file.open(QFile.ReadOnly)
        self.ui = QUiLoader().load(ui_file, self)
        ui_file.close()

        # Connect the "OK" button click to a function
        self.ui.okButton.clicked.connect(self.on_ok_clicked)

    def on_ok_clicked(self):
        print("OK Button Clicked!")  # This will print in the console

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.ui.show()  # Show the UI
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
