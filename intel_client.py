import socket
import pickle
import cv2
import numpy as np
import pyrealsense2 as rs

points = []
depth_scale = 0.001  # RealSense depth scale
intrinsics = None

# Connect to server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 5000))
print("Connected to the server.")

def recv_all(sock, size):
    data = b""
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            return None
        data += packet
    return data

def average_depth(depth_frame, point, kernel_size=5):
    x, y = point
    region = depth_frame[max(0, y - kernel_size//2): y + kernel_size//2 + 1, 
                         max(0, x - kernel_size//2): x + kernel_size//2 + 1]
    valid_depths = region[region > 0]
    return np.mean(valid_depths) * depth_scale if valid_depths.size > 0 else 0

def get_distance(point1, point2, depth_frame):
    z1 = average_depth(depth_frame, point1)
    z2 = average_depth(depth_frame, point2)

    point1_3d = rs.rs2_deproject_pixel_to_point(intrinsics, point1, z1)
    point2_3d = rs.rs2_deproject_pixel_to_point(intrinsics, point2, z2)

    return np.linalg.norm(np.array(point1_3d) - np.array(point2_3d))

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        print(f"Point {len(points)}: {x}, {y}")

cv2.namedWindow("RealSense")
cv2.setMouseCallback("RealSense", mouse_callback)

try:
    while True:
        data_len = client_socket.recv(4)
        if not data_len:
            break
        
        size = int.from_bytes(data_len, byteorder='big')
        data = recv_all(client_socket, size)
        
        if data:
            blended_image, depth_frame, intrinsics_data = pickle.loads(data)

            # Reconstruct intrinsics
            intrinsics = rs.intrinsics()
            intrinsics.width = intrinsics_data['width']
            intrinsics.height = intrinsics_data['height']
            intrinsics.ppx = intrinsics_data['ppx']
            intrinsics.ppy = intrinsics_data['ppy']
            intrinsics.fx = intrinsics_data['fx']
            intrinsics.fy = intrinsics_data['fy']
            intrinsics.model = intrinsics_data['model']
            intrinsics.coeffs = intrinsics_data['coeffs']

            cv2.imshow("RealSense", blended_image)

            if len(points) == 2:
                distance = get_distance(points[0], points[1], depth_frame) - 0.08
                print(f"Measured Distance: {distance:.2f} meters")
                points.clear()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    client_socket.close()
    cv2.destroyAllWindows()
    print("Client closed.")
