import cv2
import socket
import struct
import pickle
import threading
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('127.0.0.1', 9999))
server_socket.listen(5)
logging.info("Server started, waiting for clients...")

def stream_camera(conn, cam_index):
    try:
        cap = cv2.VideoCapture(cam_index)
        if not cap.isOpened():
            raise Exception(f"Camera {cam_index} could not be opened.")
        
        logging.info(f"Camera {cam_index} successfully opened.")
        cap.set(cv2.CAP_PROP_FPS, 15)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        frames_sent = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                logging.error(f"Failed to read from camera {cam_index}")
                break

            data = pickle.dumps((cam_index, frame))
            conn.sendall(struct.pack("Q", len(data)) + data)
            frames_sent += 1

            if frames_sent % 100 == 0:
                logging.info(f"Camera {cam_index}: {frames_sent} frames sent.")
    
    except Exception as e:
        logging.error(f"Error with camera {cam_index}: {e}")
    finally:
        cap.release()
        logging.info(f"Camera {cam_index} stream closed.")

def handle_client(conn, addr):
    threads = []
    active_cameras = 0

    for i in range(3):  # Adjust for more webcams
        try:
            t = threading.Thread(target=stream_camera, args=(conn, i), daemon=True)
            t.start()
            threads.append(t)
            active_cameras += 1
        except Exception as e:
            logging.error(f"Failed to start camera {i}: {e}")

    logging.info(f"{active_cameras} cameras started for client {addr}.")

    for t in threads:
        t.join()

    conn.close()
    logging.info(f"Connection with {addr} closed.")

while True:
    try:
        conn, addr = server_socket.accept()
        logging.info(f"New client connected from {addr}")
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except Exception as e:
        logging.error(f"Server error: {e}")
