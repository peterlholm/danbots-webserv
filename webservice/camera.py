from sys import platform
from time import sleep
from webservice_config import MINFRAMERATE, MAXFRAMERATE, WARMUP_TIME, HEIGHT, WIDTH, ZOOM

# python: disable=unresolved-import,import-error


from picamera import PiCamera   # pylint: disable=import-error

def myzoom(val):
    print ("myzoom", val)
    d =1-val
    print(d)
    res = (d/2,d/2,1-d,1-d)
    print(res)
    return res
    

class CameraSettings:   # pylint: disable=too-many-instance-attributes
    camera = None
    contrast = 0
    brightness = 50
    saturation = 0
    iso = None
    exposure_compensation = 0
    exposure_mode = 'auto'
    awb_mode = 'auto'
    sharpness = 0
    meter_mode = 'average'
    drc_strength = 'off'
    resolution = 'VGA'
    shutter_speed = 0
    zoom = ZOOM
    print ("zoom", zoom)

    def __init__(self, camera):
        self.camera = camera
        #self.reset()

    def set(self):
        self.camera.contrast = self.contrast
        self.camera.brightness = self.brightness
        self.camera.saturation = self.saturation
        if self.iso:
            self.camera.iso = self.iso
        self.camera.exposure_compensation = self.exposure_compensation
        self.camera.exposure_mode = self.exposure_mode
        self.camera.awb_mode = self.awb_mode
        self.camera.sharpness = self.sharpness
        self.camera.meter_mode = self.meter_mode
        self.camera.drc_strength = self.drc_strength
        self.camera.resolution = self.resolution
        self.camera.shutter_speed = self.shutter_speed
        print ("set", self.zoom)
        myzoom(self.zoom)
        #self.camera.zoom = (1.0-self.zoom, 1.0-self.zoom, self.zoom, self.zoom)

    def reset(self):
        print ("resetting")
        self.camera.contrast = 0
        self.camera.brightness = 50
        self.camera.saturation = 0
        self.iso = None
        self.exposure_compensation = 0
        self.exposure_mode = 'auto'
        self.awb_mode = 'auto'
        self.sharpness = 0
        self.meter_mode = 'average'
        self.drc_strength = 'off'
        self.resolution = 'VGA'
        self.shutter_speed = 0
        self.zoom = 1

    def str(self):
        return "Contrast: {} Brigthness: {} Saturation: {} Iso: {} Exposure Compensation: {} ".format(
            self.camera.contrast, self.camera.brightness, self.camera.saturation,  self.camera.iso, self.exposure_compensation)

    def set_str(self):
        return "Contrast: {} Brigthness: {} Saturation: {}".format(self.contrast, self.brightness, self.saturation)

def init_camera():
    camera = PiCamera(resolution='HD')
    camera.framerate_range =(MINFRAMERATE, MAXFRAMERATE)
    camera.resolution = (WIDTH, HEIGHT)
    #camera.resolution =(2592,1944)(1280,720)(640,480)(160,160)

    print("init zoom",camera.zoom)
    #val = (0.15,0.15,0.7,0.70)
    #camera.zoom=val

    myzoom(ZOOM)
    #camera.zoom = (1.0-ZOOM, 1.0-ZOOM, ZOOM, ZOOM)
    print (camera.zoom)
    #camera.meter_mode = 'spot' # average spot backlit matrix
    return camera

def warm_up(camera):
    sleep(WARMUP_TIME)

def fix_exposure(mycamera):
    # fix the current iso, shutter, gain.. setting
    #mycamera.iso = 800
    #warm_up(mycamera)
    print ("Fixint at", get_exposure_info(mycamera))
    mycamera.shutter_speed = mycamera.exposure_speed
    mycamera.exposure_mode = 'off'
    g = mycamera.awb_gains
    #mycamera.awb_mode = 'off'
    #mycamera.awb_gains = g
    print ("Fixed at", get_exposure_info(mycamera))

def auto_exposure(mycamera):
    mycamera.iso = 0
    mycamera.shutter_speed = 0
    mycamera.exposure_mode = 'auto'
    mycamera.awb_mode = 'auto'

