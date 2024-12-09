#include <Servo.h>


Servo motor;
int m_pin = 5; //6

void setup() {
  // put your setup code here, to run once:
  motor.attach(m_pin);
  motor.writeMicroseconds(1500);
  delay(7000);
   motor.writeMicroseconds(1690);
   delay(5000);
    motor.writeMicroseconds(1500);
}

void loop() {
  // put your main code here, to run repeatedly:

}
