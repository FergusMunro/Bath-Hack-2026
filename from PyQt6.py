from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtGui import QPixmap
import os


def getImagePath(imageName):
    path = os.getcwd()
    path = path + ("/Images/"+imageName)
    path = path.replace("\\","/")
    print(path)
    return path


app = QApplication([])

screen = app.primaryScreen()
geometry = screen.availableGeometry()
size = geometry.size()
width = geometry.width()
height = geometry.height()

window = QWidget()
window.resize(width, height)
window.setWindowTitle("Flight Cutter")

label = QLabel(window)
europeMap = QPixmap(getImagePath("Europe.jpg"))
# Scale image if you want
label.setPixmap(europeMap)
label.setScaledContents(False)  # image stretches with window
label.resize(int(width*0.8),int(height))

# Move the image inside the window
label.move(0,0)  # x=50, y=50

window.show()
app.exec()
