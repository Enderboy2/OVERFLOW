import machine
import time
led1 = machine.Pin(16, machine.Pin.OUT)
led2 = machine.Pin(17, machine.Pin.OUT)
led3 = machine.Pin(18, machine.Pin.OUT)
led4 = machine.Pin(19, machine.Pin.OUT)
led5 = machine.Pin(20, machine.Pin.OUT)
led6 = machine.Pin(21, machine.Pin.OUT)
led7 = machine.Pin(25, machine.Pin.OUT)
while True:
    time.sleep(.1)
    led1.value(not led1.value())
    led2.value(not led2.value())
    led3.value(not led3.value())
    led4.value(not led4.value())
    led5.value(not led5.value())
    led6.value(not led6.value())
    led7.value(not led7.value())