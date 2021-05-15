from sys import platform
from time import sleep
from webservice_config import MINFRAMERATE, MAXFRAMERATE, WARMUP_TIME, HEIGHT, WIDTH

# python: disable=unresolved-import,import-error

if platform == "linux":
    from picamera import PiCamera   # pylint: disable=import-error
else:
    import pygame
    import pygame.camera # pylint: disable=wrong-import-position
    #from pygame.locals import *

def init_camera():
    if platform=="linux":
        camera = PiCamera(resolution='HD')
        camera.framerate_range =(MINFRAMERATE, MAXFRAMERATE)
        camera.resolution = (WIDTH, HEIGHT)
        # camera.resolution =(1280,720)
        #camera.resolution =(2592,1944)
        #camera.resolution =(640,480)
        #camera.resolution =(160,160)
    else:
        pygame.camera.init()
        camera = pygame.camera.Camera(0,(640,480))
        camera.start()
    return camera

def warm_up(camera):
    sleep(WARMUP_TIME)

def fix_exposure(mycamera):
    # fix the current iso, shutter, gain.. setting
    mycamera.iso = 800
    warm_up(mycamera)
    mycamera.shutter_speed = mycamera.exposure_speed
    mycamera.exposure_mode = 'off'
    g = mycamera.awb_gains
    mycamera.awb_mode = 'off'
    mycamera.awb_gains = g

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

def get_exposure_info(camera):
    exposure_speed = camera.exposure_speed
    analog_gain = camera.analog_gain
    digital_gain = camera.digital_gain
    strg = ""
    if exposure_speed:
        strg = "ExposureSpeed: {:5.3f} sec (~{:4.1f} pic/sec) ".format(exposure_speed/1000000, 1000000/exposure_speed)
    strg += "Gain: Analog: {} Digital: {} = {:5.3f} ".format(
        analog_gain, digital_gain, float(analog_gain * digital_gain))
    strg += "WhiteBalance: R: {:5.3f} B: {:5.3f}".format(
        float(camera.awb_gains[0]), float(camera.awb_gains[1]) )
    return strg

def get_camera_settings(camera):
    strg = "ExposureSpeed: {:5.3f} sec(max {:5.1f}  pic/sec)\r\n".format(camera.exposure_speed/1000000, 1000000/camera.exposure_speed)
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