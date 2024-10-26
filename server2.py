from flask import Flask, render_template, Response
import cv2
import threading
import requests
import time

app = Flask(__name__)

# Camera list and streams
camera_streams = []
cameras = []

# Joystick server URL
JOYSTICK_SERVER_URL = 'http://192.168.137.1:5000/joystick'

# Initialize joystick data storage
joystick_data = {
    "axes": [],
    "buttons": [],
    "hats": []
}


# Function to generate video stream
camera_1 = cv2.VideoCapture(0)
camera_2 = cv2.VideoCapture(1)

def generate_frames(camera):
    while True:
        # Capture frame-by-frame from the specified camera
        success, frame = camera.read()
        if not success:
            break
        else:
            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            # Concatenate the image with the correct HTTP header
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            

@app.route('/video_feed_1')
def video_feed_1():
    # Video feed route for the first camera
    return Response(generate_frames(camera_1), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    # Fetch joystick data from the joystick server
    try:
        response = requests.get(JOYSTICK_SERVER_URL)
        joystick_data = response.json()
    except requests.exceptions.RequestException:
        joystick_data = {
            "axes": ["Error"],
            "buttons": ["Error"],
            "hats": ["Error"]
        }
    return render_template('index.html', data=joystick_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
