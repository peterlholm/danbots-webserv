import os
from io import BytesIO
from time import sleep
import base64
import json
from flask import Blueprint, render_template, request, Markup
#from requests.api import post # Response, send_file,
from camera import init_camera, warm_up, CameraSettings, get_exposure_info, get_picture_info_json, get_white_balance, fix_exposure, auto_exposure
from hw.led_control import set_dias, set_flash, get_dias, get_flash
from send2server import send_files

calibrate = Blueprint('calibrate', __name__, url_prefix='/calibrate')

def capture_picture(mycamera):
    fd1 = BytesIO()
    mycamera.capture(fd1, format='jpeg', use_video_port=False)
    fd1.seek(0)
    return fd1

def write_picture_info( filename, info):
    with open(filename, 'w') as outfile:
        json.dump(info, outfile)

@calibrate.route('/test', methods=['GET', 'POST'])
def test():
    mycamera = init_camera()
    mycamera.resolution =(640,480)
    warm_up(mycamera)
    settings = CameraSettings(mycamera)
    dias = None
    flash = None
    if request.method == 'POST':
        print(request.form)
        settings.contrast = int(request.form['contrast'])
        settings.brightness = int(request.form['brightness'])
        settings.saturation = int(request.form['saturation'])
        settings.iso = int(request.form['iso'])
        settings.exposure_compensation = int(request.form['exposure_compensation'])
        settings.exposure_mode = request.form['exposure_mode']
        settings.awb_mode = request.form['awb_mode']
        settings.sharpness = int(request.form['sharpness'])
        settings.meter_mode = request.form['meter_mode']
        settings.drc_strength = request.form['drc_strength']
        settings.resolution = request.form['resolution']
        settings.shutter_speed = int(request.form['shutter_speed'])*1000
        dias = request.form.get('dias')
        flash = request.form.get('flash')
    print ("Flash", flash)
    print ("Dias", dias)
    fd = capture_picture(mycamera)
    exposure1 = Markup(get_exposure_info(mycamera) + "<br>" + get_white_balance(mycamera))
    img1 = base64.b64encode(fd.getvalue()).decode()
    settings.set()
    mysettings = "Camera: " + settings.str()
    if flash:
        set_flash(True)
    if dias:
        set_dias(True)
    warm_up(mycamera)
    fd2 = capture_picture(mycamera)
    exposure2 = Markup(get_exposure_info(mycamera)+ "<br>" + get_white_balance(mycamera) + " " + mysettings)
    img2 = base64.b64encode(fd2.getvalue()).decode()
    mycamera.close()
    set_flash(False)
    set_dias(False)
    return render_template('calibrate.html', header="Calibrate", img1=img1, img2=img2, exposure1=exposure1,exposure2=exposure2)

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
    sleeptime = 1
    os.makedirs("/tmp/calib", exist_ok=True)
    mycamera = init_camera()
    #camera.resolution =(640,480)
    mycamera.resolution ='HD'
    set_dias(0)
    set_flash(0)
    warm_up(mycamera)
    #normal
    mycamera.capture('/tmp/calib/color.png', use_video_port=False)
    #print(get_picture_info_json(mycamera))
    mycamera.capture('/tmp/calib/color.jpg', use_video_port=False)
    write_picture_info("/tmp/calib/color.json", get_picture_info_json(mycamera))
    #dias
    set_dias(1)
    sleep(sleeptime)
    mycamera.capture('/tmp/calib/dias.png', use_video_port=False)
    mycamera.capture('/tmp/calib/dias.jpg', use_video_port=False)
    write_picture_info("/tmp/calib/dias.json", get_picture_info_json(mycamera))
    #full flash
    set_dias(0)
    set_flash(1)
    sleep(sleeptime)
    mycamera.capture('/tmp/calib/flash.png', use_video_port=False)
    mycamera.capture('/tmp/calib/flash.jpg', use_video_port=False)
    write_picture_info("/tmp/calib/flash.json", get_picture_info_json(mycamera))
    fix_exposure(mycamera)
    #dark
    set_flash(0)
    sleep(sleeptime)
    mycamera.capture('/tmp/calib/nolight.png', use_video_port=False)
    mycamera.capture('/tmp/calib/nolight.jpg', use_video_port=False)
    write_picture_info("/tmp/calib/nolight.json", get_picture_info_json(mycamera))
    auto_exposure(mycamera)
    #low flash
    set_dias(0)
    set_flash(0.1)
    sleep(sleeptime)
    mycamera.capture('/tmp/calib/flash01.png', use_video_port=False)
    mycamera.capture('/tmp/calib/flash01.jpg', use_video_port=False)
    write_picture_info("/tmp/calib/flash01.json", get_picture_info_json(mycamera))
    fix_exposure(mycamera)
    set_flash(0)
    sleep(sleeptime)
    mycamera.capture('/tmp/calib/nolight01.png', use_video_port=False)
    mycamera.capture('/tmp/calib/nolight01.jpg', use_video_port=False)
    write_picture_info("/tmp/calib/nolight01.json", get_picture_info_json(mycamera))
    auto_exposure(mycamera)
    mycamera.close()
    filelist = ['/tmp/calib/color.png',
                '/tmp/calib/color.jpg', '/tmp/calib/color.json',
                '/tmp/calib/dias.png', '/tmp/calib/dias.jpg', '/tmp/calib/dias.json',
                '/tmp/calib/flash.png', '/tmp/calib/flash.jpg', '/tmp/calib/flash.json',
                '/tmp/calib/nolight.png', '/tmp/calib/nolight.jpg', '/tmp/calib/nolight.json',
                '/tmp/calib/flash01.png', '/tmp/calib/flash01.jpg', '/tmp/calib/flash01.json',
                '/tmp/calib/nolight01.png', '/tmp/calib/nolight01.jpg', '/tmp/calib/nolight01.json']

    param = {"cmd": "calibrate"}
    res = send_files(filelist, post_data=param)
    if res:
        print("det gik godt")
    else:
        print("det gik skidt")
    return "alt gik godt"
