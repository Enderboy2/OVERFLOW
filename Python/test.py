import tkinter as tk
from tkinter import messagebox
import pygame
import serial.tools.list_ports
import json

class ROVControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("ROV Control Panel")

        self.check_status()

    def check_status(self):
        pygame.init()
        pygame.joystick.init()

        controllers_connected = pygame.joystick.get_count() > 0
        arduino_port = self.detect_arduino()

        if controllers_connected and arduino_port:
            self.show_ready_status()
            self.save_config({"arduino_port": arduino_port})
        else:
            self.show_not_ready_status()

        # Schedule the next check after 1 second (1000 milliseconds)
        self.root.after(1000, self.check_status)

    def detect_arduino(self):
        available_ports = [port.device for port in serial.tools.list_ports.comports()]

        for port_description in available_ports:
            try:
                with serial.Serial(port_description, timeout=1) as test_serial:
                    test_serial.write(b"Hello")
                    response = test_serial.readline().decode('utf-8').strip()

                    if "Arduino" in response:
                        return port_description
            except (serial.SerialException, ValueError):
                pass

        return None

    def show_ready_status(self):
        # Code for the "Ready" state, including enabling the Start button
        # ...
        print("ready")
        pass
    def show_not_ready_status(self):
        # Code for the "Not Ready" state, including disabling the Start button
        # ...
        pass
    def save_config(self, config_data):
        with open("config.json", "w") as config_file:
            json.dump(config_data, config_file)

    def start_rov(self):
        try:
            with open("config.json", "r") as config_file:
                config_data = json.load(config_file)
                arduino_port = config_data.get("arduino_port")

                if arduino_port:
                    # Start the rov_logic.py file with the Arduino port as an argument
                    import subprocess
                    subprocess.Popen(["python", "rov_logic.py", arduino_port])
                else:
                    messagebox.showerror("Error", "Arduino port not found. Make sure it's connected.")
        except FileNotFoundError:
            messagebox.showerror("Error", "Config file not found. Run the controller check first.")


root = tk.Tk()
app = ROVControlPanel(root)
root.mainloop()
