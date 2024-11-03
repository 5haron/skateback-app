import pyrealsense2 as rs
import numpy as np
import cv2

# Constants
MAX_DEPTH = 0.5          # Maximum depth in meters for detection (e.g., 1.0 meter)
MIN_PERCENTAGE = 50.0    # Minimum percentage coverage required for detection (e.g., 40%)

# Configure depth stream
pipeline = rs.pipeline()
config = rs.config()

# For the L515 LiDAR camera, common depth stream configurations include 640x480 at 30 fps
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

# Start streaming
pipeline.start(config)

try:
    while True:
        # Wait for a coherent set of frames: depth
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        if not depth_frame:
            continue  # If no frame is received, try again

        # Convert depth frame to numpy array
        depth_image = np.asanyarray(depth_frame.get_data())

        # Get depth scale to convert depth units to meters
        depth_sensor = pipeline.get_active_profile().get_device().first_depth_sensor()
        depth_scale = depth_sensor.get_depth_scale()  # Typically around 0.001 for L515

        # Convert depth image to meters
        depth_in_meters = depth_image * depth_scale

        # Create a mask where depth is less than MAX_DEPTH meters
        depth_less_than_max = depth_in_meters < MAX_DEPTH

        # Calculate the percentage of pixels within the specified range
        total_pixels = depth_in_meters.size
        pixels_in_range = np.count_nonzero(depth_less_than_max)
        percentage_in_range = (pixels_in_range / total_pixels) * 100

        # Check if at least MIN_PERCENTAGE of the pixels are within the range
        if percentage_in_range >= MIN_PERCENTAGE:
            print(f"Object detected: {percentage_in_range:.2f}% of pixels are less than {MAX_DEPTH}m away")
        else:
            print(f"No significant object detected: {percentage_in_range:.2f}% of pixels are less than {MAX_DEPTH}m away")

        # Optional: Visualize the depth data
        # Normalize the depth image for visualization (mapping depth to 0-255)
        depth_visual = cv2.normalize(depth_image, None, 0, 255, cv2.NORM_MINMAX)
        depth_visual = np.uint8(depth_visual)
        depth_colormap = cv2.applyColorMap(depth_visual, cv2.COLORMAP_JET)

        # Overlay the mask on the depth image (optional)
        mask_visual = np.zeros_like(depth_colormap)
        mask_visual[depth_less_than_max] = depth_colormap[depth_less_than_max]

        # Display the depth image with the mask
        cv2.imshow('Depth Image with Mask', mask_visual)
        key = cv2.waitKey(1)
        if key == 27:  # Press 'Esc' key to exit
            break

finally:
    # Stop streaming
    pipeline.stop()
    cv2.destroyAllWindows()