def get_picture_info(camera):
    info = { 'analog_gain': camera.analog_gain,
     'digital_gain': camera.digital_gain,
     'awb_gains': camera.awb_gains,
        'awb_mode': camera.awb_mode,
        'brightness': camera.brightness,
        'color_effects': camera.color_effects,
        'contrast': camera.contrast,
        'crop': camera.crop,
        'drc_strength': camera.drc_strength,
        'exif_tags': camera.exif_tags,
        'exposure_compensation': camera.exposure_compensation,
        'exposure_mode': camera.exposure_mode,
        'exposure_speed': camera.exposure_speed,
        'flash_mode': camera.flash_mode,
        'framerate': camera.framerate,
        #'framerate_delta': camera.framerate_delta,
        'framerate_range': camera.framerate_range,
        'image_denoise': camera.image_denoise,
        'image_effect': camera.image_effect,
        'iso': camera.iso,
        'meter_mode': camera.meter_mode,
        'resolution': camera.resolution,
        'revision': camera.revision,
        'saturation': camera.saturation,
        'sensor_mode': camera.sensor_mode,
        'sharpness': camera.sharpness,
        'shutter_speed': camera.shutter_speed,
        'video_denoise': camera.video_denoise,
        'zoom': camera.zoom
    }
    return info

def get_picture_info_json(camera):
    info = get_picture_info(camera)
    info['analog_gain'] =float(info['analog_gain'])
    info['digital_gain'] =float(info['digital_gain'])
    info['awb_gains'] =(float(info['awb_gains'][0]),float(info['awb_gains'][1]))
    info['framerate'] =float(info['framerate'])
    info['framerate_range'] = None
    info['exposure_speed'] = info['exposure_speed'] / 1000000.0
    return info

def get_exposure_info(camera):
    exposure_speed = camera.exposure_speed
    analog_gain = camera.analog_gain
    digital_gain = camera.digital_gain
    strg = ""
    if exposure_speed:
        strg = "ExposureSpeed: {:5.3f} sec (~{:4.1f} pic/sec) ".format(exposure_speed/1000000, 1000000/exposure_speed)
    strg += "Gain: Analog: {} Digital: {} = {:5.3f} ".format(
        analog_gain, digital_gain, float(analog_gain * digital_gain))
    return strg

def get_white_balance(camera):
    return "WhiteBalance: R: {:5.3f} B: {:5.3f}".format(float(camera.awb_gains[0]), float(camera.awb_gains[1]) )

def get_camera_settings(camera):
    #strg = "ExposureSpeed: {:5.3f} sec(max {:5.1f}  pic/sec)\r\n".format(camera.exposure_speed/1000000, 1000000/camera.exposure_speed)
    strg = "ExposureSpeed: {:5.3f} sec\r\n".format(camera.exposure_speed/1000000)
    strg += "Gain: analog " + str(camera.analog_gain) + " digital " + str(camera.digital_gain) + "\r\n"
    strg += "Brightness {:5.3f} Contrast {:5.3f}\r\n".format(camera.brightness,camera.contrast)
    strg += "Denoise {:5.3f} Sharpness {:5.3f}\r\n".format(camera.image_denoise, camera.sharpness)
    strg += "Mode: " + str(camera.sensor_mode) + " ISO: " + str(camera.iso) + "\r\n"
    strg += "FrameRate: " + str(camera.framerate) + "\r\n"
    strg += "FrameRateRange: " + str(camera.framerate_range) + "\r\n"
    strg += "PictureSize: " + str(camera.resolution) + "\r\n"
    return strg

def print_settings(camera):
    strg = "ExposureSpeed: {:5.3f} sec(max {:5.1f}  pic/sec)<br>".format(camera.exposure_speed/1000000, 1000000/camera.exposure_speed)
    strg += "FrameRate: " + str(camera.framerate) + "<br>"
    strg += "FrameRateRange: " + str(camera.framerate_range) + "<br>"
    strg += "PictureSize: " + str(camera.resolution) + "<br>"
    return strg

def calibrate_picture(camera):
    sleep(WARMUP_TIME)
    a_gain = camera.analog_gain
    d_gain = camera.digital_gain
    gain = float(a_gain) * float(d_gain)
    iso = round(gain) * 100
    cal = {
        "exposure_speed": camera.exposure_speed,
        "analog_gain": a_gain,
        "digital_gain": d_gain,
        "gain": float(a_gain) * float(camera.digital_gain),
        "iso": int(iso)
    }
    return cal
