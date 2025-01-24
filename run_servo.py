import serial
import time
from serial.tools import list_ports
import os
import curses
import socket
import json
JOYSTICK_SERVER_URL = 'http://localhost:5000/joystick' 
default_joystick_data = {
    "axes": [0, 0, 0, 0],
    "buttons": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "name": "Joystick"
}

joystick_data = default_joystick_data
gripper_statuses = [0,0,0,0,0,0,0]
servo_angles = [0,0]
motion = 'N'
threshold = 0.3
message = ''
previous_button_states = {}
servo_angles = [0,0]

def send_to_pico(message, port="/dev/ttyACM0", baudrate=115200):
    """
    Sends the given message string to a Pi Pico via USB.

    Args:
        message (str): The message to send.
        port (str): The serial port the Pico is connected to.
        baudrate (int): Baud rate for the serial connection.

    Returns:
        bool: True if message was sent successfully, False otherwise.
    """
    try:
        # Open the serial connection
        with serial.Serial(port, baudrate, timeout=1) as pico_serial:
            # Encode the message and send it
            pico_serial.write(message.encode())
            # Optional: Wait for Pico to acknowledge (if programmed)
            #time.sleep(0.1)
            # # Read response (if applicable)
            # if pico_serial.in_waiting > 0:
            #     response = pico_serial.read_all().decode('utf-8')
                #print(f"Response from Pico: {response}")
            return True
    except serial.SerialException as e:
        #print(f"Error communicating with Pico: {e}")
        return False


def detect_pico_port():
    """
    Automatically detects the serial port for a Raspberry Pi Pico.

    Returns:
        str: The serial port of the Pico (e.g., "/dev/ttyACM0") or None if not found.
    """
    pico_vid = "2E8A"  # Raspberry Pi Pico's Vendor ID
    pico_pid = "0005"  # Raspberry Pi Pico's Product ID
    
    ports = list_ports.comports()  # Get a list of all serial ports
    
    for port in ports:
        if port.vid is not None and port.pid is not None:  # Ensure VID and PID exist
            if f"{port.vid:04X}" == pico_vid and f"{port.pid:04X}" == pico_pid:
                #print(f"Pico detected on port: {port.device}")
                return port.device  # Return the port (e.g., "/dev/ttyACM0")
            else:
                #print("wrong pid/vid",f"{port.vid:04X}",f"{port.pid:04X}")
                #print (pico_vid,pico_pid)
                pass
        else:
            pass
    #print("Pico not detected.")
    return None

