from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit

class TextBox(QWidget):
    fnameEntered = pyqtSignal(str)

    def __init__(self, number):
        super().__init__()
        self.setWindowTitle("Enter Filename For Multimeter " + str(number))
        self.setGeometry(100, 100, 300, 200)
        self.filename = None  # Initialize filename attribute

        # Create a layout
        self.layout = QVBoxLayout(self)

        # Create a text entry box
        self.line_edit = QLineEdit()
        self.line_edit.returnPressed.connect(self.on_return_pressed)

        # Add the text entry box to the layout
        self.layout.addWidget(self.line_edit)

        # Show the window
        self.setLayout(self.layout)

    def on_return_pressed(self):
        # Get text from the line edit and emit the signal
        text = self.line_edit.text()
        fname = text + ".csv"
        self.filename = fname  # Store filename in attribute
        self.fnameEntered.emit(fname)
        self.close()


# def main():
#     app = QApplication(sys.argv)

#     # Create the widget
#     text_box = TextBox(1)

#     # Create a slot to receive the file name signal
#     def receive_file_name(fname):
#         print("Received file name:", fname)

#     # Connect the signal to the slot
#     text_box.fnameEntered.connect(receive_file_name)

#     sys.exit(app.exec_())

# if __name__ == '__main__':
#     main()
