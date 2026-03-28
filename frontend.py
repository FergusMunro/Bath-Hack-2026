from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt
import os
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Initialize your labels as class variables so resizeEvent can see them
        self.label = QLabel(self)
        self.rect = QLabel(self)
        self.london = QLabel(self)
        self.glasgow = QLabel(self)
        self.amsterdam = QLabel(self)
        self.berlin = QLabel(self)
        self.paris = QLabel(self)
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

        # Setup capitals
        self.london.setStyleSheet((f" background-color: red;"))
        self.glasgow.setStyleSheet((f" background-color: red;"))
        self.amsterdam.setStyleSheet((f" background-color: red;"))
        self.berlin.setStyleSheet((f" background-color: red;"))
        self.paris.setStyleSheet((f" background-color: red;"))

        # Create a text input field
        self.input_field1 = QLineEdit(self)
        self.input_field1.setPlaceholderText("Glasgow Fuel Amount")

        self.input_field2 = QLineEdit(self)
        self.input_field2.setPlaceholderText("London Fuel Amount")

        self.input_field3 = QLineEdit(self)
        self.input_field3.setPlaceholderText("Amsterdam Fuel Amount")

        self.input_field4 = QLineEdit(self)
        self.input_field4.setPlaceholderText("Paris Fuel Amount")

        self.input_field5 = QLineEdit(self)
        self.input_field5.setPlaceholderText("Berlin Fuel Amount")

        #limit how small the window can be resized to
        self.setMinimumSize(800, 600)
        
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

        #update capitals
        self.london.resize(int(width*0.01),int(width*0.01))
        self.london.move(int(width*0.235),int(height*0.52))
        self.glasgow.resize(int(width*0.01),int(width*0.01))
        self.glasgow.move(int(width*0.212),int(height*0.39))
        self.amsterdam.resize(int(width*0.01),int(width*0.01))
        self.amsterdam.move(int(width*0.298),int(height*0.515))
        self.berlin.resize(int(width*0.01),int(width*0.01))
        self.berlin.move(int(width*0.4),int(height*0.515))
        self.paris.resize(int(width*0.01),int(width*0.01))
        self.paris.move(int(width*0.255),int(height*0.615))
        

        # Update White Rectangle (25% width)
        self.rect.resize(int(width * 0.25), height)
        self.rect.move(int(width * 0.75), 0)

        rect_x = int(width * 0.75)
        self.input_field1.resize(250, 40)
        self.input_field1.move(rect_x + 20, 50)
        self.input_field2.resize(250, 40)
        self.input_field2.move(rect_x + 20, 100)
        self.input_field3.resize(250, 40)
        self.input_field3.move(rect_x + 20, 150)
        self.input_field4.resize(250, 40)
        self.input_field4.move(rect_x + 20, 200)
        self.input_field5.resize(250, 40)
        self.input_field5.move(rect_x + 20, 250)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())