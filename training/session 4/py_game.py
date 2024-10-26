import pygame
from PyQt5.QtWidgets import *

# Initialize PyQt5 GUI
app = QApplication([])
window = QWidget()

# Create a label to display the direction of movement
label = QLabel("Direction: None")

layout = QVBoxLayout()
layout.addWidget(label)
window.setLayout(layout)

def update_direction(direction):
    label.setText(f"Direction: {direction}")

# Show the PyQt5 window
window.show()

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((400, 300))

# Main loop (Expected to fail)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                label.setText("Direction: left")
                print("Moving Left")
            elif event.key == pygame.K_RIGHT:
                label.setText("Direction: right")
                print("Moving Right")
            elif event.key == pygame.K_UP:
                label.setText("Direction: up")
                print("Moving Up")
            elif event.key == pygame.K_DOWN:
                label.setText("Direction: down")
                print("Moving Down")

# Clean up and exit
pygame.quit()
app.exec_()

