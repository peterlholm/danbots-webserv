from sys import platform
from time import sleep

# python: disable=unresolved-import,import-error

if platform == "linux":
    from picamera import PiCamera   # pylint: disable=import-error
else:
    import pygame
    import pygame.camera # pylint: disable=wrong-import-position
    #from pygame.locals import *

def init_camera():
    if platform=="linux":
        camera = PiCamera()
        camera.framerate_range =(10,30)
        # camera.resolution =(1280,720)
        #camera.resolution =(2592,1944)
        #camera.resolution =(640,480)
        camera.resolution =(150,150)
    else:
        pygame.camera.init()
        camera = pygame.camera.Camera(0,(640,480))
        camera.start()
    return camera

def warm_up(camera):
    sleep(1)
    print ("Camera initial settings")
    print(get_camera_settings(camera))

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
