import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import serial.tools.list_ports
import time
import os
import json 

class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ROV Controller")
        self.root.geometry("600x400")
        self.root.minsize(500, 400)  # Set a minimum size
        self.stop = True
        self.c = 0
        self.auto_status = False
        self.image_status = False
        # Styles
        bg_color = "#35424a"
        label_color = "#FFFFFF"
        font_style = ("Helvetica", 14)

        # Header Label
        header_label = tk.Label(self.root, text="OVERFLOW", font=("Helvetica", 20, "bold"), fg=label_color, bg=bg_color)
        header_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")

        # Port Label
        self.port_label = tk.Label(self.root, text="Select Port:", font=font_style, fg=label_color, bg=bg_color)
        self.port_label.grid(row=1, column=0, pady=5, padx=10, sticky="w")

        # Port Dropdown
        self.available_ports = self.get_available_ports()
        self.selected_port = tk.StringVar()
        self.port_combobox = ttk.Combobox(self.root, textvariable=self.selected_port, values=self.available_ports)
        self.port_combobox.grid(row=1, column=1, pady=5, padx=10, sticky="w")

        # Start Button
        self.start_button = tk.Button(self.root, text="Start", command=self.start_rov, font=font_style, fg=label_color, bg="#5C8374")
        self.start_button.grid(row=2, column=0, pady=5, padx=10, sticky="w")

        # Stop Button
        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_rov, font=font_style, fg=label_color, bg="#A63232", state=tk.DISABLED)
        self.stop_button.grid(row=2, column=1, pady=5, padx=10, sticky="w")
        4
        # Restart Button
        self.restart_button = tk.Button(self.root, text="Restart", command=self.restart_rov, font=font_style, fg=label_color, bg="#FFA500", state=tk.DISABLED)
        self.restart_button.grid(row=2, column=2, pady=5, padx=10, sticky="w")

        # Motion Label
        self.motion_label = tk.Label(self.root, text="Motion ->", font=font_style, fg=label_color, bg=bg_color)
        self.motion_label.grid(row=3, column=0, pady=5, padx=10, sticky="w")

        # Speed Label
        self.speed_label = tk.Label(self.root, text="Speed ->", font=font_style, fg=label_color, bg=bg_color)
        self.speed_label.grid(row=4, column=0, pady=5, padx=10, sticky="w")

        # Speed Progress Bar
        self.speed_progress = ttk.Progressbar(self.root, length=200, mode="determinate", style="TProgressbar")
        self.speed_progress.grid(row=4, column=1, pady=5, padx=10, sticky="w")

        # Grippers Indicator
        self.grippers_indicator1 = tk.Label(self.root, text="", font=font_style, fg=label_color, bg=bg_color)
        self.grippers_indicator1.grid(row=5, column=0, pady=5, padx=10, sticky="w")
        self.grippers_indicator2 = tk.Label(self.root, text="", font=font_style, fg=label_color, bg=bg_color)
        self.grippers_indicator2.grid(row=5, column=1, pady=5, padx=10, sticky="w")
        self.grippers_indicator3 = tk.Label(self.root, text="", font=font_style, fg=label_color, bg=bg_color)
        self.grippers_indicator3.grid(row=5, column=2, pady=5, padx=10, sticky="w")
        self.grippers_indicator4 = tk.Label(self.root, text="", font=font_style, fg=label_color, bg=bg_color)
        self.grippers_indicator4.grid(row=5, column=3, pady=5, padx=10, sticky="w")

        # IMU Label
        self.imu_label = tk.Label(self.root, text="IMU Data:", font=font_style, fg=label_color, bg=bg_color)
        self.imu_label.grid(row=7, column=0, pady=5, padx=10, sticky="w")

        # Buttons
        self.auto_button = tk.Button(self.root, text="Start Auto", command=self.start_auto, font=font_style, fg=label_color, bg="#5C8374")
        self.auto_button.grid(row=7, column=1, pady=5, padx=10, sticky="w")

        self.image_button = tk.Button(self.root, text="Start Image", command=self.start_image, font=font_style, fg=label_color, bg="#5C8374")
        self.image_button.grid(row=7, column=2, pady=5, padx=10, sticky="w")

    def start_auto(self):
        if not self.auto_status:
            try:
                self.auto = subprocess.Popen(["python", "./image/auto.py",])
                print("image started")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start auto: {e}")
            self.auto_status = True
            self.auto_button.config(text="Stop Auto")
        else:
            self.auto.terminate()
            time.sleep(2)  # Wait for 2 seconds to give the process time to terminate
            if self.auto.poll() is None:  # If .poll() returns None, the process is still running
                print("auto did not terminate, killing it.")
                self.auto.kill()
            else:
                print("auto terminated gracefully.")
            self.auto_status = False
            self.image_button.config(text="Start Auto")

    def start_image(self):
        if not self.image_status:
            try:
                self.image = subprocess.Popen(["python", "./image/image.py",])
                print("image started")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start image: {e}")
            self.image_status = True
            self.image_button.config(text="Stop Image")
        else:
            self.image.terminate()
            time.sleep(2)  # Wait for 2 seconds to give the process time to terminate
            if self.image.poll() is None:  # If .poll() returns None, the process is still running
                print("image did not terminate, killing it.")
                self.image.kill()
            else:
                print("image terminated gracefully.")
            self.image_status = False
            self.image_button.config(text="Start Image")

    def get_available_ports(self):
        # Get a list of available ports
        ports = [port.device for port in serial.tools.list_ports.comports()]
        return ports

    def start_rov(self):
        selected_port = self.selected_port.get()
        if not selected_port:
            messagebox.showerror("Error", "Please select a port.")
            return

        # Start the ROV with the selected port
        with open("data.txt", "w") as file:
                file.write(f"{selected_port}\n")
        try:
            self.main = subprocess.Popen(["python", "main.py", selected_port])
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.restart_button.config(state=tk.NORMAL)
            self.stop = False
            self.run()
            print("runned")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start ROV: {e}")

    def stop_rov(self):
        # Stop the ROV
        # Add any necessary logic to stop the ROV (e.g., sending a stop command)
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.restart_button.config(state=tk.DISABLED)

        # Clear GUI data
        self.motion_label.config(text="Motion ->", bg="#35424a", fg="#FFFFFF")
        self.speed_label.config(text="Speed ->", bg="#35424a", fg="#FFFFFF")
        self.speed_progress["value"] = 0
        self.imu_label.config(text="IMU Data:", bg="#35424a", fg="#FFFFFF")
        
        self.stop = True  # Set self.stop to True when stopping the ROV
        self.c += 1
        
        self.main.terminate()
        time.sleep(2)  # Wait for 2 seconds to give the process time to terminate
        if self.main.poll() is None:  # If .poll() returns None, the process is still running
            print("main did not terminate, killing it.")
            self.main.kill()
        else:
            print("main terminated gracefully.")

        os.system('cls' if os.name == 'nt' else 'clear')  # clear the terminal
        os.system('cls')
        print("Just stopped/restarted for the", self.c, "th time ;)")

    def restart_rov(self):
        # Restart the ROV
        self.stop_rov()
        self.start_rov()

    def run(self):
        self.root.configure(bg="#35424a")

        # Column and row weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(3, weight=1)
        self.root.rowconfigure(4, weight=1)
        self.root.after(1000, self.update_gui_from_file)

    def update_gui_from_file(self):
        # Read data from the text file and update the GUI components accordingly
        try:
            with open("config.json", "r") as file:
                data_lines = file.readlines()

                # Ensure there is at least one line in the file
                if not data_lines:
                    return

                # Parse the JSON data from the first line
                json_data = json.loads(data_lines[0].strip())

                # Update GUI components accordingly
                motion_data = json_data[0]
                self.motion_label.config(text=f"Motion -> {motion_data}")

                speed_data = json_data[1]
                self.speed_label.config(text=f"Speed -> {speed_data}")
                self.speed_progress["value"] = int(speed_data / 4)

                grippers_data = json_data[3]
                if grippers_data[0] == 1:
                    self.grippers_indicator1.config(text="Open", fg="#5C8374")
                else:
                    self.grippers_indicator1.config(text="Closed", fg="#A63232")
                if grippers_data[1] == 1:
                    self.grippers_indicator2.config(text="Open", fg="#5C8374")
                else:
                    self.grippers_indicator2.config(text="Closed", fg="#A63232")
                if grippers_data[2] == 1:
                    self.grippers_indicator3.config(text="Open", fg="#5C8374")
                else:
                    self.grippers_indicator3.config(text="Closed", fg="#A63232")
                if grippers_data[3] == 1:
                    self.grippers_indicator4.config(text="Open", fg="#5C8374")
                else:
                    self.grippers_indicator4.config(text="Closed", fg="#A63232")

        except Exception as e:
            print(f"Error reading data file: {e}")
        self.root.after(1000, self.update_gui_from_file)


if __name__ == "__main__":
    gui = GUI()
    gui.run()
    gui.root.mainloop()