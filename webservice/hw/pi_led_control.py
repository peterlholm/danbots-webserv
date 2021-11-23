from time import sleep
from gpiozero import  PWMLED #LED,
from gpiozero.pins.rpigpio import RPiGPIOFactory
from gpiozero.pins.pigpio import PiGPIOFactory

# pi_led_control
# this module implement PWM Led control for GPIO

DIAS_LED_PIN = 12
FLASH_LED_PIN = 13

HW_PWM = True

class PiLedControll:
    dias_led = None
    flash_led = None
    def __init__(self):
        if HW_PWM:
            myfactory = PiGPIOFactory()
        else:
            myfactory = None
        self.dias_led = PWMLED(DIAS_LED_PIN, pin_factory=myfactory)
        #self.flash_led = PWMLED(FLASH_LED_PIN, pin_factory=myfactory, frequency=50)
        self.flash_led = PWMLED(FLASH_LED_PIN, pin_factory=myfactory)
    def set_dias(self, value):
        if value:
            self.dias_led.value = value
        else:
            self.dias_led.value = 0

    def set_flash(self, value):
        if value:
            self.flash_led.value = value
        else:
            self.flash_led.value = 0

    def off(self):
        self.dias_led.value = 0
        self.flash_led.value = 0

if __name__ == '__main__':
    lc = PiLedControll()
    lc.set_dias(True)
    sleep(2)
    lc.set_dias(False)
    sleep(2)
    lc.set_dias(1)
    sleep(11)
    lc.set_dias(0.3)
    sleep(11)
    #lc.off()
    