import socket
import cv2

# Load the depth image
image_path = "depth_image.png"
with open(image_path, "rb") as f:
    image_data = f.read()

# Create a socket and send the image
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("RECEIVER_IP_ADDRESS", 12345))  # Replace with receiver's IP
s.sendall(image_data)
s.close()
print("Image sent successfully")