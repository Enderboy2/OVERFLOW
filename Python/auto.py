import cv2
import numpy as np
import threading
import sys
from communication import Communication
import time

com = Communication()

# Color range for detection
lower_red = np.array([0, 100, 100])
upper_red = np.array([10, 255, 255])
frameHSV = None
colorSelected = False
refPt = []
desired_location = None
desired_contour_size = 1000
resolution = None

rtsp_username = "admin"
rtsp_password = "overflow123"

searching = False
search_thread = None
last_known_direction = None

# Define initial trackbar positions
initial_trackbar_vals = {
    "Lower H": lower_red[0],
    "Lower S": lower_red[1],
    "Lower V": lower_red[2],
    "Upper H": upper_red[0],
    "Upper S": upper_red[1],
    "Upper V": upper_red[2],
    "Desired Size": desired_contour_size,
}

def on_trackbar_change(value):
    pass

class ThreadedCamera:
    def __init__(self, source):
        self.capture = cv2.VideoCapture(source)
        self.ret, self.frame = self.capture.read()
        self.stopped = False
        self.resolution = (int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        print(f"Video resolution: {self.resolution}")
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        while not self.stopped:
            ret, frame = self.capture.read()
            with self.lock:
                self.ret = ret
                self.frame = frame

    def read(self):
        with self.lock:
            return self.ret, self.frame

    def stop(self):
        self.stopped = True
        self.capture.release()

def create_camera(channel, test_mode=False):
    if test_mode:
        source = 0
    else:
        rtsp = f"rtsp://{rtsp_username}:{rtsp_password}@192.168.1.1:554/Streaming/channels/{channel}01"
        source = rtsp
    return ThreadedCamera(source)

def click_and_select_color(event, x, y, flags, param):
    global frameHSV, colorSelected, refPt, lower_red, upper_red, desired_location
    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x, y)]
        pixel_value = frameHSV[y, x]
        hue = pixel_value[0]
        saturation = pixel_value[1]
        value = pixel_value[2]

        sensitivity = 15
        lower_red = np.array([max(hue - sensitivity, 0), max(saturation - sensitivity, 0), max(value - sensitivity, 0)])
        upper_red = np.array([min(hue + sensitivity, 180), min(saturation + sensitivity, 255), min(value + sensitivity, 255)])
        
        cv2.setTrackbarPos("Lower H", "Frame", lower_red[0])
        cv2.setTrackbarPos("Lower S", "Frame", lower_red[1])
        cv2.setTrackbarPos("Lower V", "Frame", lower_red[2])
        cv2.setTrackbarPos("Upper H", "Frame", upper_red[0])
        cv2.setTrackbarPos("Upper S", "Frame", upper_red[1])
        cv2.setTrackbarPos("Upper V", "Frame", upper_red[2])

        colorSelected = True
    elif event == cv2.EVENT_RBUTTONDOWN:
        desired_location = (x, y)
        print(f"Desired location: {desired_location}")

def start_searching():
    global searching, last_known_direction
    print("Search thread started")
    search_steps = [
        ("*0,70,0,0,70,0,0,0,0,0/", 2),  # Up for 2 seconds
        ("*70,0,-70,70,0,-70,0,0,0,0/", 2),  # Rotate left for 2 seconds
        ("*-70,0,70,-70,0,70,0,0,0,0/", 2)  # Rotate right for 2 seconds
    ]

    for command, duration in search_steps:
        if not searching:  # Stop the search if the object is found
            break
        print(f"Sending command: {command}")
        com.send_command(command)
        time.sleep(duration)

    searching = False
    last_known_direction = None  # Reset last known direction after search
    print("Search thread finished")

if __name__ == "__main__":
    test_mode = "-test" in sys.argv
    cam_no = "2"
    cap = create_camera(cam_no, test_mode=test_mode)
    resolution = cap.resolution

    cv2.namedWindow("Frame")
    cv2.setMouseCallback("Frame", click_and_select_color)

    for trackbar_name, initial_val in initial_trackbar_vals.items():
        cv2.createTrackbar(trackbar_name, "Frame", initial_val, 255 if trackbar_name != "Desired Size" else 10000, on_trackbar_change)

    prev_mov = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (600, 480))
        frameBlurred = cv2.GaussianBlur(frame, (5, 5), 0)
        frameHSV = cv2.cvtColor(frameBlurred, cv2.COLOR_BGR2HSV)

        # Your existing color selection and masking logic...

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.erode(frameHSV, kernel, iterations=2)
        mask = cv2.dilate(mask, kernel, iterations=2)
        mask = cv2.inRange(mask, lower_red, upper_red)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)

            # Find the center of the contour
            cx = x + w // 2
            cy = y + h // 2

            searching = False  # Object found, stop searching
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Example action based on position and desired location
            if desired_location:
                desired_x, desired_y = desired_location  
                dx, dy = desired_x - cx, desired_y - cy  # Difference in x and y coordinates
                distance = np.sqrt(dx**2 + dy**2)  # Euclidean distance

                movement_commands = [0,0]
                if distance > 45:  # Example threshold for considering movement
                    movement_commands[0] = "L" if cx < desired_x - 20 else "R" if cx > desired_x + 20 else "0"
                    movement_commands[1] = "U" if cy > desired_y + 20 else "D" if cy < desired_y - 20 else "0"

                    if movement_commands != prev_mov:
                        print(movement_commands)
                        if movement_commands[0] == "0":
                            if movement_commands[1] == "U":
                                com.send_command("*0,70,0,0,70,0,0,0,0,0/")
                            elif movement_commands[1] == "D":
                                com.send_command("*0,-70,0,0,-70,0,0,0,0,0/")
                        else:
                            if movement_commands[0] == "L":
                                com.send_command("*70,0,-70,70,0,-70,0,0,0,0/")
                            elif movement_commands[0] == "R":
                                com.send_command("*-70,0,70,-70,0,70,0,0,0,0/")    
                        prev_mov = movement_commands

            last_known_direction = 'left' if cx < resolution[0] // 2 else 'right'

        elif not contours and not searching:
            searching = True
            search_thread = threading.Thread(target=start_searching)
            search_thread.start()

        cv2.imshow("Frame", frame)
        cv2.imshow("Mask", mask)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("s"):
            if not searching:
                print("Starting search...")
                searching = True
                search_thread = threading.Thread(target=start_searching)
                search_thread.start()

    cap.stop()
    cv2.destroyAllWindows()
