import pygame
import threading
import time

# Placeholder function for getting IMU data from serial
def get_imu_data():
    # Replace this with the actual logic to get IMU data from your ROV's serial connection
    return {"roll": 0.0, "pitch": 0.0, "yaw": 0.0}

class JoystickController:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        # Check if any joystick is available
        if pygame.joystick.get_count() == 0:
            print("No joystick found.")
            pygame.quit()
            exit()

        # Get the first joystick
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        print(f"Initialized joystick: {self.joystick.get_name()}")

        self.prev_motion = None
        self.motion_start_time = None

    def is_joystick_at_rest(self, axis_values, rest_threshold=0.1):
        # Check if all axis values are within the rest threshold
        return all(abs(val) < rest_threshold for val in axis_values)

    def detect_motion(self, axis_values, threshold=0.5, rest_threshold=0.1):
        # Check if the joystick is at rest
        if self.is_joystick_at_rest(axis_values, rest_threshold):
            return "000"

        # Check for any motion (single or combined)
        left_right = axis_values[0]
        forward_backward = axis_values[1]
        rotation = axis_values[2]

        motion = ""

        if abs(forward_backward) > threshold:
            if forward_backward > 0:
                motion += "B"
            else:
                motion += "F"
        else:
            motion += "0"

        if abs(left_right) > threshold:
            if left_right > 0:
                motion += "R"
            else:
                motion += "L"
        else:
            motion += "0"

        if abs(rotation) > 0.2:
            if rotation > 0:
                motion += "R"
            else:
                motion += "L"
        else:
            motion += "0"

        return motion

    def detect_changed_motion(self, axis_values, threshold=0.1, rest_threshold=0.1):
        current_motion = self.detect_motion(axis_values, threshold, rest_threshold)
        if current_motion != self.prev_motion:
            self.prev_motion = current_motion
            if current_motion != "000":
                # Record the start time when the motion begins
                self.motion_start_time = time.time()
            return current_motion
        else:
            # If the joystick returns to rest, reset the start time
            if self.is_joystick_at_rest(axis_values, rest_threshold):
                self.motion_start_time = None
            return None

    def get_speed(self, axis_values):
        # Calculate speed based on the maximum axis value
        return max(abs(val) for val in axis_values)

    def get_and_clear_prev_motion(self):
        prev_motion = self.prev_motion
        self.prev_motion = None
        return prev_motion

    def update_prev_motion(self, motion):
        self.prev_motion = motion

class Communication:
    def __init__(self):
        # Initialize communication components
        self.serial_lock = threading.Lock()

    def send_command(self, command):
        # Send commands to the ROV if it's different from the previous motion
        with self.serial_lock:
            print(f"Sending Command: {command}")

    def receive_imu_data(self):
        # Replace this with the actual logic to get IMU data from your ROV's serial connection
        with self.serial_lock:
            imu_data = get_imu_data()
        return imu_data

class ROVController:
    def __init__(self):
        self.joystick_controller = JoystickController()
        self.communication = Communication()
        self.stop_threads = False

    def motion_detection_thread(self):
        while not self.stop_threads:
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    axis_values = [self.joystick_controller.joystick.get_axis(i) for i in range(self.joystick_controller.joystick.get_numaxes())]
                    detected_motion = self.joystick_controller.detect_changed_motion(axis_values)
                    if detected_motion:
                        speed = self.joystick_controller.get_speed(axis_values)
                        # Write motion and speed to a text file
                        with open("data.txt", "w") as file:
                            file.write(f"Motion: {detected_motion}, Speed: {speed}\n")

                        self.communication.send_command(detected_motion)
            time.sleep(0.01)  # Adjust sleep time as needed

    def imu_data_thread(self):
        while not self.stop_threads:
            imu_data = self.communication.receive_imu_data()
            time.sleep(0.1)  # Adjust sleep time as needed

    def run(self):
        motion_thread = threading.Thread(target=self.motion_detection_thread)
        imu_thread = threading.Thread(target=self.imu_data_thread)

        try:
            motion_thread.start()
            imu_thread.start()

            while True:
                pass  # Add any main thread logic if needed

        except KeyboardInterrupt:
            self.stop_threads = True
            motion_thread.join()
            imu_thread.join()
            print("Exiting...")

if __name__ == "__main__":
    rov_controller = ROVController()
    rov_controller.run()