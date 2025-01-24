import cv2
import socket
import struct
import pickle
import threading
import lo

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client_socket.connect(('192.168.137.47', 9999))
    logging.info("Connected to the server.")
except Exception as e:
    logging.error(f"Connection failed: {e}")
    exit()

data = b""
frame_dict = {}

def receive_frames():
    global data
    try:
        while True:
            # Receive message size
            while len(data) < struct.calcsize("Q"):
                packet = client_socket.recv(4096)
                if not packet:
                    logging.error("Connection lost.")
                    return
                data += packet

            packed_msg_size = data[:struct.calcsize("Q")]
            data = data[struct.calcsize("Q"):]
            msg_size = struct.unpack("Q", packed_msg_size)[0]

            # Receive entire frame
            while len(data) < msg_size:
                data += client_socket.recv(4096)

            frame_data = data[:msg_size]
            data = data[msg_size:]

            cam_index, frame = pickle.loads(frame_data)
            frame_dict[cam_index] = frame
            logging.info(f"Received frame from camera {cam_index}")

    except Exception as e:
        logging.error(f"Error receiving frames: {e}")
    finally:
        client_socket.close()
        logging.info("Connection closed.")

threading.Thread(target=receive_frames, daemon=True).start()

while True:
    try:
        for idx, frame in frame_dict.items():
            cv2.imshow(f"Webcam {idx}", frame)

        if cv2.waitKey(1) == ord('q'):
            break
    except Exception as e:
        logging.error(f"Display error: {e}")
        break

client_socket.close()
cv2.destroyAllWindows()
