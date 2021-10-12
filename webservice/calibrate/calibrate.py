"""Module for collecting calibration informatin"""
import os
#from io import BytesIO
from time import sleep
#import base64
import json
from flask import Blueprint, render_template, request #, Markup
#from requests.api import post # Response, send_file,
from camera import get_camera_settings, init_camera, warm_up, CameraSettings, get_exposure_info, get_picture_info_json, get_white_balance, fix_exposure, auto_exposure #get_picture_info
from hw.led_control import set_dias, set_flash, get_dias, get_flash
from send2server import send_files
from webservice_config import ZOOM

_DEBUG = False

calibrate = Blueprint('calibrate', __name__, url_prefix='/calibrate')

def write_picture_info( filename, info):
    with open(filename, 'w', encoding="UTF8") as outfile:
        json.dump(info, outfile)

@calibrate.route('/light', methods=['GET', 'POST'])
def light():
    dias = get_dias()
    flash = get_flash()
    if request.method == 'POST':
        print(request.form)
        dias = float(request.form['dias'])
        flash = float(request.form['flash'])
        set_dias(dias)
        set_flash(flash)
    return render_template('light.html', header="Light", dias=dias, flash=flash)

@calibrate.route('/camera', methods=['GET', 'POST'])
def camera():
    sleeptime = 1.5
    os.makedirs("/tmp/calib", mode=0o777, exist_ok=True)
    mycamera = init_camera()
    #mycamera.resolution =(2592,1944)
    set_dias(0)
    set_flash(0)
    warm_up()
    if _DEBUG:
        print(get_camera_settings(mycamera))
    #normal
    mycamera.capture('/tmp/calib/color.png', use_video_port=False)
    if _DEBUG:
        print("Color", get_exposure_info(mycamera))
    mycamera.capture('/tmp/calib/color.jpg', use_video_port=False)
    write_picture_info("/tmp/calib/color.json", get_picture_info_json(mycamera))
    #dias
    set_dias(1)
    sleep(sleeptime)
    mycamera.capture('/tmp/calib/dias.png', use_video_port=False)
    if _DEBUG:
        print("Dias:",get_exposure_info(mycamera))
    mycamera.capture('/tmp/calib/dias.jpg', use_video_port=False)
    write_picture_info("/tmp/calib/dias.json", get_picture_info_json(mycamera))
    #full flash
    set_dias(0)
    set_flash(1)
    sleep(sleeptime)
    mycamera.capture('/tmp/calib/flash.png', use_video_port=False)
    if _DEBUG:
        print("Flash",get_exposure_info(mycamera))
    mycamera.capture('/tmp/calib/flash.jpg', use_video_port=False)
    write_picture_info("/tmp/calib/flash.json", get_picture_info_json(mycamera))
    fix_exposure(mycamera)
    #dark
    set_flash(0)
    sleep(sleeptime)
    mycamera.capture('/tmp/calib/nolight.png', use_video_port=False)
    if _DEBUG:
        print("NoLight", get_exposure_info(mycamera))
    mycamera.capture('/tmp/calib/nolight.jpg', use_video_port=False)
    write_picture_info("/tmp/calib/nolight.json", get_picture_info_json(mycamera))
    auto_exposure(mycamera)
    #low flash
    set_dias(0)
    set_flash(0.1)
    sleep(sleeptime)
    mycamera.capture('/tmp/calib/flash01.png', use_video_port=False)
    if _DEBUG:
        print("Flash01", get_exposure_info(mycamera))
    mycamera.capture('/tmp/calib/flash01.jpg', use_video_port=False)
    write_picture_info("/tmp/calib/flash01.json", get_picture_info_json(mycamera))
    fix_exposure(mycamera)
    set_flash(0)
    sleep(sleeptime)
    mycamera.capture('/tmp/calib/nolight01.png', use_video_port=False)
    mycamera.close()
    filelist = ['/tmp/calib/color.png', '/tmp/calib/color.jpg', '/tmp/calib/color.json',
                '/tmp/calib/dias.png', '/tmp/calib/dias.jpg', '/tmp/calib/dias.json',
                '/tmp/calib/flash.png', '/tmp/calib/flash.jpg', '/tmp/calib/flash.json',
                '/tmp/calib/nolight.png', '/tmp/calib/nolight.jpg', '/tmp/calib/nolight.json',
                '/tmp/calib/flash01.png', '/tmp/calib/flash01.jpg', '/tmp/calib/flash01.json',
                #'/tmp/calib/nolight01.png', '/tmp/calib/nolight01.jpg', '/tmp/calib/nolight01.json'
                ]
    res = send_files(filelist, post_data={"cmd": "calcamera", "sice": 160, "zoom": ZOOM})
    if res:
        return res
    print("det gik skidt", res)
    return '{ "result": "false"}'
