from flask import Flask, jsonify
from flask_cors import CORS
import pygame

app = Flask(__name__)
CORS(app)  # Enable CORS

# Initialize Pygame and joystick
pygame.init()
pygame.joystick.init()

# Maintain a dictionary to store the last known state of buttons
last_button_state = {}

@app.route('/joystick', methods=['GET'])
def get_joystick_status(): 
    status = {}
    try:
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()

            # Joystick name
            status['name'] = joystick.get_name()

            # Button states with debouncing
            buttons = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]

            print(buttons)
            status['buttons'] = buttons

            # Axis positions
            axes = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
            status['axes'] = axes

            # Check if the fourth axis is zero and wait for it to change
            if axes[3] == 0.0:
                print("Fourth axis is zero. Waiting for movement...")
                return jsonify(status)  # Skip sending status until values change

            # Check if all axis values are zero and reinitialize if necessary
            if all(val == 0.0 for val in axes):
                joystick.quit()  # Quit the joystick to reset
                joystick.init()   # Reinitialize the joystick

            return jsonify(status)
        else:
            return jsonify({'error': 'No joystick found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500                                                                  

if __name__ == '__main__':
    app.run(host='192.168.137.1', port=5000)
