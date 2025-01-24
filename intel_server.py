import socket
import pickle
import cv2
import pyrealsense2 as rs
import numpy as np

# Initialize RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
profile = pipeline.start(config)

# Depth alignment
align = rs.align(rs.stream.color)

# Get intrinsics and convert to dictionary
depth_intrinsics = profile.get_stream(rs.stream.depth).as_video_stream_profile().get_intrinsics()
intrinsics_dict = {
    "width": depth_intrinsics.width,
    "height": depth_intrinsics.height,
    "ppx": depth_intrinsics.ppx,
    "ppy": depth_intrinsics.ppy,
    "fx": depth_intrinsics.fx,
    "fy": depth_intrinsics.fy,
    "model": depth_intrinsics.model,
    "coeffs": depth_intrinsics.coeffs,
}

# Server setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('127.0.0.1', 5000))
server_socket.listen(1)
print("Server listening on port 5000...")

conn, addr = server_socket.accept()
print(f"Connection from {addr}")

try:
    while True:
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)
        color_frame = aligned_frames.get_color_frame()
        depth_frame = aligned_frames.get_depth_frame()

        if not color_frame or not depth_frame:
            continue

        # Convert frames to numpy arrays
        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())
        depth_colormap = cv2.applyColorMap(
            cv2.convertScaleAbs(depth_image, alpha=0.05), cv2.COLORMAP_JET
        )

        # Blend images
        blended_image = cv2.addWeighted(depth_colormap, 0.5, color_image, 0.5, 0)

        # Serialize and send
        data = pickle.dumps((blended_image, depth_image, intrinsics_dict))
        conn.sendall(len(data).to_bytes(4, byteorder='big'))
        conn.sendall(data)

finally:
    pipeline.stop()
    conn.close()
    server_socket.close()
    print("Server closed.")
