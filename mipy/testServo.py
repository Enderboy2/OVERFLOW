# Rui Santos & Sara Santos - Random Nerd Tutorials
# Complete project details at https://RandomNerdTutorials.com/raspberry-pi-pico-servo-motor-micropython/

from machine import Pin, PWM
from time import sleep

# Set up PWM Pin for servo control
servo_pin = Pin(0)
servo = PWM(servo_pin)

# Set Duty Cycle for Different Angles
max_duty = 7864
min_duty = 1802


def calculate_duty(angle):
    
    duty = (33.6 * angle) + min_duty
    return int(duty)
half_duty = int(max_duty/2)

#Set PWM frequency
frequency = 50
servo.freq (frequency)

print(calculate_duty(90))
print(calculate_duty(180))
print(calculate_duty(0))
try:
    while True:
        #Servo at 0 degrees
        servo.duty_u16(calculate_duty(0))
        sleep(2)
        #Servo at 90 degrees
        servo.duty_u16(calculate_duty(120))
        sleep(2)
        #Servo at 180 degrees
        # servo.duty_u16(calculate_duty(180))
        # sleep(2)    
      
except KeyboardInterrupt:
    print("Keyboard interrupt")
    # Turn off PWM 
    servo.deinit()