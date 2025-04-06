import socket

# Create a socket and listen for incoming connections
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("0.0.0.0", 12345))  # Listen on all interfaces
s.listen(1)

print("Waiting for connection...")
conn, addr = s.accept()
print(f"Connected to {addr}")

# Receive the image data
image_data = b""
while True:
    chunk = conn.recv(4096)
    if not chunk:
        break
    image_data += chunk

# Save the received image
with open("received_depth_image.png", "wb") as f:
    f.write(image_data)

print("Image received and saved as received_depth_image.png")
conn.close()