import threading
import time
from communication import Communication
from joystick_controller import JoystickController
import pygame
import sys
import json

class ROVController:
    def __init__(self):
        self.joystick_controller = JoystickController()
        self.communication = Communication()
        self.stop_threads = False
        self.combined_data = ["000000", 0,[0, 0, 0, 0, 0, 0],[0,0,0,0]]
        self.imu_data = ""
        self.strg = ""
        self.prev_strg = ""

    # Inside the motion_detection_thread in main.py
    def motion_detection_thread(self):
        self.write_and_print()
        while not self.stop_threads:
            if not pygame.joystick.get_count():
                self.communication.send_command("*0,0,0,0,0,0,0,0,0,0/")
            for event in pygame.event.get():
                if event.type == (pygame.JOYAXISMOTION or pygame.JOYHATMOTION):
                    axis_values = [
                        self.joystick_controller.joystick.get_axis(i)
                        for i in range(self.joystick_controller.joystick.get_numaxes())
                    ]
                    hat_values = self.joystick_controller.joystick.get_hat(0)
                    self.combined_data[:3] = self.joystick_controller.detect_changed_motion(
                        axis_values, hat_values
                    )
                    
                    
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

                self.prev_strg = self.strg
                self.strg = str("*"+str(self.combined_data[2][0])+ ","+str(self.combined_data[2][1])+ ","+str(self.combined_data[2][2])+ ","+str(self.combined_data[2][3])+ ","+str(self.combined_data[2][4])+ ","+str(self.combined_data[2][5]) + "," + str(self.combined_data[3][0])+","+ str(self.combined_data[3][1])+","+ str(self.combined_data[3][2])+","+ str(self.combined_data[3][3])+"/")
                #print(str(self.combined_data[2][0]))
                if(self.strg != self.prev_strg):
                    self.write_and_print()
            time.sleep(0.1)

    def write_and_print(self):
        # Write combined data to a text file
        with open('config.json', 'w') as json_file:
            json.dump(self.combined_data, json_file)
        #strg = "*" + ','.join(map(str, self.combined_data[2])) + ',' + ','.join(map(str, self.combined_data[3])) + "/"
        self.communication.send_command(self.strg)

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

        except KeyboardInterrupt:
            self.stop_threads = True
            motion_thread.join()
            imu_thread.join()
            print("Exiting...")


if __name__ == "__main__":
    rov_controller = ROVController()
    rov_controller.run()
