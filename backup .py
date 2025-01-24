import machine
import time
from bno055 import *
import sys
import select
class ROVController:
    def __init__(self):
        # Initialize I2C and IMU
        try:
            self.i2c = machine.SoftI2C(scl=machine.Pin(3), sda=machine.Pin(2))
            self.imu = BNO055(self.i2c)
        except:
            print("no imu")
        self.calibrated = False
        self.yaw = 0
        self.roll = 0
        self.pitch = 0
        # Initialize onboard LED
        self.led = machine.Pin(25, machine.Pin.OUT)

        # Initialize PID Controllers
        self.pid_yaw = PID(kp=1.0, ki=0.1, kd=0.05, setpoint=0, integral_limit=50)
        self.pid_roll = PID(kp=1.5, ki=0.2, kd=0.1, setpoint=0, integral_limit=50)
        self.pid_pitch = PID(kp=1.5, ki=0.2, kd=0.1, setpoint=0, integral_limit=50)
        self.movements = {
            'pitch':[],
            'roll':[],
            'yaw': []
        }
        # Time tracking for PID update
        self.previous_time = time.ticks_us()

        self.m1_pin = 10
        self.m2_pin = 4
        self.m3_pin = 6
        self.m4_pin = 7
        self.m5_pin = 8
        self.m6_pin = 11
        self.m7_pin = 9
        self.m8_pin = 5
        self.servo_1 = machine.PWM(machine.Pin(12))
        self.servo_2 = machine.PWM(machine.Pin(13))
        self.servo_1.freq(50)
        self.servo_2.freq(50)
        
        # Initialize PWM for each servo motor
        self.motor_1 = machine.PWM(machine.Pin(self.m1_pin))
        self.motor_2 = machine.PWM(machine.Pin(self.m2_pin))
        self.motor_3 = machine.PWM(machine.Pin(self.m3_pin))
        self.motor_4 = machine.PWM(machine.Pin(self.m4_pin))
        self.motor_5 = machine.PWM(machine.Pin(self.m5_pin))
        self.motor_6 = machine.PWM(machine.Pin(self.m6_pin))
        self.motor_7 = machine.PWM(machine.Pin(self.m7_pin))
        self.motor_8 = machine.PWM(machine.Pin(self.m8_pin))
        self.gripper_1 = machine.Pin(16,machine.Pin.OUT)
        self.gripper_2 = machine.Pin(17,machine.Pin.OUT)
        self.gripper_3 = machine.Pin(18,machine.Pin.OUT)
        self.gripper_4 = machine.Pin(19,machine.Pin.OUT)
        self.light_1 = machine.Pin(20,machine.Pin.OUT)
        self.light_2 = machine.Pin(21,machine.Pin.OUT)
        self.light_3 = machine.Pin(22,machine.Pin.OUT)

        frequency = 50
        self.motor_1.freq(frequency)
        self.motor_2.freq(frequency)
        self.motor_3.freq(frequency)
        self.motor_4.freq(frequency)
        self.motor_5.freq(frequency)
        self.motor_6.freq(frequency)
        self.motor_7.freq(frequency)
        self.motor_8.freq(frequency)
        self.motors_off()
        self.speed = 0
        self.motion = ''
        self.gripper_statuses = [0,0,0,0,0,0,0]
        self.servo_angles = [0,0]
        self.prev_servo_angles = [0,0]


    def toggle_led(self):
        self.led.value(not self.led.value())
    def blink_led(self,times, delay=0.1):
        for _ in range(times):
            self.toggle_led()
            time.sleep(delay)
            self.toggle_led()
            time.sleep(delay)
    def check_calibration(self):
        try:
            print("got here")
            if not self.calibrated:
                self.calibrated = self.imu.calibrated()
                print('Calibration required: sys {} gyro {} accel {} mag {}'.format(*self.imu.cal_status()))
        except:
            print("no calibration")

    def update_pid(self):
        try:
            yaw, roll, pitch = self.imu.euler()
        except:
            yaw,roll,pitch = [0,0,0] 
        self.yaw = yaw
        self.roll = roll
        self.pitch = pitch
        # Calculate elapsed time
        current_time = time.ticks_us()
        dt = (time.ticks_diff(current_time, self.previous_time)) / 1_000_000  # Convert us to seconds
        self.previous_time = current_time

        # Update PID controllers
        control_yaw = self.pid_yaw.update(yaw, dt)
        control_roll = self.pid_roll.update(roll, dt)
        control_pitch = self.pid_pitch.update(pitch, dt)

        # Determine specific movements
        self.movements = self.determine_movements(control_yaw, control_roll, control_pitch, threshold=10.0)

        # Apply control outputs to actuators (replace this with your motor control logic)
        # Example: self.apply_control(control_yaw, control_roll, control_pitch)

    @staticmethod
    def determine_movements(control_yaw, control_roll, control_pitch, threshold=1.0):
        movements = {"yaw": [], "roll": [], "pitch": []}

        def normalize(value):
            value = (value + 360) % 360 if value < 0 else value % 360
            return value - 360 if value > 180 else value

        control_yaw = normalize(control_yaw)
        control_roll = normalize(control_roll)
        control_pitch = normalize(control_pitch)

        # Determine yaw movement
        if control_yaw > threshold:
            movements["yaw"].append("turn right")
        elif control_yaw < -threshold:
            movements["yaw"].append("turn left")

        # Determine roll movement
        if control_roll > threshold:
            movements["roll"].append("tilt right")
        elif control_roll < -threshold:
            movements["roll"].append("tilt left")

        # Determine pitch movement
        if control_pitch > threshold:
            movements["pitch"].append("tilt up")
        elif control_pitch < -threshold:
            movements["pitch"].append("tilt down")

        return movements
    
    def apply_speeds(self, speeds):
        for i in range(8):
            neutral_pulse = 1500 + int(speeds[i])
            duty = self.microseconds_to_duty(neutral_pulse)
            speeds[i] = duty
            print(speeds[i])
        
        self.motor_1.duty_u16(speeds[0])
        self.motor_2.duty_u16(speeds[1])
        self.motor_3.duty_u16(speeds[2])
        self.motor_4.duty_u16(speeds[3])
        self.motor_5.duty_u16(speeds[4])
        self.motor_6.duty_u16(speeds[5])
        self.motor_7.duty_u16(speeds[6])
        self.motor_8.duty_u16(speeds[7])

    def recieve_decode(self):
        if select.select([sys.stdin], [], [], 0)[0]: # type: ignore
            data = sys.stdin.readline().strip()
            print("Received:", data)
            try:
                values = data.split(",")
                self.motion = values[0]
                self.speed = values[1]
                self.gripper_statuses = values[2:9] #2,3,4,5,6,7,8
                print("gripper statuses after setting from message -> ",self.gripper_statuses)
                self.servo_angles[0] = int(values[9])
                self.servo_angles[1] = int(values[10]) # type: ignore 2,3,4,5
                print(self.servo_angles)
                #sys.stdout.write("value 0:" + str(self.gripper_statuses))
                #self.blink_led(2)  # Blink once if a message is received

            except:
                print("invalid data string", data.split(","))
                
        else:
            #self.blink_led(1)  # Blink once if no message
            #time.sleep(1)  # Wait before checking again
            pass

    def apply_control(self):
        """ dfm = int((int(self.speed) / 100) * 400) # type: ignore
        dfmn = int((int(self.speed) / 100) * -400) """
        dfm = int((int(self.speed) / 100) * 240) # type: ignore
        dfmn = int((int(self.speed) / 100) * -240)
        self.gripper_1.value(bool(int(self.gripper_statuses[0])))
        self.gripper_2.value(bool(int(self.gripper_statuses[1])))
        self.gripper_3.value(bool(int(self.gripper_statuses[2])))    
        self.gripper_4.value(bool(int(self.gripper_statuses[3])))
        self.light_1.value(bool(int(self.gripper_statuses[4])))
        self.light_2.value(bool(int(self.gripper_statuses[5])))
        self.light_3.value(bool(int(self.gripper_statuses[6])))
        
        if self.servo_angles[0] != self.prev_servo_angles[0]:
            self.servo_1.duty_u16(self.calculate_servo_duty(self.servo_angles[0]))
            self.prev_servo_angles[0] = self.servo_angles[0]
        if self.servo_angles[1] != self.prev_servo_angles[1]:
            self.servo_2.duty_u16(self.calculate_servo_duty(self.servo_angles[1]))
            self.prev_servo_angles[1] = self.servo_angles[1]

        if self.motion == "N":
            self.motors_off()
        elif self.motion == "F":
            self.apply_speeds([dfm,dfm,dfmn,dfmn,dfm,dfm,dfmn,dfmn])
            #print("moving forward ;) at motor_speed",dfm )
        elif self.motion == "B":
            self.apply_speeds([dfmn,dfmn,dfm,dfm,dfmn,dfmn,dfm,dfm])
        elif self.motion == "R":
            self.apply_speeds([dfm,dfmn,dfmn,dfm,dfm,dfmn,dfmn,dfm])
        elif self.motion == "L":
            self.apply_speeds([dfmn,dfm,dfm,dfmn,dfmn,dfm,dfm,dfmn])
        elif self.motion == "U":
            self.apply_speeds([dfmn,dfmn,dfmn,dfmn,dfm,dfm,dfm,dfm])
        elif self.motion == "D":
            self.apply_speeds([dfm,dfm,dfm,dfm,dfmn,dfmn,dfmn,dfmn])
        elif self.motion == "r":
            self.apply_speeds([dfmn,dfm,dfmn,dfm,dfmn,dfm,dfmn,dfm])
        elif self.motion == "l":
            self.apply_speeds([dfm,dfmn,dfm,dfmn,dfm,dfmn,dfm,dfmn])
        
    @staticmethod
    def calculate_servo_duty(angle):
        duty = (33.6 * angle) + 1802
        return int(duty)
        
    @staticmethod
    def microseconds_to_duty(us):
        # Formula: duty = (us / 20000) * 65535 for 16-bit resolution
        return int((us / 20000) * 65535)
    
    
    def motors_off(self):
        # print("stopping motors")
        self.motor_1.duty_u16(self.microseconds_to_duty(1500))
        self.motor_2.duty_u16(self.microseconds_to_duty(1500))
        self.motor_3.duty_u16(self.microseconds_to_duty(1500))
        self.motor_4.duty_u16(self.microseconds_to_duty(1500))
        self.motor_5.duty_u16(self.microseconds_to_duty(1500))
        self.motor_6.duty_u16(self.microseconds_to_duty(1500))
        self.motor_7.duty_u16(self.microseconds_to_duty(1500))
        self.motor_8.duty_u16(self.microseconds_to_duty(1500))

# PID Class (as a helper)
class PID:
    def _init_(self, kp, ki, kd, setpoint=0, integral_limit=None):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.previous_error = 0
        self.integral = 0
        self.integral_limit = integral_limit

    def update(self, measured_value, dt):
        error = self.setpoint - measured_value
        proportional = self.kp * error
        self.integral += error * dt
        if self.integral_limit is not None:
            self.integral = max(min(self.integral, self.integral_limit), -self.integral_limit)
        integral = self.ki * self.integral
        derivative = (error - self.previous_error) / dt if dt > 0 else 0
        derivative = self.kd * derivative
        output = proportional + integral + derivative
        self.previous_error = error
        return output

    
# Main loop
def main():
    rov = ROVController()
    #rov.check_calibration()
    rov.motors_off()
    rov.blink_led(12)
    time.sleep(7)
    while True:
        #rov.toggle_led()
        #time.sleep(.1)
        #print(rov.movements)
        #print(rov.pitch, ",",rov.roll,",",rov.pitch)
        rov.recieve_decode()
        rov.apply_control()
        #rov.check_calibration()
        #rov.update_pid()
if __name__ == "__main__":
    main()