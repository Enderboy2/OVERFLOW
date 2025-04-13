import RPi.GPIO as GPIO
import time

# Motor 1 GPIO pins
MOTOR1_ENA = 25  # Enable Pin
MOTOR1_IN1 = 23  # Input Pin 1
MOTOR1_IN2 = 24  # Input Pin 2

# Motor 2 GPIO pins
MOTOR2_ENB = 17  # Enable Pin
MOTOR2_IN3 = 27  # Input Pin 3
MOTOR2_IN4 = 22  # Input Pin 4

# Motor 3 GPIO pins
MOTOR3_ENA = 12  # Enable Pin
MOTOR3_IN1 = 5   # Input Pin 1
MOTOR3_IN2 = 6   # Input Pin 2

class MotorController:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Setup Motor 1
        GPIO.setup(MOTOR1_ENA, GPIO.OUT)
        GPIO.setup(MOTOR1_IN1, GPIO.OUT)
        GPIO.setup(MOTOR1_IN2, GPIO.OUT)
        self.pwm1 = GPIO.PWM(MOTOR1_ENA, 100)
        self.pwm1.start(0)
        
        # Setup Motor 2
        GPIO.setup(MOTOR2_ENB, GPIO.OUT)
        GPIO.setup(MOTOR2_IN3, GPIO.OUT)
        GPIO.setup(MOTOR2_IN4, GPIO.OUT)
        self.pwm2 = GPIO.PWM(MOTOR2_ENB, 100)
        self.pwm2.start(0)
        
        # Setup Motor 3
        GPIO.setup(MOTOR3_ENA, GPIO.OUT)
        GPIO.setup(MOTOR3_IN1, GPIO.OUT)
        GPIO.setup(MOTOR3_IN2, GPIO.OUT)
        self.pwm3 = GPIO.PWM(MOTOR3_ENA, 100)
        self.pwm3.start(0)

    def control_motor(self, motor_number, speed, direction):
        """
        Control individual motors
        :param motor_number: 1, 2, or 3
        :param speed: 0 to 100
        :param direction: 'forward' or 'backward'
        """
        if speed < 0 or speed > 100:
            return
            
        if motor_number == 1:
            self.pwm1.ChangeDutyCycle(speed)
            if direction == 'forward':
                GPIO.output(MOTOR1_IN1, GPIO.HIGH)
                GPIO.output(MOTOR1_IN2, GPIO.LOW)
            else:
                GPIO.output(MOTOR1_IN1, GPIO.LOW)
                GPIO.output(MOTOR1_IN2, GPIO.HIGH)
                
        elif motor_number == 2:
            self.pwm2.ChangeDutyCycle(speed)
            if direction == 'forward':
                GPIO.output(MOTOR2_IN3, GPIO.HIGH)
                GPIO.output(MOTOR2_IN4, GPIO.LOW)
            else:
                GPIO.output(MOTOR2_IN3, GPIO.LOW)
                GPIO.output(MOTOR2_IN4, GPIO.HIGH)
                
        elif motor_number == 3:
            self.pwm3.ChangeDutyCycle(speed)
            if direction == 'forward':
                GPIO.output(MOTOR3_IN1, GPIO.HIGH)
                GPIO.output(MOTOR3_IN2, GPIO.LOW)
            else:
                GPIO.output(MOTOR3_IN1, GPIO.LOW)
                GPIO.output(MOTOR3_IN2, GPIO.HIGH)

    def stop_motor(self, motor_number):
        """
        Stop individual motors
        :param motor_number: 1, 2, or 3
        """
        if motor_number == 1:
            self.pwm1.ChangeDutyCycle(0)
            GPIO.output(MOTOR1_IN1, GPIO.LOW)
            GPIO.output(MOTOR1_IN2, GPIO.LOW)
        elif motor_number == 2:
            self.pwm2.ChangeDutyCycle(0)
            GPIO.output(MOTOR2_IN3, GPIO.LOW)
            GPIO.output(MOTOR2_IN4, GPIO.LOW)
        elif motor_number == 3:
            self.pwm3.ChangeDutyCycle(0)
            GPIO.output(MOTOR3_IN1, GPIO.LOW)
            GPIO.output(MOTOR3_IN2, GPIO.LOW)

    def stop_all(self):
        """Stop all motors"""
        self.stop_motor(1)
        self.stop_motor(2)
        self.stop_motor(3)

    def cleanup(self):
        """Cleanup GPIO pins"""
        self.stop_all()
        GPIO.cleanup()

# Example usage
if __name__ == "__main__":
    try:
        motor_controller = MotorController()
        
        # Example: Run motor 1 forward at 50% speed
        motor_controller.control_motor(1, 50, 'forward')
        time.sleep(2)
        
        # Example: Run motor 2 backward at 75% speed
        motor_controller.control_motor(2, 75, 'backward')
        time.sleep(2)
        
        # Example: Run motor 3 forward at 100% speed
        motor_controller.control_motor(3, 100, 'forward')
        time.sleep(2)
        
        # Stop all motors
        motor_controller.stop_all()
        
    except KeyboardInterrupt:
        print("Program stopped by user")
    finally:
        motor_controller.cleanup()