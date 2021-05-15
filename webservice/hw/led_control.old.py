""" HW based led control """

import time
from gpiozero import PWMLED
import wiringpi

FLASH_IO=23
DIAS_IO=26
#FLASH_IO=12
#DIAS_IO=13
def reset_pins(io, pin):
    io.pinMode(pin,io.OUTPUT)
    io.digitalWrite(pin, io.LOW)


def pwm_dim(io, pin, val):
    val = val*1024 #maps percent to 1024 range
    io.pinMode(pin,io.PWM_OUTPUT)
    io.pwmWrite(pin, int(val))
    if(val == 0):
        io.digitalWrite(pin, io.LOW)


io = wiringpi.GPIO(wiringpi.GPIO.WPI_MODE_PINS)

reset_pins(io, FLASH_IO)
reset_pins(io, DIAS_IO)

def flash_led(val):
    print("Flash", val)
    #led = PWMLED(FLASH_IO)
    if val:
        pwm_dim(io,FLASH_IO,0.95)
    else:
        pwm_dim(io,FLASH_IO,0.0)
    return

def dias_led(val):
    print("Dias", val)
    led = PWMLED(DIAS_IO)
    if val:
        pwm_dim(io,DIAS_IO,0.95)
    else:
        pwm_dim(io,DIAS_IO,0.0)
    return

#tryk knap gpio 4

if __name__ == '__main__':
    print("Start testing")
    print("Turn Flash led ON")
    flash_led(True)
    time.sleep(3)
    print("Turn Flash Led OFF")
    flash_led(False)
    time.sleep(3)
    print("Turn Dias led ON")
    dias_led(True)
    time.sleep(3)
    print("Turn Dial Led OFF")
    dias_led(False)
    time.sleep(3)
    print("Turn Both led ON")
    flash_led(True)
    dias_led(True)
    time.sleep(3)
    print("Turn Both Led OFF")
    flash_led(False)
    dias_led(False)
    print("Test finish")
