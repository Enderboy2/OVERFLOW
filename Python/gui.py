import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import serial.tools.list_ports
import time
import os

class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ROV Controller")
        self.root.geometry("400x400")
        self.root.minsize(500, 400)  # Set a minimum size
        self.stop = True
        self.c = 0
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
        self.motion_label = tk.Label(self.root, text="Motion:", font=font_style, fg=label_color, bg=bg_color)
        self.motion_label.grid(row=3, column=0, pady=5, padx=10, sticky="w")

        # Speed Label
        self.speed_label = tk.Label(self.root, text="Speed:", font=font_style, fg=label_color, bg=bg_color)
        self.speed_label.grid(row=4, column=0, pady=5, padx=10, sticky="w")

        # Speed Progress Bar
        self.speed_progress = ttk.Progressbar(self.root, length=200, mode="determinate", style="TProgressbar")
        self.speed_progress.grid(row=4, column=1, pady=5, padx=10, sticky="w")

        # Grippers Label
        self.grippers_label = tk.Label(self.root, text="Grippers:", font=font_style, fg=label_color, bg=bg_color)
        self.grippers_label.grid(row=5, column=0, pady=5, padx=10, sticky="w")

        # Grippers Indicator
        self.grippers_indicator = tk.Label(self.root, text="", font=font_style, fg=label_color, bg=bg_color)
        self.grippers_indicator.grid(row=5, column=1, pady=5, padx=10, sticky="w")

        # Gripper Index Label
        self.gripper_index_label = tk.Label(self.root, text="", font=font_style, fg=label_color, bg=bg_color)
        self.gripper_index_label.grid(row=6, column=0, pady=5, padx=10, sticky="w")

        # IMU Label
        self.imu_label = tk.Label(self.root, text="IMU Data:", font=font_style, fg=label_color, bg=bg_color)
        self.imu_label.grid(row=7, column=0, pady=5, padx=10, sticky="w")

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
            
            subprocess.Popen(["python", "main.py", selected_port])
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.restart_button.config(state=tk.NORMAL)
            self.stop = False
            self.run()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start ROV: {e}")

    def stop_rov(self):
        # Stop the ROV
        # Add any necessary logic to stop the ROV (e.g., sending a stop command)
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.restart_button.config(state=tk.DISABLED)

        # Clear GUI data
        self.motion_label.config(text="Motion:", bg="#35424a", fg="#FFFFFF")
        self.speed_label.config(text="Speed:", bg="#35424a", fg="#FFFFFF")
        self.speed_progress["value"] = 0
        self.grippers_label.config(text="Grippers:", bg="#35424a", fg="#FFFFFF")
        self.grippers_indicator.config(text="", bg="#35424a", fg="#5C8374")
        self.gripper_index_label.config(text="", bg="#35424a", fg="#FFFFFF")
        self.imu_label.config(text="IMU Data:", bg="#35424a", fg="#FFFFFF")
        self.stop = True
        self.c += 1
        os.system('cls' if os.name == 'nt' else 'clear') # clear the terminal
        print("Just stopped/restarted for the", self.c ,"th time ;)")

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
        self.root.mainloop()
        while(self.stop != True):
            self.update_gui_from_file()
            time.sleep(0.1)

    def update_gui_from_file(self):
        # Read data from the text file and update the GUI components accordingly
        try:
            with open("data.txt", "r") as file:
                # Read all lines into a list
                data_lines = file.readlines()

                # Example: Update motion label
                motion_data = data_lines[0].strip()
                self.motion_label.config(text=f"Motion: {motion_data}")

                # Example: Update speed label and progress bar
                speed_data = data_lines[1].strip()
                self.speed_label.config(text=f"Speed: {speed_data}")
                self.speed_progress["value"] = int(speed_data)

                # Example: Update grippers label and indicator
                grippers_data = data_lines[2].strip()
                self.grippers_label.config(text=f"Grippers: {grippers_data}")
                if grippers_data == "1":
                    self.grippers_indicator.config(text="Open", fg="#5C8374")
                else:
                    self.grippers_indicator.config(text="Closed", fg="#A63232")

                # Example: Update gripper index label
                gripper_index_data = data_lines[3].strip()
                self.gripper_index_label.config(text=f"Gripper Index: {gripper_index_data}")

        except Exception as e:
            # Handle file read error
            print(f"Error reading data file: {e}")


if __name__ == "__main__":
    gui = GUI()
    gui.run()