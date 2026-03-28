from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtGui import QPixmap

app = QApplication([])

window = QWidget()
window.resize(600, 400)


label = QLabel(window)
pixmap = QPixmap("C:/Users/mwhea/Bath hack/Screenshot 2026-03-28 132009.jpg")

# Scale image if you want
label.setPixmap(pixmap)
label.setScaledContents(False)  # image stretches with window
label.resize(950,800)

# Move the image inside the window
label.move(0,0)  # x=50, y=50

window.show()
app.exec()