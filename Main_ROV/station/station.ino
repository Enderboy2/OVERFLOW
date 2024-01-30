//not using the build in serial, but I could have
#include <SoftwareSerial.h>
#define SSerialRX        7 //Serial Receive pin
#define SSerialTX        8 //Serial Transmit pin
#define SSerialTxControl A0   //RS485 Direction control pin
 
#define RS485Transmit    HIGH //station
#define RS485Receive     LOW //rov
 
int byteReceived;
int byteSend;
 
// making an RS485Serial object
SoftwareSerial RS485Serial(SSerialRX, SSerialTX); // RX, TX
 
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.println("RS485 demo by Kevin Saye");
  pinMode(SSerialTxControl, OUTPUT);
 
  digitalWrite(SSerialTxControl, RS485Transmit);  // Init Transceiver  
  RS485Serial.begin(115200);   // set the data rate .
}
 
void loop() {
  if (Serial.available()) {
    // read data from the real serial (we are going to send it on the RS485 bus
    byteReceived = Serial.read();
    Serial.print(byteReceived, DEC);
 
    digitalWrite(SSerialTxControl, RS485Transmit);  // Enable RS485 Transmit   
    RS485Serial.write(byteReceived);                // Send byte to Remote Device
  }
 
  // now we read from the RS485 bus
  if (RS485Serial.available()) {
    byteReceived = RS485Serial.read();
    Serial.write(byteReceived );
  }
}