def clear_terminal():
    """
    Clears the terminal screen.
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def get_remote_joystick_status(client_socket):
    #print("Fetching joystick data...")
    global joystick_data
    try:
        # Fetch data from the joystick server
        response_json = client_socket.recv(1024).decode()
        
        # Check and update joystick_data based on the condition
        if 'axes' in response_json and '3' in response_json['axes']:
            if response_json['axes']['3'] != 0:
                joystick_data = response_json
                
            else:
                joystick_data = default_joystick_data
        else:
            #print("Unexpected response structure:", response_json)
            joystick_data = default_joystick_data
    except :
        #print(f"Error fetching joystick data: {e}")
        joystick_data = default_joystick_data
        print("There is an error")

def determine_motion(joystick_data):
    global gripper_statuses
    global previous_button_states
    global servo_angles
    #global mode
    try:
        # Validate that joystick_data has the necessary keys
        if not ('buttons' in joystick_data and isinstance(joystick_data['buttons'], dict) and
                'axes' in joystick_data and isinstance(joystick_data['axes'], dict)):
            #print("Invalid joystick data structure.")
            return

        # Initialize previous_button_states if not already done
        if not previous_button_states:
            previous_button_states = {str(i): 0 for i in range(len(gripper_statuses))}

        # Update gripper statuses based on button presses
        for i in range(len(gripper_statuses)):
            button_key = str(i)  # Use string keys as in joystick_data
            if button_key in joystick_data['buttons']:
                # Detect a press transition (from 0 to 1)
                if joystick_data['buttons'][button_key] == 1 and previous_button_states[button_key] == 0:
                    gripper_statuses[i] = int(not gripper_statuses[i])  # Toggle status

                # Update previous button state
                previous_button_states[button_key] = joystick_data['buttons'][button_key]

        # Extract axis values, defaulting to 0 if missing
        forward_backward = joystick_data['axes'].get('1', 0.0)
        left_right = joystick_data['axes'].get('0', 0.0)
        rotation = joystick_data['axes'].get('2', 0.0)
        hat = joystick_data['hat']
        
        #     if mode == 'N':
        #         if hat[0] != 0:
        #             if hat[0] == 1:
        #                 mode == 'S1+'
        #             else:
        #                 mode == 'S1-'
        #         else:
        #             if hat[1] == 1:
        #                 mode == 'S1+'
        #             elif hat[1] == -1:
        #                 mode == 'S1-'
        #     else:
        #         mode == 'N'
        
        
        # Determine motion
        if joystick_data['buttons'][str(7)] == 1:
            motion = "N"
            if hat[1] > 0:
                if servo_angles[0] + 30 <= 180:
                    servo_angles[0] = servo_angles[0] + 30
            elif hat[1] < 0:
                 if servo_angles[0] - 30 >= 0:
                    servo_angles[0] = servo_angles[0] - 30
            elif hat[0] > 0:
                if servo_angles[1] + 30 <= 180:
                    servo_angles[1] = servo_angles[1] + 30
            elif hat[0] < 0:
                 if servo_angles[1] - 30 >= 0:
                    servo_angles[1] = servo_angles[1] - 30
           
        else:
            if abs(forward_backward) > threshold:
                motion = "B" if forward_backward > 0 else "F"
            elif abs(left_right) > threshold + 0.1:
                motion = "R" if left_right > 0 else "L"
            elif abs(rotation) > threshold + 0.1:
                motion = "r" if rotation > 0 else "l"
            elif hat[1] > 0:
                motion = "U"
            elif hat[1] < 0:
                motion = "D"
            elif hat[0] > 0:
                motion = "E"
            elif hat[0] < 0:
                motion = "Q"
            else:
                motion = "N"



        speed = int((((joystick_data['axes'].get('3', 0.0) * -1) + 1) / 2) * 100)
        
        # Construct the message
       
            
        message = motion + ',' + str(speed) + ',' + ','.join(str(item) for item in gripper_statuses) + ',' + str(servo_angles[0]) + ',' + str(servo_angles[1]) + ','
        message = message[:(len(message)) - 1]
        return message
    except Exception as e:
        #print(f"An error occurred in determine_motion: {e}")
        message = "N," + ',' +','.join(str(item) for item in gripper_statuses)
        message = message[:(len(message)) - 1]
        return message
        
def run_server():
    pico_port = detect_pico_port()
    server_ip = "localhost"
    port = 5000

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_ip, port))
    server.listen(5)
    print(f"Listening on {server_ip}:{port}")

    try:
        while True:
            client_socket, client_address = server.accept()
            print(f"Accepted connection from {client_address[0]}:{client_address[1]}")

            prev_message = None  # Initialize previous message

            try:
                while True:
                    request = client_socket.recv(1024)
                    if not request:
                        print("Client disconnected.")
                        break
                    try:
                        joystick_data = json.loads(request.decode("utf-8"))
                        message = determine_motion(joystick_data)
                        
                        # Print only if the message is different from the previous one
                        if message != prev_message:
                            print(message)
                            if pico_port:
                                if send_to_pico((message+"\n"), pico_port):
                                    #stdscr.addstr(1, 0, "Message sent successfully.")
                                    print(f"Sent: {message}")
                                    pass
                                else:
                                    #stdscr.addstr(1, 0, "Failed to send message. Rechecking Pico connection...")
                                    pico_port = detect_pico_port()  # Recheck Pico connection if sending fails
                            else:
                                #stdscr.addstr(1, 0, "Pico not found. Please connect it.")
                                pico_port = detect_pico_port()  # Continuously check for Pico connection
                            prev_message = message  # Update previous message

                    except json.JSONDecodeError:
                        print("Invalid JSON data received.")
                        continue

                    # Optionally send a response to the client
                    response = "Data received".encode("utf-8")
                    client_socket.send(response)

            except socket.error as e:
                print(f"Socket error: {e}")

            finally:
                client_socket.close()
                print("Connection to client closed.")

    except KeyboardInterrupt:
        print("Server shutting down.")

    finally:
        server.close()
        print("Server socket closed.")

# Run the server

run_server()