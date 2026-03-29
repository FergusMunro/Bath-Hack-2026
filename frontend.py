from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QPushButton, QScrollArea, QWidget, QLabel, QLineEdit, QMenu, QWidgetAction, QVBoxLayout
from PyQt6.QtGui import QIcon, QPainterPath, QPixmap, QPainter, QColor, QPen
from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QTimer, QPointF

import os
import sys
import random
import math

from dino import startGame
import backend
import backendDataClass
import data
import backendDataClass

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
        self._p1 = QPointF(0, 0)   # Bezier control point
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
        x = u*u*self._p0.x() + 2*u*t*self._p1.x() + t*t*self._p2.x()
        y = u*u*self._p0.y() + 2*u*t*self._p1.y() + t*t*self._p2.y()
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

    lambda_fn: () -> float  — current average departures per second (from backend)
    locations_fn: () -> list[(x, y)]  — current pixel coords of cities
    """

    def __init__(self, parent_window, lambda_fn, locations_fn):
        self._parent = parent_window  # Store the main window instead of a single sprite
        self._lambda_fn = lambda_fn
        self._locations_fn = locations_fn
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._dispatch)

    def start(self):
        self._schedule_next(0, 1)   # arbitrary indices for the very first interval

    def stop(self):
        self._timer.stop()

    def _schedule_next(self, i=0, j=1):
        interval_ms = sample_poisson_ms(self._lambda_fn(i, j))
        self._timer.start(interval_ms)

    def _dispatch(self):
        locs = self._locations_fn()
        if len(locs) >= 2:
            i, j = random.sample(range(len(locs)), 2)
            
            # Create a brand new plane for this specific flight
            new_plane = PlaneSprite(self._parent)
            new_plane.resize(self._parent.size())
            new_plane.move(0, 0)
            
            # Stack it under a UI element so it doesn't block city button clicks
            new_plane.stackUnder(self._parent.london) 
            
            new_plane.show()
            new_plane.fly(QPointF(*locs[i]), QPointF(*locs[j]))
            
        self._schedule_next(i, j)


class MainWindow(QWidget):

    buttonList  = list()

    def __init__(self):
        super().__init__()
        # Initialize your labels as class variables so resizeEvent can see them
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

        # Plane sprite must sit above the map label but below city buttons
                                             # bring to top first...
        self.london.raise_()                 # ...then raise all city buttons above it
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
        self.scheduler = PlaneScheduler(
            parent_window=self,  # Pass the MainWindow as the parent
            lambda_fn=self.flightData.getNumFlights,
            locations_fn=lambda: self.overlay.locations,
        )
        self.scroll = QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.widget = QWidget()                 # Widget that contains the collection of Vertical Box
        self.vbox = QVBoxLayout() 
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
        
        # Setup the image label
        pixmap = QPixmap(self.getImagePath("Europe.jpg"))
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)

        # Setup the white rectangle
        self.rect.setStyleSheet("background-color: white;")

        # Setup capitals
        i=0
        for city_button in [self.london, self.glasgow, self.amsterdam, self.berlin, self.paris, 
                            self.madrid,self.reykjavik,self.rome,self.prague,self.athens]:
            city_button.setStyleSheet(""" 
                                      QPushButton {background-color: red; border: none;}
                                      QPushButton::menu-indicator {image: none; width: 0px;}
                                      """)
            menu = QMenu(self)
            
            # 1. Create a container widget to hold BOTH the input and the button
            container = QWidget()
            container.setFixedSize(180, 150)
            layout = QVBoxLayout(container)
            
            
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(str(int(data.fuel_availability[i])))

            fuelPrice = QLineEdit()
            fuelPrice.setPlaceholderText(str(int(data.fuel_cost[i])))
            
            city = QLabel(data.cities[i])
            i=i+1
            
            confirm_btn = QPushButton("Confirm")
            
            self.buttonList.append(Buttons(confirm_btn,line_edit,fuelPrice,menu,city.text()))

            layout.addWidget(city)
            layout.addWidget(line_edit)
            layout.addWidget(fuelPrice)
            layout.addWidget(confirm_btn)
            
            # 2. Add the container to the menu
            action = QWidgetAction(self)
            action.setDefaultWidget(container)
            menu.addAction(action)

            # 3. Connect the button - now it won't close the whole window
            confirm_btn.clicked.connect(
                lambda _, c=city.text(), le=line_edit, fp=fuelPrice, m=menu: self.update_all(c, le, fp, m)
            )
               
            city_button.setMenu(menu)

        # Sidebar stuff
        self.button1T = QLabel("Flights Cancelled:",self)
        self.button2T = QLabel("Total Revenue Lost:",self)
        self.button3T = QLabel(self)
        self.button3T.setFixedWidth(int(self.width() * 0.5))  

        for boxes in [self.button1T,self.button2T,self.button3T]:
            boxes.setStyleSheet("""
            color: black;
            font-size: 22px;
            font-weight: bold;
            """)

        '''for boxes in [self.button1,self.button2,self.button3]:
            boxes.setStyleSheet("""
            background-color: lightyellow;   /* background color */
            color: darkblue;                 /* text color */
            border: 2px solid gray;          /* border color and thickness */
            border-radius: 5px;              /* rounded corners */
            """)'''
        
       # Sidebar scroll area
        # Sidebar scroll area
        self.scroll.setParent(self)  # make it a child of MainWindow
        self.scroll.setGeometry(int(self.width()*0.77), int(self.height()*0.15), int(self.width()*0.22), int(self.height()*0.7))
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)

        # Container widget inside scroll area
        self.widget.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, 
            QtWidgets.QSizePolicy.Policy.Expanding  # let it grow vertically
        )
        self.widget.setLayout(self.vbox)
        self.scroll.setWidget(self.widget)
        self.scroll.setStyleSheet("""
        QScrollBar:vertical {
            background: #f0f0f0;
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background: #555;
            min-height: 30px;
            border-radius: 6px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            background: #aaa;
            height: 12px;
        }
        """)
        flightData = backend.doAnalysis()
        clear_layout(self.vbox)
        for i in range(len(flightData.cancelledFlights)):
            for j in range(len(flightData.cancelledFlights[i])):
             if i<j:
              value = flightData.cancelledFlights[j][i]
              if value > 0:
               object = QLabel(f"{data.cities[i]} <> {data.cities[j]}: {int(value)}")
               self.vbox.addWidget(object)
        self.button3T.setText(str(flightData.getLostProfit()))
        self.scroll.show()

        # Trigger the first sizing manually
        self.showMaximized()
        self.scheduler.start()

    def resizeEvent(self, event):
        # This function now actually moves/resizes your labels 
        # whenever the window changes size
        width = self.width()
        height = self.height()

        # Update Image Label (75% width)
        self.label.resize(int(width * 0.75), height)
        self.label.move(0, 0)

        #update capitals
        for city in [self.london, self.glasgow, self.amsterdam, self.berlin, self.paris, 
                            self.madrid,self.reykjavik,self.rome,self.prague,self.athens]:
            city.resize(int(width*0.01),int(width*0.01))
        self.london.move(int(width*0.235),int(height*0.52))
        self.glasgow.move(int(width*0.212),int(height*0.39))
        self.amsterdam.move(int(width*0.298),int(height*0.515))
        self.berlin.move(int(width*0.4),int(height*0.515))
        self.paris.move(int(width*0.255),int(height*0.615))

        self.madrid.move(int(width*0.135),int(height*0.8))
        self.reykjavik.move(int(width*0.12),int(height*0.09))
        self.rome.move(int(width*0.387),int(height*0.81))
        self.prague.move(int(width*0.41),int(height*0.588))
        self.athens.move(int(width*0.55),int(height*0.9))
        

        # Update White Rectangle (25% width)
        self.rect.resize(int(width * 0.25), height)
        self.rect.move(int(width * 0.75), 0)

        rect_x = int(width * 0.777)
        rect_y = int(height*0.08)
        '''for boxes in [self.button1,self.button2,self.button3]:
            boxes.resize(int(width*0.2),int(height*0.06))
            self.button1.move(rect_x,rect_y)
            self.button2.move(rect_x,rect_y+int(height*0.12))
            self.button3.move(rect_x,rect_y+int(height*0.24))'''

        for boxes in [self.button1T]:
            self.button1T.move(rect_x,rect_y-int(height*0.05))
            self.button2T.move(rect_x,rect_y+int(height*0.8))
            self.button3T.move(rect_x,rect_y+int(height*0.85))
        
        self.overlay.resize(self.label.size())
        self.overlay.move(self.label.pos())
        self.overlay.locations = [
            (int(self.width()*0.235), int(self.height()*0.52)),   # London
            (int(self.width()*0.212), int(self.height()*0.39)),   # Glasgow
            (int(self.width()*0.298), int(self.height()*0.515)),  # Amsterdam
            (int(self.width()*0.4),   int(self.height()*0.515)),  # Berlin
            (int(self.width()*0.255), int(self.height()*0.615)),  # Paris
            (int(self.width()*0.135), int(self.height()*0.8)),   # Madrid
            (int(self.width()*0.12), int(self.height()*0.09)),   # reykjavik
            (int(self.width()*0.387), int(self.height()*0.81)),   # rome
            (int(self.width()*0.41), int(self.height()*0.588)),   # prague
            (int(self.width()*0.55), int(self.height()*0.9)),   # athens
        ]
        self.overlay.update()
        self.scroll.setGeometry(int(width*0.77), int(height*0.08), int(width*0.22), int(height*0.8))

    def update_all(self, city, line_edit, fuelPrice, menu):
            flightData = backend.doAnalysis()
            num = flightData.cityDict[city]

            # Convert QLineEdit text to float safely
            try:
                data.fuel_availability[num] = float(line_edit.text())
            except ValueError:
                data.fuel_availability[num] = 0.0

            try:
                data.fuel_cost[num] = float(fuelPrice.text())
            except ValueError:
                data.fuel_cost[num] = 0.0

            # Re-run analysis
            flightData = backend.doAnalysis()

            # Clear old labels
            clear_layout(self.vbox)

            # Add new labels
            for i in range(len(flightData.cancelledFlights)):
                for j in range(len(flightData.cancelledFlights[i])):
                    if i < j:
                        value = flightData.cancelledFlights[j][i]
                        if value > 0:
                            obj = QLabel(f"{data.cities[i]} <> {data.cities[j]}: {int(value)}")
                            self.vbox.addWidget(obj)

            # Update lost profit
            self.button3T.setText(str(int(flightData.getLostProfit())))

            # Refresh the rate source so plane frequency reflects new fuel data
            self.flightData = flightData
            self.scheduler._lambda_fn = self.flightData.getNumFlights

            menu.close()
    
def clear_layout(layout):
     while layout.count():
        item = layout.takeAt(0)   # remove item from layout
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()  # safely delete widget

class Overlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        # This will be filled by MainWindow.resizeEvent
        self.locations = []  

        self.start = 0
        self.span = 120

    def paintEvent(self, event):
        if len(self.locations) < 5:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QColor("red"))
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)

        # Draw lines between every pair of cities
        for i in range(len(self.locations)):
            x1, y1 = self.locations[i]
            for j in range(i+1, len(self.locations)):
                x2, y2 = self.locations[j]

                # Midpoint
                mx = (x1 + x2) / 2
                my = (y1 + y2) / 2

                # Raise midpoint upward to create a curve
                cx = mx
                cy = my - 80   # adjust curvature

                path = QPainterPath()
                path.moveTo(x1, y1)
                path.quadTo(cx, cy, x2, y2)

                painter.drawPath(path)


class Buttons:
    def __init__(self, button, fuelVolume, fuelCost, menu, city):
        self.button = button
        self.fuelVolume = fuelVolume
        self.fuelCost = fuelCost
        self.menu = menu
        self.city = city

    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())