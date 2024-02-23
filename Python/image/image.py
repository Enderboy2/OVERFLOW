import cv2
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
import numpy as np
import sys
import os
import datetime

rtsp_username = "admin"
rtsp_password = "overflow123"
width = 1600  # Adjusted to accommodate dual feeds
height = 600

class CameraController:
    def __init__(self, root, screen_width, screen_height, test_mode=False):
        self.root = root
        self.root.title("Camera Control")

        # Calculate feed dimensions based on screen size
        self.feed_width = int(screen_width / 2) - 10  # Half the screen width - padding
        self.feed_height = int(screen_height * 0.75)  # 75% of screen height

        self.root.geometry(f"{screen_width}x{screen_height}")
        self.test_mode = test_mode

        self.cam_no = 4
        self.cam = self.create_camera(str(self.cam_no))
        self.lock = threading.Lock()

        self.lower_hsv = np.array([0, 0, 0])
        self.upper_hsv = np.array([0, 0, 0])

        self.create_widgets()
        self.is_running = True
        self.update_image_thread = threading.Thread(target=self.update_image)
        self.update_image_thread.start()

        self.root.bind("<Key>", self.handle_keypress)

    def handle_keypress(self, event):
        # Check for "t" key press to not interfere with screenshot functionality
        if event.char == "t":
            self.take_screenshot(event)
        elif event.char.isdigit() and not self.test_mode:  # Ensure we're not in test mode and key is a digit
            new_cam_no = int(event.char)
            if 1 <= new_cam_no <= 4:  # Limit the camera number to 1-4
                self.switch_camera(new_cam_no)

    def switch_camera(self, new_cam_no):

        if self.test_mode:
            print("Camera switching is disabled in test mode.")
            return
        # Stop the current feed
        with self.lock:
            self.is_running = False
            if self.cam is not None:
                self.cam.release()  # Release the current camera
            self.update_image_thread.join()  # Wait for the thread to finish

        # Update the camera number
        self.cam_no = new_cam_no
        # Create a new camera capture object
        self.cam = self.create_camera(str(self.cam_no))

        # Restart the image update thread
        if self.cam is not None:
            self.is_running = True
            self.update_image_thread = threading.Thread(target=self.update_image)
            self.update_image_thread.start()
        else:
            # Handle the case where the camera could not be connected
            messagebox.showerror("Error", f"Cannot connect to camera {new_cam_no}")

    def create_camera(self, channel):
        if self.test_mode:
            return cv2.VideoCapture(0)  # Use the default camera

        rtsp = f"rtsp://{rtsp_username}:{rtsp_password}@192.168.1.1:554/Streaming/channels/{channel}01"
        cap = cv2.VideoCapture(rtsp)
        if not cap.isOpened():
            messagebox.showerror("Error", f"Cannot connect to camera {channel}")
            return None
        return cap

    def create_widgets(self):
        self.canvas_original = tk.Canvas(self.root, width=self.feed_width, height=self.feed_height)
        self.canvas_original.pack(side=tk.LEFT)

        self.canvas_processed = tk.Canvas(self.root, width=self.feed_width, height=self.feed_height)
        self.canvas_processed.pack(side=tk.RIGHT)

        self.canvas_original.bind("<Button-1>", self.select_color)  # Bind left mouse click to color selection

    def update_image(self):
        while self.is_running:
            if self.cam is not None:
                with self.lock:
                    success, frame = self.cam.read()
                if success:
                    self.display_frame(frame, self.canvas_original, process=False)
                    processed_frame = self.remove_water(frame)
                    self.display_frame(processed_frame, self.canvas_processed, process=True)
            cv2.waitKey(1)

    def display_frame(self, frame, canvas, process):
        if process:
            frame = self.remove_water(frame)
        frame = cv2.resize(frame, (800, 480))
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        img_tk = ImageTk.PhotoImage(image=img)
        canvas.img_tk = img_tk  # Save reference to avoid garbage collection
        canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)

    def remove_water(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_hsv, self.upper_hsv)
        result = cv2.bitwise_and(frame, frame, mask=~mask)
        return result

    def select_color(self, event):
        x, y = event.x, event.y
        with self.lock:
            _, frame = self.cam.read()
            if frame is not None:
                hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                color = hsv_frame[y, x]
                # Create a range around the selected color
                self.lower_hsv = np.array([max(color[0] - 10, 0), max(color[1] - 40, 0), max(color[2] - 40, 0)])
                self.upper_hsv = np.array([min(color[0] + 10, 255), min(color[1] + 40, 255), min(color[2] + 40, 255)])

    def take_screenshot(self, event):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # Base paths for original and processed screenshots
        original_path = os.path.join("screenshots", "original")
        processed_path = os.path.join("screenshots", "processed")
        # Ensure the directories exist
        os.makedirs(original_path, exist_ok=True)
        os.makedirs(processed_path, exist_ok=True)

        with self.lock:
            success, frame = self.cam.read()
            if success:
                # Save the original frame
                cv2.imwrite(os.path.join(original_path, f"{timestamp}.png"), frame)
                # Process and save the processed frame
                processed_frame = self.remove_water(frame)
                cv2.imwrite(os.path.join(processed_path, f"{timestamp}.png"), processed_frame)
                print(timestamp)


if __name__ == "__main__":
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    test_mode = "-test" in sys.argv
    app = CameraController(root, screen_width, screen_height,test_mode=test_mode)
    root.mainloop()
