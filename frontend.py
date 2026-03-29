from tkinter import Menu

import numpy as np

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (
    QApplication,
    QPushButton,
    QScrollArea,
    QSlider,
    QWidget,
    QLabel,
    QLineEdit,
    QMenu,
    QWidgetAction,
    QVBoxLayout,
)
from PyQt6.QtGui import QIcon, QPainterPath, QPixmap, QPainter, QColor, QPen
from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QTimer, QPointF

import os
import sys
import random
import math

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
        self.setStyleSheet(
            "background-color:white; border:2px solid darkblue; border-radius:5px;"
        )
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
def sample_poisson_ms(lam):
    """Return a Poisson-distributed inter-arrival interval in milliseconds.
    lam is the average number of flights per second."""
    if lam <= 0:
        lam = 0.1
    interval_s = random.expovariate(lam)
    return max(500, int(interval_s * 1000))


class PlaneSprite(QWidget):
    """Transparent overlay that draws a cross-shaped plane and flies it along
    a quadratic Bezier arc between two city coordinates."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self._progress = 0.0
        self._p0 = QPointF(0, 0)
        self._p1 = QPointF(0, 0)  # Bezier control point
        self._p2 = QPointF(0, 0)
        self._angle = 0.0
        self.visible_plane = False

        # Timer-based animation: fires every 16 ms (~60 fps)
        self._duration_ms = 4000
        self._elapsed_ms = 0
        self._tick_ms = 16
        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(self._tick_ms)
        self._anim_timer.timeout.connect(self._tick)

    def fly(self, p0: QPointF, p2: QPointF):
        self._p0 = p0
        self._p2 = p2
        mx = (p0.x() + p2.x()) / 2
        my = (p0.y() + p2.y()) / 2
        self._p1 = QPointF(mx, my - 90)
        self._progress = 0.0
        self._elapsed_ms = 0
        self.visible_plane = True
        self._anim_timer.start()

    def _tick(self):
        self._elapsed_ms += self._tick_ms
        self._progress = min(1.0, self._elapsed_ms / self._duration_ms)
        self._update_angle()
        self.update()
        if self._progress >= 1.0:
            self._anim_timer.stop()
            self.visible_plane = False
            self.update()
            self.deleteLater()

    def _bezier_point(self, t) -> QPointF:
        u = 1.0 - t
        x = u * u * self._p0.x() + 2 * u * t * self._p1.x() + t * t * self._p2.x()
        y = u * u * self._p0.y() + 2 * u * t * self._p1.y() + t * t * self._p2.y()
        return QPointF(x, y)

    def _update_angle(self):
        t = max(0.001, min(0.999, self._progress))
        dt = 0.01
        a = self._bezier_point(t - dt)
        b = self._bezier_point(t + dt)
        self._angle = math.degrees(math.atan2(b.y() - a.y(), b.x() - a.x()))

    def paintEvent(self, event):
        if not self.visible_plane:
            return
        pos = self._bezier_point(self._progress)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.translate(pos)
        painter.rotate(self._angle)

        arm = 10
        thick = 4
        from PyQt6.QtGui import QPen

        pen = QPen(QColor(30, 30, 30))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(QColor("white"))
        # Fuselage
        painter.drawRect(-arm, -thick // 2, arm * 2, thick)
        # Wings
        painter.drawRect(-thick // 2, -arm, thick, arm * 2)
        painter.end()


class PlaneScheduler:
    """Drives PlaneSprite departures via a Poisson process.

    lambda_matrix: () -> float  — current average departures per second (from backend)
    locations_fn: () -> list[(x, y)]  — current pixel coords of cities
    """

    def __init__(self, parent_window, lambda_matrix, locations_fn):
        self._parent = parent_window  # Store the main window instead of a single sprite
        self._lambda_matrix = lambda_matrix / 100

        self._locations_fn = locations_fn
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._dispatch)

        self.fps = 15

    def updateLambdaMatrix(self, flightMatrix):
        self._lambda_matrix = flightMatrix / 100

    def start(self):
        self._timer.setSingleShot(False)  # repeating timer
        self._timer.start(int(1000 / self.fps))

    def stop(self):
        self._timer.stop()

    def _dispatch(self):
        locs = self._locations_fn()
        if len(locs) >= 2:
            for i in range(10):
                for j in range(10):
                    if i == j:
                        continue

                    prob = 1 - np.exp(-(self._lambda_matrix[i, j]) * (self.fps / 1000))
                    u = random.random()
                    if u < prob:
                        new_plane = PlaneSprite(self._parent)
                        new_plane.resize(self._parent.size())
                        new_plane.move(0, 0)

                        new_plane.stackUnder(self._parent.london)

                        new_plane.show()

                        new_plane.fly(QPointF(*locs[i]), QPointF(*locs[j]))


"""
   if len(locs) >= 2:
        # Randomly pick two distinct cities as origin (i) and destination (j)
        i, j = random.sample(range(len(locs)), 2)

        # Create a new plane sprite for this flight

    # Schedule the next plane dispatch based on this route
    self._schedule_next(i, j)
