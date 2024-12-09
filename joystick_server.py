import pygame
import socket
import json

# Initialize Pygame and Joystick
pygame.init()
pygame.joystick.init()

joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

THRESHOLD = 0.2  # Define a threshold for axis changes

def get_joystick_data():
    joystick_data = {
        'axes': {},
        'buttons': {},
        'hat': None
    }

    if joystick:
        joystick_data['name'] = joystick.get_name()

        # Get axes data and apply threshold
        for i in range(joystick.get_numaxes()):
            axis_value = joystick.get_axis(i)
            # Round to 2 decimal places to reduce noise
            joystick_data['axes'][i] = round(axis_value, 2)

        # Get buttons data
        for i in range(joystick.get_numbuttons()):
            joystick_data['buttons'][i] = joystick.get_button(i)

        # Get hat data if present
        if joystick.get_numhats() > 0:
            joystick_data['hat'] = joystick.get_hat(0)

    return joystick_data

def significant_change(data1, data2):
    for axis in data1['axes']:
        if abs(data1['axes'][axis] - data2['axes'][axis]) > THRESHOLD:
            return True
    for button in data1['buttons']:
        if data1['buttons'][button] != data2['buttons'][button]:
            return True
    if data1['hat'] != data2['hat']:
        return True
    return False

def run_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = "192.168.137.47"
    server_port = 5000

    try:
        client.connect((server_ip, server_port))
        prev_data = get_joystick_data()

        while True:
            pygame.event.pump()  # Poll for joystick events
            
            current_data = get_joystick_data()
            if significant_change(current_data, prev_data):
                msg = json.dumps(current_data)
                client.sendall(msg.encode('utf-8'))
                print(f"Sent: {msg}")
                prev_data = current_data

            pygame.time.wait(100)

    except (socket.error, ConnectionRefusedError) as e:
        print(f"Connection error: {e}")
    finally:
        client.close()
        print("Connection to server closed")

# Run the client
if __name__ == "__main__":
    run_client()
