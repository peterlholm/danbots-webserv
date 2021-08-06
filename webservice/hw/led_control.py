from time import sleep
from gpiozero import LED, PWMLED

from hw.pi_led_control import PiLedControll

I2C_LED_CONTROL = False

if I2C_LED_CONTROL:
    from hw.i2cPWM import setDias, setFlash
    print ("Using i2c LED control")

    def set_dias(val):
        setDias(val*100)

    def set_flash(val):
        setFlash(val*100)

    def get_dias():
        print("get_dias - not implemented")
        return False

    def get_flash():
        print("get_flash - not implemented")
        return False


    def off():
        setDias(0)
        setFlash(0)

else:
    lc = PiLedControll()

    def set_dias(val):
        print ("setdias",val )
        lc.set_dias(val)

    def set_flash(val):
        lc.set_flash(val)

    def get_dias():
        return lc.dias_led.value

    def get_flash():
        return lc.flash_led.value

    def off():
        lc.off()

if __name__ == '__main__':
    set_dias(0.3)
    sleep(5)
        