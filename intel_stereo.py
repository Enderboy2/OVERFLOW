import cv2
import pyrealsense2 as rs
import numpy as np

# Initialize RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
profile = pipeline.start(config)

# Get depth scale
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()

# Get alignment object
align = rs.align(rs.stream.color)

# Mouse click points
points = []
locked_frames = None

def average_depth(depth_frame, point, kernel_size=5):
    x, y = point
    depth_data = np.asanyarray(depth_frame.get_data())
    region = depth_data[max(0, y - kernel_size//2): y + kernel_size//2 + 1, 
                        max(0, x - kernel_size//2): x + kernel_size//2 + 1]
    valid_depths = region[region > 0]
    if len(valid_depths) > 0:
        return np.mean(valid_depths) * depth_scale
    else:
        return 0


def get_distance(point1, point2, depth_frame):
    z1 = average_depth(depth_frame, point1)
    z2 = average_depth(depth_frame, point2)
    
    # Convert pixel points to 3D space
    intrinsics = profile.get_stream(rs.stream.depth).as_video_stream_profile().get_intrinsics()
    point1_3d = rs.rs2_deproject_pixel_to_point(intrinsics, point1, z1)
    point2_3d = rs.rs2_deproject_pixel_to_point(intrinsics, point2, z2)

    # Calculate Euclidean distance
    distance = np.linalg.norm(np.array(point1_3d) - np.array(point2_3d))
    return distance

# Mouse callback function
def mouse_callback(event, x, y, flags, param):
    global locked_frames
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        print(f"Point {len(points)}: {x}, {y}")
        if len(points) == 1:
            locked_frames = pipeline.wait_for_frames()

# Main loop
cv2.namedWindow("RealSense")
cv2.setMouseCallback("RealSense", mouse_callback)

try:
    while True:
        if locked_frames is None:
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)
            color_frame = aligned_frames.get_color_frame()
            depth_frame = aligned_frames.get_depth_frame()
            if not color_frame or not depth_frame:
                continue

            # Convert to numpy arrays
            color_image = np.asanyarray(color_frame.get_data())
            depth_image = np.asanyarray(depth_frame.get_data())
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        else:
            aligned_frames = align.process(locked_frames)
            color_frame = aligned_frames.get_color_frame()
            depth_frame = aligned_frames.get_depth_frame()
            color_image = np.asanyarray(color_frame.get_data())
            depth_image = np.asanyarray(depth_frame.get_data())
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        # Apply transparency to depth image (alpha blending)
        alpha = 0.5  # Set transparency level (0.0 is fully transparent, 1.0 is fully opaque)
        transparent_depth = cv2.addWeighted(depth_colormap, alpha, color_image, 1 - alpha, 0)

        # Show the combined image with transparent depth overlaid on the color image
        cv2.imshow("RealSense", transparent_depth)
        
        # Check if two points are selected
        if len(points) == 2:
            distance = get_distance(points[0], points[1], depth_frame) - 0.08
            print(f"Measured Distance: {distance:.2f} meters")
            points.clear()
            locked_frames = None

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    pipeline.stop()
    cv2.destroyAllWindows()