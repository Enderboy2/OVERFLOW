import threading
import time
from communication import Communication
from joystick_controller import JoystickController
import pygame
import sys

class ROVController:
    def __init__(self):
        self.joystick_controller = JoystickController()
        self.communication = Communication()
        self.stop_threads = False
        self.combined_data = [0, 0, 0, 0]
        self.prev_combined_data = [0, 0, 0, 0]
        self.imu_data = ""

    # Inside the motion_detection_thread in main.py
    def motion_detection_thread(self):
        while not self.stop_threads:
            for event in pygame.event.get():
                if event.type == (pygame.JOYAXISMOTION or pygame.JOYHATMOTION):
                    axis_values = [
                        self.joystick_controller.joystick.get_axis(i)
                        for i in range(self.joystick_controller.joystick.get_numaxes())
                    ]
                    hat_values = self.joystick_controller.joystick.get_hat(0)
                    motion = self.joystick_controller.detect_changed_motion(
                        axis_values, hat_values
                    )
                    if motion[0] != "00000":
                        self.combined_data[0] = motion[0]
                        self.combined_data[1] = motion[1]
                        self.combined_data[2] = motion[2]
                        if self.combined_data != self.prev_combined_data:
                            self.prev_combined_data = self.combined_data[:]
                            self.write_and_print()
                    elif self.prev_combined_data[0] != "00000":
                        self.combined_data[0] = motion[0]
                        self.combined_data[1] = motion[1]
                        self.combined_data[2] = motion[2]
                        self.prev_combined_data = self.combined_data[:]
                        self.write_and_print()
                elif event.type == pygame.JOYBUTTONDOWN:
                    button_states = [
                        self.joystick_controller.joystick.get_button(i)
                        for i in range(
                            self.joystick_controller.joystick.get_numbuttons()
                        )
                    ]
                    self.combined_data[3] = self.joystick_controller.get_buttons(
                        button_states
                    )
                    self.prev_combined_data = self.combined_data[:]
                    self.write_and_print()
            time.sleep(0.1)

    def write_and_print(self):
        # Write combined data to a text file
        with open("data.txt", "w") as file:
            for data in self.combined_data:
                file.write(f"{data}\n")
        #self.communication.send_command(",".join(map(str, self.combined_data)))
        print(",".join(map(str, self.combined_data)))

    def imu_data_thread(self):
        while not self.stop_threads:
            imuData = self.communication.receive_data()
            if imuData:
                # Process the received IMU data if needed
                print("Received IMU data:", imuData.decode())
                self.imu_data = imuData
            time.sleep(0.5)  # Adjust sleep time as needed

    def run(self):
        motion_thread = threading.Thread(target=self.motion_detection_thread)
        imu_thread = threading.Thread(target=self.imu_data_thread)

        try:
            motion_thread.start()
            #imu_thread.start()

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
