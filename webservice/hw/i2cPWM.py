import time
import smbus

###########################################
#  NB  lowest value is 1/32
###########################################

class ncp5623:
    def __init__(self):
        self.DEVICE_ADDRESS = 0x38
        self.LEDregister = 0x70
        self.pwm1Address = 0x40  # 64 #0x40 #DIAS LED
        # 96 #0x60 #pwm2 and pwm3 are connected in parallel in order to provide more current
        self.pwm2Address = 0x60
        self.pwm3Address = 0x80  # 128 #0x80

    def setCurrent(self):
        # set software limit to max
        bus.write_byte(self.DEVICE_ADDRESS, 0x3f)

# Each diode has an individual function in order not to cause confution
    def setDiasBrightness(self, brightness):
        # if i2c fails it tries to set the brightness again
        try:
            hexVal = ILED_calc(brightness)
            I2C_pwm1 = self.pwm1Address | hexVal
            bus.write_byte(self.DEVICE_ADDRESS, I2C_pwm1)
            time.sleep(0.5)
        except:
            time.sleep(0.1)
            self.setDiasBrightness(brightness)

    def setFlashBrightness(self, brightness):
        # if i2c fails it tries to set the brightness again
        try:
            hexVal = ILED_calc(brightness)
            I2C_pwm2 = self.pwm2Address | hexVal
            I2C_pwm3 = self.pwm3Address | hexVal
            bus.write_byte(self.DEVICE_ADDRESS, I2C_pwm3)
            bus.write_byte(self.DEVICE_ADDRESS, I2C_pwm2)
            time.sleep(0.5)
        except:
            time.sleep(0.1)
            self.setFlashBrightness(brightness)


# maps from one interval to another, in this case from 0-100 to 0-31
def map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


def ILED_calc(val):
    iLed = map(val, 0, 100, 0, 31)
    iLed = int(round(iLed))
    return iLed


bus = smbus.SMBus(1)
p1 = ncp5623()
p1.setCurrent()

# call these functions from another script


def setDias(val):
    p1.setDiasBrightness(val)


def setFlash(val):
    p1.setFlashBrightness(val)


### DEBUG ###
if __name__ == "__main__":
    # initialize i2c and ncp5623
    time.sleep(0.1)

    if(0):

        for dc in range(0, 101, 5):    # Loop 0 to 100 stepping dc by 5 each loop
            p1.setFlashBrightness(dc)
            p1.setDiasBrightness(dc)
            # wait .05 seconds at current LED brightness
            time.sleep(0.2)
            print(dc)

        for dc in range(95, 0, -5):    # Loop 95 to 5 stepping dc down by 5 each loop
            p1.setFlashBrightness(dc)
            p1.setDiasBrightness(dc)
            # wait .05 seconds at current LED brightness
            time.sleep(0.2)

    else:
        p1.setFlashBrightness(0)
        p1.setDiasBrightness(0)
