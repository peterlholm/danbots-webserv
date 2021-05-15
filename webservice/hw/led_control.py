from gpiozero import LED

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
