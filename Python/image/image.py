import cv2
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
import time

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
        self.lock = threading.Lock()

        self.create_widgets()
        self.is_running = True
        self.update_image_thread = threading.Thread(target=self.update_image)
        self.update_image_thread.start()

    def create_camera(self, channel):
        rtsp = f"rtsp://{rtsp_username}:{rtsp_password}@192.168.1.1:554/Streaming/channels/{channel}01"
        cap = cv2.VideoCapture(rtsp)
        if not cap.isOpened():
            messagebox.showerror("Error", f"Cannot connect to camera {channel}")
            return None
        return cap

    def create_widgets(self):
        self.canvas = tk.Canvas(self.root, width=800, height=480)
        self.canvas.pack()

        next_button = ttk.Button(self.root, text="Next", command=self.next_camera)
        next_button.pack(side=tk.RIGHT, padx=10)

        previous_button = ttk.Button(self.root, text="Previous", command=self.previous_camera)
        previous_button.pack(side=tk.RIGHT, padx=10)

        screenshot_button = ttk.Button(self.root, text="Take Screenshot", command=self.take_screenshot)
        screenshot_button.pack(side=tk.LEFT, padx=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_image(self):
        while self.is_running:
            if self.cam is not None:
                with self.lock:
                    success, current_cam = self.cam.read()
                if success:
                    current_cam = cv2.resize(current_cam, (800, 480))
                    img = Image.fromarray(cv2.cvtColor(current_cam, cv2.COLOR_BGR2RGB))
                    img_tk = ImageTk.PhotoImage(image=img)
                    self.canvas.img_tk = img_tk  # Save reference to avoid garbage collection
                    self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
            time.sleep(1/30)  # Control frame rate

    def switch_camera(self, cam_no):
        with self.lock:
            if self.cam is not None:
                self.cam.release()
            self.cam = self.create_camera(str(cam_no))

    def next_camera(self):
        print("Next Button Pressed")
        self.cam_no = (self.cam_no + 1) % 5 or 1
        self.switch_camera(self.cam_no)

    def previous_camera(self):
        print("Previous Button Pressed")
        self.cam_no = (self.cam_no - 1) % 5 or 4
        self.switch_camera(self.cam_no)

    def take_screenshot(self):
        with self.lock:
            success, current_cam = self.cam.read()
            if success:
                screenshot_path = f"screenshot_{self.cam_no}.png"
                cv2.imwrite(screenshot_path, current_cam)
                messagebox.showinfo("Screenshot", f"Screenshot saved to {screenshot_path}")

    def on_close(self):
        self.is_running = False
        self.update_image_thread.join()
        if self.cam is not None:
            self.cam.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraController(root)
    root.mainloop()
