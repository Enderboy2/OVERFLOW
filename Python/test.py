import tkinter as tk
from tkinter import ttk
import threading
import time
from communication import Communication

com = Communication()

def my_function(numbers, duration):
    com.send_command("*" + str(numbers[0]) + "," + str(numbers[1]) + "," + str(numbers[2]) + "," + str(numbers[3]) + "," + str(numbers[4]) + "," + str(numbers[5]) + "," + "0,0,0,0/")
    time.sleep(duration)
    com.send_command("*0,0,0,0,0,0,0,0,0,0/")
    print("Function completed")

def start_function():
    try:
        numbers = [int(entry_fields[i].get()) for i in range(6)]
        duration = int(duration_entry.get())
        
        threading.Thread(target=my_function, args=(numbers, duration)).start()
    except ValueError:
        print("Please enter valid integers.")

root = tk.Tk()
root.title("Function Runner")

entry_fields = []
for i in range(6):
    entry = ttk.Entry(root)
    entry.grid(row=0, column=i)
    entry_fields.append(entry)

ttk.Label(root, text="Duration (s):").grid(row=1, column=0)
duration_entry = ttk.Entry(root)
duration_entry.grid(row=1, column=1)

start_button = ttk.Button(root, text="Start Function", command=start_function)
start_button.grid(row=2, column=0, columnspan=6)

root.mainloop()
