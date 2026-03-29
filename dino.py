import sys
import random
import os
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QTimer, QRect


class DinoRunner(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_game()

    def init_ui(self):
        # Window setup
        self.setFixedSize(600, 200)
        self.setWindowTitle('Dino Runner')
        self.setStyleSheet("background-color: #f7f7f7;")
        self.show()

    def init_game(self):
        # Dinosaur Properties
        self.dino_x = 50
        self.dino_y = 150
        self.dino_w = 20
        self.dino_h = 40
        self.dino_dy = 0          # Velocity
        self.gravity = 0.8        # Downward pull
        self.jump_power = -12     # Upward force
        self.is_grounded = True

        # Game State
        self.obstacles = []
        self.score = 0
        self.game_speed = 5
        self.game_over = False
        self.frames = 0

        # Start the Game Loop (~60 Frames Per Second)
        if hasattr(self, 'timer'):
            self.timer.stop()
        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(16)

    def keyPressEvent(self, event):
        # Handle Jumping and Restarting
        if event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Up):
            if self.game_over:
                self.init_game() # Restart the game
            elif self.is_grounded:
                self.dino_dy = self.jump_power
                self.is_grounded = False

    def game_loop(self):
        if self.game_over:
            return

        self.frames += 1

        # 1. Update Physics (Gravity)
        self.dino_dy += self.gravity
        self.dino_y += self.dino_dy

        # Ground Collision Detection
        ground_y = 170
        if self.dino_y + self.dino_h >= ground_y:
            self.dino_y = ground_y - self.dino_h
            self.dino_dy = 0
            self.is_grounded = True

        # 2. Handle Obstacles (Spawning)
        # Randomly spawn a cactus based on the frame count
        if self.frames % random.randint(60, 110) == 0:
            # QRect(x, y, width, height)
            self.obstacles.append(QRect(600, 130, 20, 40))

        # 3. Move Obstacles & Check Collisions
        # Create a bounding box for the Dino
        dino_rect = QRect(int(self.dino_x), int(self.dino_y), self.dino_w, self.dino_h)
        
        # Iterate over a copy of the list so we can safely remove items
        for obs in list(self.obstacles):
            obs.moveLeft(obs.left() - int(self.game_speed))
            
            # Check Collision
            if dino_rect.intersects(obs):
                self.game_over = True

            # Remove obstacles that go off-screen and add to score
            if obs.right() < 0:
                self.obstacles.remove(obs)
                self.score += 10

        # 4. Gradually Increase Difficulty
        if self.frames % 500 == 0 and self.game_speed < 12:
            self.game_speed += 0.5

        # Trigger a UI repaint
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw Ground Line
        painter.setPen(QColor("#535353"))
        painter.drawLine(0, 170, self.width(), 170)

        # Draw the Dinosaur (Dark Grey)
        painter.fillRect(int(self.dino_x), int(self.dino_y), self.dino_w, self.dino_h, QColor("#535353"))

        # Draw the Obstacles (Orange)
        for obs in self.obstacles:
            painter.fillRect(obs, QColor("#ff5722"))

        # Draw the Score
        painter.setFont(QFont("Courier New", 14, QFont.Weight.Bold))
        painter.setPen(QColor("#535353"))
        painter.drawText(450, 30, f"Score: {self.score}")

        # Draw Game Over Text
        if self.game_over:
            painter.setFont(QFont("Courier New", 24, QFont.Weight.Bold))
            painter.drawText(210, 90, "GAME OVER")
            painter.setFont(QFont("Courier New", 12))
            painter.drawText(200, 120, "Press Space to Restart")

def startGame():
    # Initialize the PyQt6 Application
    game_window = DinoRunner()
    game_window.show()
    return game_window 

if __name__ == "__main__":
    startGame()