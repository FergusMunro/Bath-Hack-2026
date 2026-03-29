
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QPushButton, QScrollArea, QWidget, QLabel, QLineEdit, QMenu, QWidgetAction, QVBoxLayout
from PyQt6.QtGui import QIcon, QPainterPath, QPixmap, QPainter, QColor
from PyQt6 import QtCore
from PyQt6.QtCore import Qt

import os
import sys

from dino import startGame
import backend
import backendDataClass
import data
import backendDataClass

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