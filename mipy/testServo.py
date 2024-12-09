# Rui Santos & Sara Santos - Random Nerd Tutorials
# Complete project details at https://RandomNerdTutorials.com/raspberry-pi-pico-servo-motor-micropython/

from machine import Pin, PWM
from time import sleep

# Set up PWM Pin for servo control
servo_pin = Pin(0)
servo = PWM(servo_pin)

# Set Duty Cycle for Different Angles
#Set PWM frequency
frequency = 50
servo.freq(frequency)

try:
    while True:
        #Servo at 0 degrees
        servo.duty_u16(16384)
        print("Servo at 0 degrees")
        sleep(2)
        #Servo at 90 degrees
        servo.duty_u16(32768)
        print("Servo at 90 degrees")
        sleep(3)
        #Servo at 180 degrees
        servo.duty_u16(49152)
        print("Servo at 180 degrees")
        sleep(2)   
        servo.duty_u16(0)
        print("0")
        sleep(2)  
      
except KeyboardInterrupt:
    print("Keyboard interrupt")
    # Turn off PWM 
    servo.deinit()