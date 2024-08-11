import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QLabel
from PyQt5.QtCore import Qt

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        # Create the main layout
        main_layout = QHBoxLayout()

        # Create the left and right sections
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        
        # Create top and bottom layouts for each section
        top_left_layout = QVBoxLayout()
        bottom_left_layout = QVBoxLayout()
        top_right_layout = QVBoxLayout()
        bottom_right_layout = QVBoxLayout()

        # Top left section
        top_left_top = QWidget()
        top_left_bottom = QWidget()
        top_left_top.setStyleSheet("background-color: lightblue;")
        top_left_bottom.setStyleSheet("background-color: lightcyan;")
        top_left_layout.addWidget(top_left_top)
        top_left_layout.addWidget(top_left_bottom)

        # Bottom left section
        bottom_left_top = QWidget()
        bottom_left_bottom = QWidget()
        bottom_left_top.setStyleSheet("background-color: lightgreen;")
        bottom_left_bottom.setStyleSheet("background-color: lightyellow;")
        bottom_left_layout.addWidget(bottom_left_top)
        bottom_left_layout.addWidget(bottom_left_bottom)

        # Top right section
        top_right_top = QWidget()
        top_right_bottom = QWidget()
        top_right_top.setStyleSheet("background-color: lightcoral;")
        top_right_bottom.setStyleSheet("background-color: lightpink;")
        top_right_layout.addWidget(top_right_top)
        top_right_layout.addWidget(top_right_bottom)

        # Bottom right section
        bottom_right_top = QWidget()
        bottom_right_bottom = QWidget()
        bottom_right_top.setStyleSheet("background-color: lightgoldenrodyellow;")
        bottom_right_bottom.setStyleSheet("background-color: lightgrey;")
        bottom_right_layout.addWidget(bottom_right_top)
        bottom_right_layout.addWidget(bottom_right_bottom)

        # Use QSplitter to manage the height distribution within each section
        left_splitter = QSplitter(Qt.Vertical)
        left_splitter.addWidget(top_left_layout.widgetAt(0))
        left_splitter.addWidget(bottom_left_layout.widgetAt(0))
        
        right_splitter = QSplitter(Qt.Vertical)
        right_splitter.addWidget(top_right_layout.widgetAt(0))
        right_splitter.addWidget(bottom_right_layout.widgetAt(0))
        
        # Add splitters to main layouts
        left_layout.addWidget(left_splitter)
        right_layout.addWidget(right_splitter)

        # Create layout containers for 3/10 and 2/10 width ratio
        main_left = QWidget()
        main_right = QWidget()
        
        main_left.setLayout(left_layout)
        main_right.setLayout(right_layout)

        # Add widgets to the main layout
        main_layout.addWidget(main_left, 3)
        main_layout.addWidget(main_right, 2)
        
        # Set the main layout for the main window
        self.setLayout(main_layout)
        self.setWindowTitle('Distributed Layout with Horizontal Split')
        self.resize(800, 600)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