"""


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

        # Sliders
        self.sliders = []
        self.slider_labels = []

        # Marquee at the top
        self.marquee = Marquee(self, text="No cancelled flights yet.", speed=2)

        self.refreshButton = QPushButton("↻ Refresh Flights", self)

        # Plane sprite must sit above the map label but below city buttons
        # bring to top first...
        self.london.raise_()  # ...then raise all city buttons above it
        self.glasgow.raise_()
        self.amsterdam.raise_()
        self.berlin.raise_()
        self.paris.raise_()
        self.madrid.raise_()
        self.reykjavik.raise_()
        self.rome.raise_()
        self.prague.raise_()
        self.athens.raise_()

        self.flightData = backend.doAnalysis()

        # pass values to overlay
        self.overlay.buttonList = self.buttonList
        self.overlay.availableFlights = self.flightData.totalFlights

        self.scheduler = PlaneScheduler(
            parent_window=self,  # Pass the MainWindow as the parent
            lambda_matrix=self.flightData.getFlightMatrix(),
            locations_fn=lambda: self.overlay.locations,
        )
        self.scroll = (
            QScrollArea()
        )  # Scroll Area which contains the widgets, set as the centralWidget
        self.widget = QWidget()  # Widget that contains the collection of Vertical Box
        self.vbox = QVBoxLayout()
        self.initUI()

    def keyPressEvent(self, event):
        if (
            event.key() == Qt.Key.Key_D
            and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
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

        # Sliders setup
        slider_names = ["Profit", "Minimise disruption", "Prioritise essential"]
        for name in slider_names:
            slider_label = QLabel(name, self)
            slider_label.setStyleSheet("color: black; font-weight: bold;")
            slider = QSlider(Qt.Orientation.Horizontal, self)
            slider.setRange(0, 100)
            slider.setValue(50)
            slider.valueChanged.connect(
                lambda val, l=slider_label, name=name: l.setText(f"{name}: {val}")
            )
            self.sliders.append(slider)
            self.slider_labels.append(slider_label)

        # Create capital city buttons
        i = 0
        for city_button in [
            self.london,
            self.glasgow,
            self.amsterdam,
            self.berlin,
            self.paris,
            self.madrid,
            self.reykjavik,
            self.rome,
            self.prague,
            self.athens,
        ]:
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
            self.buttonList.append(
                Buttons(confirm_btn, line_edit, fuelPrice, menu, city_label.text())
            )

            layout.addWidget(city_label)
            layout.addWidget(line_edit)
            layout.addWidget(fuelPrice)
            layout.addWidget(confirm_btn)

            action = QWidgetAction(self)
            action.setDefaultWidget(container)
            menu.addAction(action)

            confirm_btn.clicked.connect(
                lambda _, c=city_label.text(), le=line_edit, fp=fuelPrice, m=menu: self.update_all(
                    c, le, fp, m
                )
            )

            city_button.setMenu(menu)

        # Sidebar labels
        self.button1T = QLabel("Flights Cancelled:", self)
        self.button2T = QLabel("Total Revenue Lost:", self)
        self.button3T = QLabel(self)
        self.button4T = QLabel(self)
        self.button3T.setFixedWidth(int(self.width() * 0.5))

        for boxes in [self.button1T, self.button2T, self.button3T, self.button4T]:
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
        self.widget.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self.widget.setLayout(self.vbox)
        self.scroll.setWidget(self.widget)
        self.scroll.setStyleSheet("""
            QScrollBar:vertical { background: #f0f0f0; width: 12px; border-radius: 6px;}
            QScrollBar::handle:vertical { background: #555; min-height: 30px; border-radius: 6px;}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { background: #aaa; height: 12px;}
        """)

        # Initial flight data
        self.update_flights()
        # Refresh button (bottom-right)
        self.refreshButton.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)
        self.refreshButton.clicked.connect(self.update_flights)
        self.refreshButton.raise_()

        # Trigger the first sizing manually
        self.showMaximized()
        self.scheduler.start()

    def resizeEvent(self, event):
        width = self.width()
        height = self.height()

        # Background map
        self.label.resize(int(width * 0.75), height)
        self.label.move(0, 0)

        # Update capitals
        for city in [
            self.london,
            self.glasgow,
            self.amsterdam,
            self.berlin,
            self.paris,
            self.madrid,
            self.reykjavik,
            self.rome,
            self.prague,
            self.athens,
        ]:
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

        # Sliders bottom right
        slider_width = int(width * 0.2)
        slider_height = int(height * 0.03)
        padding = 10
        for i, (slider, label) in enumerate(zip(self.sliders, self.slider_labels)):
            y = height - (len(self.sliders) - i) * (slider_height + padding + 15)
            label.move(width - int(slider_width / 1.3), y)
            slider.setGeometry(
                width - int(slider_width * 1.1) - padding,
                y + 15,
                slider_width,
                slider_height,
            )
            label.setText(label.text() + ": " + str(slider.value()))

        rect_x = int(width * 0.777)
        rect_y = int(height * 0.08)
        self.button1T.move(rect_x, rect_y - int(height * 0.05))
        self.button2T.move(rect_x, rect_y + int(height * 0.6))
        self.button3T.move(rect_x, rect_y + int(height * 0.65))
        self.button4T.move(int(width * 0.4), int(height*0.95))
        self.scroll.setGeometry(
            int(width * 0.77), int(height * 0.08), int(width * 0.22), int(height * 0.6)
        )

        # Overlay
        self.overlay.resize(self.label.size())
        self.overlay.move(self.label.pos())
        self.overlay.locations = [
            (int(width * 0.235), int(height * 0.52)),
            (int(width * 0.212), int(height * 0.39)),
            (int(width * 0.298), int(height * 0.515)),
            (int(width * 0.4), int(height * 0.515)),
            (int(width * 0.255), int(height * 0.615)),
            (int(width * 0.135), int(height * 0.8)),
            (int(width * 0.12), int(height * 0.09)),
            (int(width * 0.387), int(height * 0.81)),
            (int(width * 0.41), int(height * 0.588)),
            (int(width * 0.55), int(height * 0.9)),
        ]
        self.overlay.update()

        # Marquee
        self.marquee.setFixedWidth(int(width * 0.75))
        self.marquee.move(0, 0)
        self.marquee.raise_()

        btn_w, btn_h = int(width * 0.15), int(height * 0.06)
        self.refreshButton.setFixedSize(btn_w, btn_h)
        self.refreshButton.move(int(width * 0.01), int(height * 0.93))
        self.refreshButton.raise_()

    def update_all(self, city, line_edit, fuelPrice, menu):
        try:
            num = data.cities.index(city)
            data.fuel_availability[num] = float(line_edit.text())
            data.fuel_cost[num] = float(fuelPrice.text())
        except:
            pass
        menu.close()

    def update_flights(self):
        backend.updateProfitImportance(self.sliders[0].value())
        backend.updateReplacementImportance(self.sliders[1].value())
        backend.updateDemandImportance(self.sliders[2].value())
        flightData = backend.doAnalysis()
        clear_layout(self.vbox)

        # Sidebar cancelled flights
        flight_texts = []
        remainingFlights = []
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
                        flight_texts.append(
                            f"{data.cities[i]} <> {data.cities[j]}: {int(value)} cancelled"
                        )

                        flight_texts.append(
                            f"{data.cities[i]} <> {data.cities[j]}: {int(value)} cancelled"
                        )

        for i in range(len(flightData.totalFlights)):
            for j in range(len(flightData.totalFlights[i])):
                if i < j:
                    remaining = flightData.getNumFlights(i, j)
                    remainingFlights.append(
                        f"{data.cities[i]} <> {data.cities[j]}: {int(remaining)} remaining"
                    )
        self.button3T.setText(str(int(flightData.getLostProfit())))
        self.button4T.setText("Total People Affected: " + str(int(flightData.getTotalAffected())))
        marquee_text = (
            " | ".join(flight_texts) if flight_texts else "No cancelled flights yet."
        )
        marquee_text = marquee_text +" " + " | ".join(remainingFlights) if remainingFlights else "No remaining flights."
        self.marquee.updateText(marquee_text)
        # Refresh the rate source so plane frequency reflects new fuel data
        self.flightData = flightData
        self.scheduler.updateLambdaMatrix(self.flightData.getFlightMatrix())
        self.overlay.BackEndData = self.flightData


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
        self.BackEndData = backend.doAnalysis()

    def paintEvent(self, event):
        if len(self.locations) < 5:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)

        for i in range(len(self.locations)):
            x1, y1 = self.locations[i]
            for j in range(i + 1, len(self.locations)):
                painter.setPen(QColor("green"))
                firstCity = self.buttonList[i].city
                secondCity = self.buttonList[j].city

                cancelled = self.BackEndData.getCancelledFlights(firstCity, secondCity)

                if self.availableFlights[i][j] == 0:
                    opacity = 0.1
                else:
                    opacity = (
                        self.availableFlights[i][j] - cancelled
                    ) / self.availableFlights[i][j]

                if opacity < 0:
                    opacity = 0

                painter.setOpacity(opacity)
                if opacity < 0.75 and opacity > 0.5:
                    painter.setPen(QColor("yellow"))

                elif opacity <= 0.5 and opacity > 0.25:
                    painter.setPen(QColor("red"))

                elif opacity <= 0.25:
                    painter.setPen(QColor("black"))

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

