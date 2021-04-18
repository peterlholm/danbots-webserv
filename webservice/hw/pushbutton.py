#tryk knap gpio 4
from gpiozero import Button

BUTTON_IO = 4

button = Button(BUTTON_IO)

def button_press():
    print ("Button Press")

button.when_pressed = button_press
