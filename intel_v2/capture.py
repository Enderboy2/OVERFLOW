import pyrealsense2 as rs
import numpy as np
import cv2

# Configure depth stream
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

# Start streaming
pipeline.start(config)

try:
    # Wait for a coherent pair of frames: depth
    frames = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    if not depth_frame:
        raise RuntimeError("No depth frame captured")

    # Convert depth frame to numpy array
    depth_image = np.asanyarray(depth_frame.get_data())

    # Save the depth image
    cv2.imwrite("depth_image.png", depth_image)
    print("Depth image saved as depth_image.png")

finally:
    # Stop streaming
    pipeline.stop()