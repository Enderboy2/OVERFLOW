/* Sweep
  by BARRAGAN <http://barraganstudio.com>
  This example code is in the public domain.

  modified 28 May 2015
  by Michael C. Miller
  modified 8 Nov 2013
  by Scott Fitzgerald

  http://arduino.cc/en/Tutorial/Sweep
*/

#include <Servo.h>

Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards


void setup() {
  myservo.attach(2);  // attaches the servo on GIO2 to the servo object
  Serial.begin(9600);
}

void loop() {
  int pos;
    pos = 0;
    myservo.write(pos);          
    Serial.println(pos);// tell servo to go to position in variable 'pos'
   
}
