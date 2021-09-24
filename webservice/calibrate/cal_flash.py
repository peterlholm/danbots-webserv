"""
Callibrate the light from the flash led
. create light correction mask on server
"""

import os
from io import BytesIO
from time import sleep
#import base64
import json
from flask import Blueprint #, render_template, request, Markup
from picamera import PiCamera

#from requests.api import post # Response, send_file,

#from camera import init_camera, warm_up, CameraSettings, get_exposure_info, get_picture_info_json, get_white_balance, fix_exposure, auto_exposure
#from .camera import fix_exposure
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
    # fix the current iso, shutter, gain.. setting
    #mycamera.iso = 800
    #warm_up(mycamera)
    #print ("Fixint at", get_exposure_info(mycamera))
    mycamera.shutter_speed = mycamera.exposure_speed
    mycamera.exposure_mode = 'off'
    #g = mycamera.awb_gains
    #mycamera.awb_mode = 'off'
    #mycamera.awb_gains = g
    #print ("Fixed at", get_exposure_info(mycamera))

@calibrate_flash.route('/flash_led', methods=['GET', 'POST'])
def flash_led():
    use_video_port = False
    set_dias(0)
    set_flash(0)
    calib_folder = "/tmp/flashcalib/"
    setletime = 5
    os.makedirs(calib_folder, exist_ok=True)
    mycamera = PiCamera(sensor_mode=2, resolution=(2592,1944))
    #camera.resolution =(640,480)
    #mycamera.resolution ='HD'
    sleep(setletime)
    mycamera.capture(calib_folder+'color.jpg', use_video_port=use_video_port)
    set_flash(1)
    sleep(setletime)
    mycamera.capture(calib_folder+'flash10.jpg', use_video_port=use_video_port)
    set_flash(0.1)
    sleep(setletime)
    mycamera.capture(calib_folder+'flash01.jpg', use_video_port=use_video_port)
    set_flash(0.05)
    sleep(setletime)
    mycamera.capture(calib_folder+'flash005.jpg', use_video_port=use_video_port)
    fix_exposure(mycamera)
    #dark
    set_flash(0)
    sleep(setletime)
    mycamera.capture(calib_folder+'nolight.jpg', use_video_port=use_video_port)
    #auto_exposure(mycamera)
    mycamera.close()

    filelist = [calib_folder+'color.jpg',
                calib_folder+'flash10.jpg', calib_folder+'flash01.jpg',
                calib_folder+'flash005.jpg', calib_folder+'nolight.jpg']

    param = {"cmd": "calflash"}
    res = send_files(filelist, post_data=param)
    print (res)
    if res:
        return res
    return "alt gik godt"
