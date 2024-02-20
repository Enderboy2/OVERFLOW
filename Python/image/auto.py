import cv2
import numpy as np

lower_red = np.array([0, 100, 100])
upper_red = np.array([10, 255, 255])

frameHSV = None
colorSelected = False
refPt = []

rtsp_username = "admin"
rtsp_password = "overflow123"

def create_camera(channel):
    rtsp = f"rtsp://{rtsp_username}:{rtsp_password}@192.168.1.1:554/Streaming/channels/{channel}01"
    cap = cv2.VideoCapture(rtsp)
    if not cap.isOpened():
        print("Error", f"Cannot connect to camera {channel}")
        return None
    return cap

def click_and_select_color(event, x, y, flags, param):
    global frameHSV, colorSelected, refPt, lower_red, upper_red
    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x, y)]
        pixel_value = frameHSV[y, x]
        hue = pixel_value[0]
        saturation = pixel_value[1]
        value = pixel_value[2]

        sensitivity = 15
        lower_red = np.array([max(hue - sensitivity, 0), max(saturation - sensitivity, 0), max(value - sensitivity, 0)])
        upper_red = np.array([min(hue + sensitivity, 180), min(saturation + sensitivity, 255), min(value + sensitivity, 255)])
        
        cv2.setTrackbarPos("Lower H", "Frame", lower_red[0])
        cv2.setTrackbarPos("Lower S", "Frame", lower_red[1])
        cv2.setTrackbarPos("Lower V", "Frame", lower_red[2])
        cv2.setTrackbarPos("Upper H", "Frame", upper_red[0])
        cv2.setTrackbarPos("Upper S", "Frame", upper_red[1])
        cv2.setTrackbarPos("Upper V", "Frame", upper_red[2])

        colorSelected = True

def nothing(x):
    pass

cam_no = 4
cap = create_camera(str(cam_no))

cv2.namedWindow("Frame")
cv2.setMouseCallback("Frame", click_and_select_color)

cv2.createTrackbar("Lower H", "Frame", 0, 180, nothing)
cv2.createTrackbar("Lower S", "Frame", 0, 255, nothing)
cv2.createTrackbar("Lower V", "Frame", 0, 255, nothing)
cv2.createTrackbar("Upper H", "Frame", 180, 180, nothing)
cv2.createTrackbar("Upper S", "Frame", 255, 255, nothing)
cv2.createTrackbar("Upper V", "Frame", 255, 255, nothing)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Resize the frame here, after it has been captured
    frame = cv2.resize(frame, (600, 480))
    frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    if colorSelected:
        lower_red = np.array([cv2.getTrackbarPos("Lower H", "Frame"),
                              cv2.getTrackbarPos("Lower S", "Frame"),
                              cv2.getTrackbarPos("Lower V", "Frame")])
        upper_red = np.array([cv2.getTrackbarPos("Upper H", "Frame"),
                              cv2.getTrackbarPos("Upper S", "Frame"),
                              cv2.getTrackbarPos("Upper V", "Frame")])

    mask = cv2.inRange(frameHSV, lower_red, upper_red)
    result = cv2.bitwise_and(frame, frame, mask=mask)

    cv2.imshow("Frame", frame)
    cv2.imshow("Mask", mask)
    cv2.imshow("Result", result)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
