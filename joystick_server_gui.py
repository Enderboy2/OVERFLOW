import pygame
import socket
import json
import asyncio
import websockets
import threading

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
        "axes": {},
        "buttons": {},
        "hat": None,
    }

    if joystick:
        joystick_data["name"] = joystick.get_name()

        # Get axes data and apply threshold
        for i in range(joystick.get_numaxes()):
            axis_value = joystick.get_axis(i)
            joystick_data["axes"][i] = round(axis_value, 2)

        # Get buttons data
        for i in range(joystick.get_numbuttons()):
            joystick_data["buttons"][i] = joystick.get_button(i)

        # Get hat data if present
        if joystick.get_numhats() > 0:
            joystick_data["hat"] = joystick.get_hat(0)

    return joystick_data


def significant_change(data1, data2):
    for axis in data1["axes"]:
        if abs(data1["axes"][axis] - data2["axes"][axis]) > THRESHOLD:
            return True
    for button in data1["buttons"]:
        if data1["buttons"][button] != data2["buttons"][button]:
            return True
    if data1["hat"] != data2["hat"]:
        return True
    return False


# TCP Socket for ROV Communication
def run_tcp_client(data_queue):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = "localhost"
    server_port = 5000

    try:
        print(f"Connecting to TCP server at {server_ip}:{server_port}...")
        client.connect((server_ip, server_port))
        print("TCP connection established")

        prev_data = get_joystick_data()

        while True:
            pygame.event.pump()  # Poll for joystick events

            current_data = get_joystick_data()
            if significant_change(current_data, prev_data):
                msg = json.dumps(current_data)
                client.sendall(msg.encode("utf-8"))
                print(f"TCP Sent: {msg}")
                prev_data = current_data

                # Send data to the WebSocket server
                data_queue.put_nowait(current_data)  # Directly put data in the queue

            pygame.time.wait(100)

    except (socket.error, ConnectionRefusedError) as e:
        print(f"TCP Connection error: {e}")
    finally:
        client.close()
        print("TCP connection to server closed")


# WebSocket Server for GUI Communication
async def joystick_websocket_server(websocket, path, data_queue):
    prev_data = {}
    try:
        while True:
            # Check if new data is available in the queue
            if not data_queue.empty():
                current_data = await data_queue.get()

                if significant_change(current_data, prev_data):
                    msg = json.dumps(current_data)
                    await websocket.send(msg)
                    print(f"WebSocket Sent: {msg}")
                    prev_data = current_data

            await asyncio.sleep(0.1)  # Prevent high CPU usage
    except websockets.ConnectionClosed:
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"WebSocket server error: {e}")


async def run_websocket_server(data_queue):
    async def server(websocket, path):
        await joystick_websocket_server(websocket, path, data_queue)

    try:
        print("Starting WebSocket server...")
        # Start WebSocket server using asyncio
        await websockets.serve(server, "localhost", 8765)
    except Exception as e:
        print(f"WebSocket server error: {e}")


# Function to start both TCP client and WebSocket server in threads
def start_servers():
    # Create a queue for inter-process communication
    data_queue = asyncio.Queue()

    # Start the TCP client in a separate thread
    tcp_thread = threading.Thread(target=run_tcp_client, args=(data_queue,))
    tcp_thread.daemon = True
    tcp_thread.start()

    # Start the WebSocket server (asyncio loop)
    loop = asyncio.get_event_loop()
    loop.create_task(run_websocket_server(data_queue))
    loop.run_forever()  # Run the event loop indefinitely


# Main function to run everything
if __name__ == "__main__":
    start_servers()
