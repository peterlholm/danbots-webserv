""" camera module for scanning """
#from sys import platform
from time import sleep
from picamera import PiCamera   # pylint: disable=import-error
from webservice_config import MINFRAMERATE, MAXFRAMERATE, WARMUP_TIME, HEIGHT, WIDTH, ZOOM

# python: disable=unresolved-import,import-error,line-too-long

_DEBUG = False

def myzoom(val):
    "Convert from float to tuple for camera"
    #print ("myzoom", val)
    dif =1-val
    #print(d)
    res = (dif/2,dif/2,1-dif,1-dif)
    #print(res)
    return res

class CameraSettings:   # pylint: disable=too-many-instance-attributes
    "Class for camera settings"
    camera = None
    contrast = 0
    brightness = 50
    saturation = 0
    iso = None
    exposure_compensation = 0
    exposure_mode = 'auto'
    awb_mode = 'flash'
    sharpness = 0
    meter_mode = 'average'
    drc_strength = 'off'
    resolution = 'VGA'
    shutter_speed = 0
    zoom = ZOOM

    def __init__(self, camera):
        self.camera = camera
        #self.reset()

    def set(self):
        "initialisation"
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
        #print ("set", self.zoom)
        #myzoom(self.zoom)
        #self.camera.zoom = (1.0-self.zoom, 1.0-self.zoom, self.zoom, self.zoom)

    def reset(self):
        "Reset settings"
        print ("resetting")
        self.camera.contrast = 0
        self.camera.brightness = 50
        self.camera.saturation = 0
        self.iso = None
        self.exposure_compensation = 0
        self.exposure_mode = 'auto'
        self.awb_mode = 'flash'
        self.sharpness = 0
        self.meter_mode = 'average'
        self.drc_strength = 'off'
        self.resolution = 'VGA'
        self.shutter_speed = 0
        self.zoom = 1

    def str(self):
        "return settings as string"
        # return "Contrast: {} Brigthness: {} Saturation: {} Iso: {}
        # Exposure Compensation: {} ".format(
        #     self.camera.contrast, self.camera.brightness, self.camera.saturation,
        #  self.camera.iso, self.exposure_compensation)
        return f"Contrast: {self.camera.contrast} Brigthness: {self.camera.brightness} Saturation: {self.camera.saturation} Iso: {self.camera.iso} Exposure Compensation: {self.exposure_compensation}"

    def set_str(self):
        "return short settings"
        return "Contrast: {self.contrast} Brigthness: {self.brightness} Saturation: {self.saturation}"

def init_camera():
    "camera standard initialisation"
    camera = PiCamera(resolution='HD')
    camera.awb_mode = 'flash'
    camera.framerate_range =(MINFRAMERATE, MAXFRAMERATE)
    camera.resolution = (WIDTH, HEIGHT)
    #camera.resolution =(2592,1944)(1280,720)(640,480)(160,160)
    camera.zoom = myzoom(ZOOM)
    #print (camera.zoom)
    #camera.meter_mode = 'spot' # average spot backlit matrix
    return camera

def warm_up():
    "give time for callibaration of exposure"
    sleep(WARMUP_TIME)

def fix_exposure(mycamera):
    "fix the current iso, shutter, gain but NOT awb setting"
    #mycamera.iso = 800
    if _DEBUG:
        print ("Fixing exposure at", get_exposure_info(mycamera))
    mycamera.shutter_speed = mycamera.exposure_speed
    mycamera.exposure_mode = 'off'
    #g = mycamera.awb_gains
    #mycamera.awb_mode = 'off'
    #mycamera.awb_gains = g
    if _DEBUG:
        print ("Fixed exposure at", get_exposure_info(mycamera))

def auto_exposure(mycamera):
    "set auto exposure on"
    mycamera.iso = 0
    mycamera.shutter_speed = 0
    mycamera.exposure_mode = 'auto'
    mycamera.awb_mode = 'auto'

def get_picture_info(camera):
    "get the picture info from last picture"
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
    "get picture info in json format"
    info = get_picture_info(camera)
    info['analog_gain'] =float(info['analog_gain'])
    info['digital_gain'] =float(info['digital_gain'])
    info['awb_gains'] =(float(info['awb_gains'][0]),float(info['awb_gains'][1]))
    info['framerate'] =float(info['framerate'])
    info['framerate_range'] = None
    info['exposure_speed'] = info['exposure_speed'] / 1000000.0
    return info

def get_exposure_info(camera):
    """Get the exposure info as string"""
    exposure_speed = camera.exposure_speed
    analog_gain = float(camera.analog_gain)
    digital_gain = float(camera.digital_gain)
    strg = f"ExposureSpeed: {exposure_speed/1000000:5.3f} sec Gain: Analog: {analog_gain} Digital: {digital_gain} = {float(analog_gain * digital_gain):5.3f}"
    return strg


def get_exposure_info_dict(camera):
    """Get the exposure info as string"""
    exposure_speed = float(camera.exposure_speed)
    analog_gain = float(camera.analog_gain)
    digital_gain = float(camera.digital_gain)
    exp = { "ExposureSpeed": exposure_speed/1000000, "AnalogGain": analog_gain, "DigitalGain": digital_gain, "TotalGain": analog_gain * digital_gain}
    return exp

def get_white_balance(camera):
    "get white balance as string"
    return f"WhiteBalance: R: {float(camera.awb_gains[0]):5.3f} B: {float(camera.awb_gains[1]):5.3f}"

def get_camera_settings(camera):
    "get camera settings as string"
    #strg = "ExposureSpeed: {:5.3f} sec(max {:5.1f}  pic/sec)\r\n".format(camera.exposure_speed/1000000, 1000000/camera.exposure_speed)
    strg = f"ExposureSpeed: {camera.exposure_speed/1000000:5.3f} sec\r\n"
    strg += "Gain: analog " + str(camera.analog_gain) + " digital " + str(camera.digital_gain) + "\r\n"
    strg += f"Brightness {camera.brightness:5.3f} Contrast {camera.contrast:5.3f}\r\n"
    strg += f"Denoise {camera.image_denoise:5.3f} Sharpness {camera.sharpness:5.3f}\r\n"
    strg += "Mode: " + str(camera.sensor_mode) + " ISO: " + str(camera.iso) + "\r\n"
    strg += "FrameRate: " + str(camera.framerate) + "\r\n"
    strg += "FrameRateRange: " + str(camera.framerate_range) + "\r\n"
    strg += "PictureSize: " + str(camera.resolution) + "\r\n"
    return strg

def print_settings(camera):
    "get picture settings as string"
    strg = f"ExposureSpeed: {camera.exposure_speed/1000000:5.3f} sec(max {1000000/camera.exposure_speed:5.1f}  pic/sec)<br>"
    strg += "FrameRate: " + str(camera.framerate) + "<br>"
    strg += "FrameRateRange: " + str(camera.framerate_range) + "<br>"
    strg += "PictureSize: " + str(camera.resolution) + "<br>"
    return strg

def calibrate_picture(camera):
    "get callibration info - ??"
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
