from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtGui import QIcon, QPixmap
import os
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Initialize your labels as class variables so resizeEvent can see them
        self.label = QLabel(self)
        self.rect = QLabel(self)
        self.initUI()

    def getImagePath(self, imageName):
        path = os.getcwd()
        path = path + ("/Images/" + imageName)
        path = path.replace("\\", "/")
        return path

    def initUI(self):
        self.setWindowTitle("Flight Cutter")
        self.setWindowIcon(QIcon(self.getImagePath("Plane.ico")))
        
        # Setup the image label
        pixmap = QPixmap(self.getImagePath("Europe.jpg"))
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)

        # Setup the white rectangle
        self.rect.setStyleSheet("background-color: white;")
        
        # Trigger the first sizing manually
        self.showMaximized()

    def resizeEvent(self, event):
        # This function now actually moves/resizes your labels 
        # whenever the window changes size
        width = self.width()
        height = self.height()

        # Update Image Label (75% width)
        self.label.resize(int(width * 0.75), height)
        self.label.move(0, 0)

        # Update White Rectangle (25% width)
        self.rect.resize(int(width * 0.25), height)
        self.rect.move(int(width * 0.75), 0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())