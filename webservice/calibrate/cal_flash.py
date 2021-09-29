"""
Callibrate the light from the flash led
. create light correction mask on server
"""

import os
from io import BytesIO
from time import sleep
from shutil import rmtree
#import base64
import json
from flask import Blueprint #, render_template, request, Markup
from picamera import PiCamera
from hw.led_control import set_dias, set_flash #, get_dias, get_flash
from send2server import send_files

# sensor modes
# mode	Resolution 	Aspect 	Framerates 	    Video 	Image 	FoV 	Binning
# 1 	1920x1080 	16:9 	1 < fps <= 30 	    x 	  	    Partial None
# 2 	2592x1944 	4:3 	1 < fps <= 15 	    x 	    x 	Full 	None
# 3 	2592x1944 	4:3 	1/6 <= fps <= 1 	x 	    x 	Full 	None
# 4 	1296x972 	4:3 	1 < fps <= 42 	    x 	    	Full 	2x2
# 5 	1296x730 	16:9 	1 < fps <= 49 	    x 	    	Full 	2x2
# 6 	640x480 	4:3 	42 < fps <= 60 	    x 	    	Full 	4x4
# 7 	640x480 	4:3 	60 < fps <= 90 	    x 	    	Full 	4x4

_DEBUG = False
CALIB_FOLDER = "/tmp/flashcalib/"
SETLE_TIME = 2
STD_FLASH_VALUE = 0.1

calibrate_flash = Blueprint('calibrate2', __name__, url_prefix='/calibrate')

def capture_picture(mycamera):
    fd1 = BytesIO()
    mycamera.capture(fd1, format='jpeg', use_video_port=False)
    fd1.seek(0)
    return fd1

def write_picture_info( filename, info):
    with open(filename, 'w', encoding="UTF8") as outfile:
        json.dump(info, outfile)

def fix_exposure(mycamera):
    mycamera.shutter_speed = mycamera.exposure_speed
    mycamera.exposure_mode = 'off'
def auto_exposure(mycamera):
    mycamera.exposure_mode = "auto"

def get_exposure_info(camera):
    strg = f"ExposureSpeed: {camera.exposure_speed/1000000:5.3f} sec Gain: Analog: {camera.analog_gain} Digital: {camera.digital_gain} = {float(camera.analog_gain * camera.digital_gain):5.3f} "

    return strg

def d_exposure_info(camera, info=""):
    if _DEBUG:
        print(info, get_exposure_info(camera))

@calibrate_flash.route('/flash_led', methods=['GET', 'POST'])
def flash_led():
    use_video_port = True
    set_dias(0)
    set_flash(0)
    rmtree(CALIB_FOLDER, ignore_errors=True)
    os.makedirs(CALIB_FOLDER, exist_ok=True, mode=0o777)
    mycamera = PiCamera(sensor_mode=2, resolution=(2592,1944))
    #mycamera = PiCamera(sensor_mode=2, resolution=(1296,972))
    #camera.resolution =(640,480)
    #mycamera.resolution ='HD'
    sleep(SETLE_TIME)
    mycamera.capture(CALIB_FOLDER+'color.jpg', use_video_port=use_video_port)
    d_exposure_info(mycamera,"color")
    set_flash(1)
    sleep(SETLE_TIME)
    mycamera.capture(CALIB_FOLDER+'flash10.jpg', use_video_port=use_video_port)
    d_exposure_info(mycamera,"flash10")
    set_flash(STD_FLASH_VALUE)
    sleep(SETLE_TIME)
    mycamera.capture(CALIB_FOLDER+'flash01.jpg', use_video_port=use_video_port)
    d_exposure_info(mycamera,"flash01")
    set_flash(0.05)
    sleep(SETLE_TIME)
    mycamera.capture(CALIB_FOLDER+'flash005.jpg', use_video_port=use_video_port)
    d_exposure_info(mycamera,"flash005")
    fix_exposure(mycamera)
    #nolight
    set_flash(0)
    sleep(SETLE_TIME)
    mycamera.capture(CALIB_FOLDER+'nolight.jpg', use_video_port=use_video_port)
    d_exposure_info(mycamera,"nolight")
    auto_exposure(mycamera)
    sleep(SETLE_TIME)
    mycamera.capture(CALIB_FOLDER+'nolight0.jpg', use_video_port=use_video_port)
    d_exposure_info(mycamera,"nolight0")
    sleep(SETLE_TIME)
    mycamera.color_effects = (128,128)
    set_flash(STD_FLASH_VALUE)
    mycamera.capture(CALIB_FOLDER+'black_white.jpg', use_video_port=use_video_port)
    d_exposure_info(mycamera,"black white")
    # standard billede
    mycamera.resolution = (160, 160)
    mycamera.color_effects = None
    sleep(SETLE_TIME)
    mycamera.capture(CALIB_FOLDER+'standard.jpg', use_video_port=use_video_port)
    d_exposure_info(mycamera,"standard")
    mycamera.close()
    set_flash(0)
    filelist = [CALIB_FOLDER+'color.jpg',
                CALIB_FOLDER+'flash10.jpg', CALIB_FOLDER+'flash01.jpg', CALIB_FOLDER+'flash005.jpg',
                CALIB_FOLDER+'nolight.jpg', CALIB_FOLDER+'nolight0.jpg',
                CALIB_FOLDER+'black_white.jpg', CALIB_FOLDER+'standard.jpg']

    param = {"cmd": "calflash"}
    res = send_files(filelist, post_data=param, timeout=180)
    if _DEBUG:
        print (res)
    if res:
        return res
    return "Det gik ikke så godt"
