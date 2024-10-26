from flask import Flask, jsonify
import pygame
from flask_cors import CORS
import threading

app = Flask(__name__)
CORS(app)

# Initialize joystick data
joystick_data = {
    "axes": [],
    "buttons": [],
    "hats": []
}

def get_joystick_data():
    global joystick_data
    pygame.init()
    pygame.joystick.init()
    
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    
    while True:
        pygame.event.pump()  # Process event queue
        
        # Update all joystick axes
        joystick_data['axes'] = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
        
        # Update all button states
        joystick_data['buttons'] = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]
        
        # Update all hat (D-pad) positions
        joystick_data['hats'] = [joystick.get_hat(i) for i in range(joystick.get_numhats())]

# Flask route to serve the joystick data as JSON
@app.route('/joystick-data', methods=['GET'])
def get_data():
    return jsonify(joystick_data)

if __name__ == '__main__':
    # Run joystick data collection in a background thread
    threading.Thread(target=get_joystick_data, daemon=True).start()
    
    # Start Flask server
    app.run(host='192.168.137.1', port=5000)
