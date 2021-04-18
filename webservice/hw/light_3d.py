# set flash light for 3d capture
#from scan3d.led_control import flash_led,dias_led
from gpiozero import LED
from time import sleep
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

def light_3d(picturenumber):
    print (picturenumber)
    if picturenumber == 0:
        print ("turn off both")
        set_flash(False)
        set_dias(False)
        #turn off all light
    elif picturenumber == 1:
        print ("turn flash on", picturenumber)
        set_dias(False)
        set_flash(True)
    elif picturenumber == 2:
        print ("turn dias led on", picturenumber)
        set_flash(False)
        set_dias(True)
    else:
        print ("turn off")
        set_flash(False)
        set_dias(False)


    return True

if __name__ == '__main__':
    for i in range(0,5):
        light_3d(i)
        sleep(5)
        