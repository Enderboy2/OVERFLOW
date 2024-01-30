import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

rtsp_username = "admin"
rtsp_password = "overflow123"
width = 800
height = 600

class CameraController:
    def __init__(self, root):
        self.root = root
        self.root.title("Camera Control")
        self.root.geometry(f"{width}x{height}")

        self.cam_no = 1
        self.cam = self.create_camera(str(self.cam_no))

        self.create_widgets()

    def create_camera(self, channel):
        rtsp = f"rtsp://{rtsp_username}:{rtsp_password}@192.168.1.1:554/Streaming/channels/{channel}01"
        cap = cv2.VideoCapture(rtsp)  
        return cap

    def create_widgets(self):
        self.canvas = tk.Canvas(self.root, width=800, height=480)
        self.canvas.pack()

        self.update_image()

        next_button = ttk.Button(self.root, text="Next", command=self.next_camera)
        next_button.pack(side=tk.RIGHT, padx=10)

        previous_button = ttk.Button(self.root, text="Previous", command=self.previous_camera)
        previous_button.pack(side=tk.RIGHT, padx=10)

        screenshot_button = ttk.Button(self.root, text="Take Screenshot", command=self.take_screenshot)
        screenshot_button.pack(side=tk.LEFT, padx=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_image(self):
        success, current_cam = self.cam.read()
        dim = (width, height)
        full_frame = cv2.resize(current_cam, dim, interpolation=cv2.INTER_AREA)
        img = Image.fromarray(cv2.cvtColor(full_frame, cv2.COLOR_BGR2RGB))
        img_tk = ImageTk.PhotoImage(image=img)
        self.canvas.img_tk = img_tk  # Save reference to avoid garbage collection
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        self.root.after(10, self.update_image)

    def next_camera(self):
        print("Next Button Pressed")
        self.cam_no = (self.cam_no + 1) % 5 or 1
        del self.cam
        self.cam = self.create_camera(str(self.cam_no))

    def previous_camera(self):
        print("Previous Button Pressed")
        self.cam_no = (self.cam_no - 1) % 5 or 4
        del self.cam
        self.cam = self.create_camera(str(self.cam_no))

    def take_screenshot(self):
        success, current_cam = self.cam.read()
        if success:
            # Perform task on the captured frame (example: grayscale conversion)
            gray_frame = cv2.cvtColor(current_cam, cv2.COLOR_BGR2GRAY)

            # Save the screenshot to a local folder
            screenshot_path = f"screenshot_{self.cam_no}.png"
            cv2.imwrite(screenshot_path, current_cam)
            print(f"Screenshot saved to {screenshot_path}")

    def on_close(self):
        self.cam.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraController(root)
    root.mainloop()
