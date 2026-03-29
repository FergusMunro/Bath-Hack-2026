from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QPushButton, QScrollArea, QWidget, QLabel, QLineEdit, QMenu, QWidgetAction, QVBoxLayout
from PyQt6.QtGui import QIcon, QPainterPath, QPixmap, QPainter, QColor
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
import os
import sys

from dino import startGame
import backend
import data

# ------------------- Marquee Widget -------------------
class Marquee(QWidget):
    def __init__(self, parent=None, text="", speed=2):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.text = text
        self.speed = speed
        self.label = QLabel(self)
        self.label.setStyleSheet("color:black; font-weight:bold; font-size:16px;")
        self.setStyleSheet("background-color:white; border:2px solid darkblue; border-radius:5px;")
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.scroll)
        self.timer.start(30)
        self.offset = 0
        self.updateText(text)

    def scroll(self):
        self.offset -= self.speed
        if self.offset + self.label.width() < 0:
            self.offset = self.width()
        self.label.move(self.offset, 0)

    def updateText(self, text):
        self.text = text
        self.label.setText(text)
        self.label.adjustSize()
        self.offset = self.width()
        self.label.move(self.offset, 0)

# ------------------- Main Window -------------------
class MainWindow(QWidget):
    buttonList = list()

    def __init__(self):
        super().__init__()
        # Base UI elements
        self.label = QLabel(self)
        self.rect = QLabel(self)
        self.london = QPushButton(self)
        self.glasgow = QPushButton(self)
        self.amsterdam = QPushButton(self)
        self.berlin = QPushButton(self)
        self.paris = QPushButton(self)
        self.madrid = QPushButton(self)
        self.reykjavik = QPushButton(self)
        self.rome = QPushButton(self)
        self.prague = QPushButton(self)
        self.athens = QPushButton(self)
        self.overlay = Overlay(self)
        self.overlay.stackUnder(self.london)
        self.scroll = QScrollArea()
        self.widget = QWidget()
        self.vbox = QVBoxLayout()

        # Marquee at the top
        self.marquee = Marquee(self, text="No cancelled flights yet.", speed=2)
        self.initUI()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_D and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.dino_game = startGame()

    def getImagePath(self, imageName):
        path = os.getcwd()
        path = path + ("/Images/" + imageName)
        path = path.replace("\\", "/")
        return path

    def initUI(self):
        self.setWindowTitle("Flight Cutter")
        self.setWindowIcon(QIcon(self.getImagePath("Plane.ico")))

        # Background map
        pixmap = QPixmap(self.getImagePath("Europe.jpg"))
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)

        # White sidebar
        self.rect.setStyleSheet("background-color: white;")

        # Create capital city buttons
        i = 0
        for city_button in [self.london, self.glasgow, self.amsterdam, self.berlin, self.paris,
                            self.madrid, self.reykjavik, self.rome, self.prague, self.athens]:
            city_button.setStyleSheet(""" 
                QPushButton {background-color: red; border: none;}
                QPushButton::menu-indicator {image: none; width: 0px;}
            """)
            menu = QMenu(self)
            container = QWidget()
            container.setFixedSize(180, 150)
            layout = QVBoxLayout(container)

            line_edit = QLineEdit()
            line_edit.setPlaceholderText(str(int(data.fuel_availability[i])))
            fuelPrice = QLineEdit()
            fuelPrice.setPlaceholderText(str(int(data.fuel_cost[i])))
            city_label = QLabel(data.cities[i])
            i += 1
            confirm_btn = QPushButton("Confirm")
            self.buttonList.append(Buttons(confirm_btn, line_edit, fuelPrice, menu, city_label.text()))

            layout.addWidget(city_label)
            layout.addWidget(line_edit)
            layout.addWidget(fuelPrice)
            layout.addWidget(confirm_btn)

            action = QWidgetAction(self)
            action.setDefaultWidget(container)
            menu.addAction(action)

            confirm_btn.clicked.connect(
                lambda _, c=city_label.text(), le=line_edit, fp=fuelPrice, m=menu: self.update_all(c, le, fp, m)
            )

            city_button.setMenu(menu)

        # Sidebar labels
        self.button1T = QLabel("Flights Cancelled:", self)
        self.button2T = QLabel("Total Revenue Lost:", self)
        self.button3T = QLabel(self)
        self.button3T.setFixedWidth(int(self.width() * 0.5))

        for boxes in [self.button1T, self.button2T, self.button3T]:
            boxes.setStyleSheet("""
                color: black;
                font-size: 22px;
                font-weight: bold;
            """)

        # Sidebar scroll
        self.scroll.setParent(self)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.widget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.widget.setLayout(self.vbox)
        self.scroll.setWidget(self.widget)
        self.scroll.setStyleSheet("""
            QScrollBar:vertical { background: #f0f0f0; width: 12px; border-radius: 6px;}
            QScrollBar::handle:vertical { background: #555; min-height: 30px; border-radius: 6px;}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { background: #aaa; height: 12px;}
        """)

        # Initial flight data
        self.update_flights()

        self.showMaximized()

    def resizeEvent(self, event):
        width = self.width()
        height = self.height()

        # Background map
        self.label.resize(int(width * 0.75), height)
        self.label.move(0, 0)

        # Update capitals
        for city in [self.london, self.glasgow, self.amsterdam, self.berlin, self.paris,
                     self.madrid, self.reykjavik, self.rome, self.prague, self.athens]:
            city.resize(int(width * 0.01), int(width * 0.01))
        self.london.move(int(width * 0.235), int(height * 0.52))
        self.glasgow.move(int(width * 0.212), int(height * 0.39))
        self.amsterdam.move(int(width * 0.298), int(height * 0.515))
        self.berlin.move(int(width * 0.4), int(height * 0.515))
        self.paris.move(int(width * 0.255), int(height * 0.615))
        self.madrid.move(int(width * 0.135), int(height * 0.8))
        self.reykjavik.move(int(width * 0.12), int(height * 0.09))
        self.rome.move(int(width * 0.387), int(height * 0.81))
        self.prague.move(int(width * 0.41), int(height * 0.588))
        self.athens.move(int(width * 0.55), int(height * 0.9))

        # Sidebar rectangle
        self.rect.resize(int(width * 0.25), height)
        self.rect.move(int(width * 0.75), 0)

        rect_x = int(width * 0.777)
        rect_y = int(height * 0.08)
        self.button1T.move(rect_x, rect_y - int(height * 0.05))
        self.button2T.move(rect_x, rect_y + int(height * 0.6))
        self.button3T.move(rect_x, rect_y + int(height * 0.65))
        self.scroll.setGeometry(int(width * 0.77), int(height * 0.08), int(width * 0.22), int(height * 0.6))

        # Overlay
        self.overlay.resize(self.label.size())
        self.overlay.move(self.label.pos())
        self.overlay.locations = [
            (int(width * 0.235), int(height * 0.52)), (int(width * 0.212), int(height * 0.39)),
            (int(width * 0.298), int(height * 0.515)), (int(width * 0.4), int(height * 0.515)),
            (int(width * 0.255), int(height * 0.615)), (int(width * 0.135), int(height * 0.8)),
            (int(width * 0.12), int(height * 0.09)), (int(width * 0.387), int(height * 0.81)),
            (int(width * 0.41), int(height * 0.588)), (int(width * 0.55), int(height * 0.9))
        ]
        self.overlay.update()

        # Marquee
        self.marquee.setFixedWidth(int(width * 0.75))
        self.marquee.move(0, 0)
        self.marquee.raise_()

    def update_all(self, city, line_edit, fuelPrice, menu):
        try:
            num = data.cities.index(city)
            data.fuel_availability[num] = float(line_edit.text())
            data.fuel_cost[num] = float(fuelPrice.text())
        except:
            pass
        self.update_flights()
        menu.close()

    def update_flights(self):
        flightData = backend.doAnalysis()
        clear_layout(self.vbox)

        # Sidebar cancelled flights
        flight_texts = []
        for i in range(len(flightData.cancelledFlights)):
            for j in range(len(flightData.cancelledFlights[i])):
                if i < j:
                    value = flightData.cancelledFlights[j][i]
                    if value > 0:
                        obj = QLabel(
                            f"<b>{data.cities[i]} &lt;&gt; {data.cities[j]}: {int(value)} flights</b> <br>"
                            f"{int(flightData.getDivertedToTrain(data.cities[i], data.cities[j]))} people were diverted to train<br>"
                            f"{int(flightData.getUnableToFindTransport(data.cities[i], data.cities[j]))} people were unable to find transport<br>"
                        )
                        obj.setWordWrap(True)
                        self.vbox.addWidget(obj)
                        flight_texts.append(f"{data.cities[i]} <> {data.cities[j]}: {int(value)} cancelled")

        self.button3T.setText(str(int(flightData.getLostProfit())))
        marquee_text = " | ".join(flight_texts) if flight_texts else "No cancelled flights yet."
        self.marquee.updateText(marquee_text)


def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()


# ------------------- Overlay -------------------
class Overlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.locations = []

    def paintEvent(self, event):
        if len(self.locations) < 5:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QColor("red"))
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)

        for i in range(len(self.locations)):
            x1, y1 = self.locations[i]
            for j in range(i + 1, len(self.locations)):
                x2, y2 = self.locations[j]
                mx = (x1 + x2) / 2
                my = (y1 + y2) / 2
                path = QPainterPath()
                path.moveTo(x1, y1)
                path.quadTo(mx, my - 80, x2, y2)
                painter.drawPath(path)


# ------------------- Buttons -------------------
class Buttons:
    def __init__(self, button, fuelVolume, fuelCost, menu, city):
        self.button = button
        self.fuelVolume = fuelVolume
        self.fuelCost = fuelCost
        self.menu = menu
        self.city = city


# ------------------- Run -------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())