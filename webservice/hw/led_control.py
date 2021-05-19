from time import sleep
from gpiozero import LED, PWMLED

LED_dias = LED(12)
LED_flash = LED(13)

def set_flash(on_off):
    if on_off:
        LED_flash.on()
    else:
        LED_flash.off()

def set_dias(on_off):
    if on_off:
        LED_dias.on()
    else:
        LED_dias.off()


def pwmtest():
    myled = PWMLED(13)

    myled.blink(on_time=5, off_time=5, fade_in_time=1, fade_out_time=1,)
    sleep(30)
    myled.off()
    myled.value(0.2)
    sleep(10)
    myled.off()
    return

if __name__ == '__main__':
    pwmtest()
    