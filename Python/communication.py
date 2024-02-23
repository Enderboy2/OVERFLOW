import threading
import serial
import time

class Communication:
    def __init__(self):
        # Initialize communication components
        self.port = self.read()[0].strip()
        # Initialize communication components only if the port is not empty
        if self.port:
            try:
                self.arduino = serial.Serial(port=self.port, baudrate=115200, timeout=.1)
            except:
                print("An exception occurred")
        else:
            print("Port is empty. Communication components not initialized.")

    def send_command(self, command):
        # Send to STATION
        try:
            self.arduino.write(bytes(command, 'utf-8'))
            print("sent -> ",command)
            time.sleep(0.05)
        except:
            pass


    def receive_data(self):
        # Replace this with the actual logic to get IMU data from your ROV's serial connection
        data = self.arduino.readline()
        return data
        
    def write(self,combined_data):
        with open("data.txt", "w") as file:
            for data in combined_data:
                file.write(f"{data}")

    def read(self):
        with open('data.txt') as f:
            lines = f.readlines()
        return lines
    def read_port_from_file(self, file_path, n):
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                if 0 < n <= len(lines):
                    return lines[n-1].strip()  # Adjusting for 0-based indexing
                else:
                    print(f"Invalid line number {n}.")
                    return None
        except FileNotFoundError:
            print(f"File not found: {file_path}.")
            return None


