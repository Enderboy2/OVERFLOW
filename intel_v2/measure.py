import tkinter as tk
from tkinter import messagebox
import cv2
import numpy as np

# Load the depth image
depth_image = cv2.imread("received_depth_image.png", cv2.IMREAD_UNCHANGED)

# Function to calculate distance between two points
def calculate_distance(point1, point2):
    depth1 = depth_image[point1[1], point1[0]]
    depth2 = depth_image[point2[1], point2[0]]
    distance = np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2 + (depth1 - depth2)**2)
    return distance

# GUI for selecting points
class DepthImageApp:
    def __init__(self, root):
        self.root = root
        self.points = []
        self.canvas = tk.Canvas(root, width=depth_image.shape[1], height=depth_image.shape[0])
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        if len(self.points) < 2:
            self.points.append((event.x, event.y))
            self.canvas.create_oval(event.x-2, event.y-2, event.x+2, event.y+2, fill="red")
            if len(self.points) == 2:
                distance = calculate_distance(self.points[0], self.points[1])
                messagebox.showinfo("Distance", f"Distance between points: {distance:.2f} units")
                self.points = []

# Run the GUI
root = tk.Tk()
app = DepthImageApp(root)
root.mainloop()