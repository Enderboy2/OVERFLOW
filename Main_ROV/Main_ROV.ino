#include <MPU6050_tockn.h>
#include <Wire.h>
#include <Servo.h>
#include <SoftwareSerial.h>
#include<string.h>
#define SSerialTxControl A0   //RS485 Direction control pin

#define RS485Transmit    HIGH //Station
#define RS485Receive     LOW //ROV



Servo motor_1;
Servo motor_2;
Servo motor_3;
Servo motor_4;
Servo motor_5;
Servo motor_6;

SoftwareSerial RS485Serial(7, 8); // RX, TX

class ROV {
  private:

    String command = "";
    int motorSpeeds[7];
    int gripperStatuses[5];
    byte gripperBools[5];
    int imuData[9];
    MPU6050 mpu6050;
    int m1_pin = 3;
    int m2_pin = 5;
    int m3_pin = 6;
    int m4_pin = 9;
    int m5_pin = 10;
    int m6_pin = 11;
    int grip1_pin =  2;
    int grip2_pin =  4;
    int grip3_pin = 12;
    int grip4_pin = 13;


  public:
    ROV() : mpu6050(Wire) {}

    void receive_data() {
      int byteReceived;
      int byteSend;
      char c;
      int values[11];

      if (RS485Serial.available()) {
        byteReceived = RS485Serial.read();
        c = static_cast<char>(byteReceived);
        if (c == '/') {
          Serial.println("whole command -> " + this->command);
          this->command = this->command.substring(1);
          int index = 0;
          while (this->command.length() > 0) {
            int commaIndex = this->command.indexOf(',');
            if (commaIndex != -1) {
              String valueStr = this->command.substring(0, commaIndex);

              values[index] = valueStr.toInt();

              this->command = this->command.substring(commaIndex + 1);

              index++;
            } else {
              values[index] = this->command.toInt();
              break;
            }
          }

          for (int i = 0; i <= 10; i++) {
            if (i <= 5) {
              this->motorSpeeds[i] = values[i];
            } else {
              this->gripperStatuses[i];
            }
          }

          Serial.println(this->command); //print certain value

          this->command = "";

        } else {
          this->command += c;
        }

      }

    }

    void getImuData() {
      mpu6050.update();
      this-> imuData[0] = mpu6050.getTemp();
      this-> imuData[1] = mpu6050.getAccX();
      this-> imuData[2] = mpu6050.getAccY();
      this-> imuData[3] = mpu6050.getAccZ();

      this-> imuData[4] = mpu6050.getGyroX();
      this-> imuData[5] = mpu6050.getGyroY();
      this-> imuData[6] = mpu6050.getGyroZ();

      this-> imuData[7] = mpu6050.getGyroAngleX();
      this-> imuData[8] = mpu6050.getGyroAngleY();
      this-> imuData[9] = mpu6050.getGyroAngleZ();

      this-> imuData[10] = mpu6050.getAngleX();
      this-> imuData[11] = mpu6050.getAngleY();
      this-> imuData[12] = mpu6050.getAngleZ();

    }

    void initialize() {

      Serial.begin(115200);
      Wire.begin();
      mpu6050.begin();
      pinMode(SSerialTxControl, OUTPUT);
      digitalWrite(SSerialTxControl, RS485Receive);  // Init Transceiver
      RS485Serial.begin(115200);   // set the data rate .

      motor_1.attach(m1_pin);
      motor_2.attach(m2_pin);
      motor_3.attach(m3_pin);
      motor_4.attach(m4_pin);
      motor_5.attach(m5_pin);
      motor_6.attach(m6_pin);

      motor_1.writeMicroseconds(1500);
      motor_2.writeMicroseconds(1500);
      motor_3.writeMicroseconds(1500);
      motor_4.writeMicroseconds(1500);
      motor_5.writeMicroseconds(1500);
      motor_6.writeMicroseconds(1500);

      digitalWrite(grip1_pin, 0);
      digitalWrite(grip2_pin, 0);
      digitalWrite(grip3_pin, 0);
      digitalWrite(grip4_pin, 0);
    }

    void adjust_motors() {
      motor_1.writeMicroseconds(1500 + motorSpeeds[0]);
      motor_2.writeMicroseconds(1500 + motorSpeeds[1]);
      motor_3.writeMicroseconds(1500 + motorSpeeds[2]);
      motor_4.writeMicroseconds(1500 + motorSpeeds[3]);
      motor_5.writeMicroseconds(1500 + motorSpeeds[4]);
      motor_6.writeMicroseconds(1500 + motorSpeeds[5]);
    }

    void adjust_grippers() {
      Serial.print(this->gripperStatuses[0]);
      Serial.print(this->gripperStatuses[1]);
      Serial.print(this->gripperStatuses[2]);
      Serial.println(this->gripperStatuses[3]);
      digitalWrite( 2, this->gripperStatuses[0] );
      digitalWrite( 4, this->gripperStatuses[1] );
      digitalWrite( 12, 1 );
      digitalWrite( 13, this->gripperStatuses[3] );
    }

    void send_imu_data() {
      this->getImuData();
      //serial.print(this->imuData[0])
      //serial.print(this->imuData[1])
      //serial.print(this->imuData[2])
      //serial.print(this->imuData[3])
      //serial.print(this->imuData[4])
      //serial.print(this->imuData[5])
      //serial.print(this->imuData[6])
      //serial.print(this->imuData[7])
      //serial.print(this->imuData[8])
      //serial.print(this->imuData[9])
      //serial.print(this->imuData[10])
      //serial.print(this->imuData[11])
      //serial.println(this->imuData[12])
      Serial.write("data of imu");
      Serial.println("data of imu");
    }

    void operate() {

      while (true) {
        this->receive_data();
        this->adjust_motors();
        this->adjust_grippers();
        //this->send_imu_data();
      }
    }

};

ROV rov;

void setup() {
  rov.initialize();
  rov.operate();
}

void loop() {
  // Handle any other non-blocking tasks here
}
