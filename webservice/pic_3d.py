"""
Module for management of 3d scans
"""
from datetime import datetime
from io import BytesIO, StringIO
from time import sleep
import json
from flask import Blueprint, Response, request
from camera import auto_exposure, fix_exposure, get_exposure_info, get_exposure_info_dict, init_camera, warm_up, CameraSettings
from send2server import send_api_request, post_file_objects # , post_file_object, get_camera_settings
from send_files import  send_mem_files, save_mem_files, send_file_objects #, send_mem_files_bg send_start, send_stop,API_START,
from hw.led_control import set_flash, set_dias
from webservice_config import CAPTURE_3D, HEIGHT, WIDTH, DEVICEID, myconfig
from webservice_config import COMPUTE_SERVER


_DEBUG = myconfig.getboolean('capture_3d','debug',fallback=False)

DIAS_LEVEL = float(CAPTURE_3D['dias'])                  # light level for dias
FLASH_LEVEL = float(CAPTURE_3D['flash'])                # light level for flash
CAPTURE_DELAY = float(CAPTURE_3D['capture_delay'])      # delay to setle light meter
NUMBER_PICTURES = int(CAPTURE_3D['number_pictures'])
PICTURE_INTERVAL = float(CAPTURE_3D['picture_interval']) # delay between pictures
EXPOSURE_COMPENSATION = int(CAPTURE_3D['exposure_compensation'])
JPEG_QUALITY = 100
TESTINFO = True     # send exposure info with images

def led_off():
    set_flash(0)
    set_dias(0)

def init_3d_camera(settings):
    """ initialize for 3d capture """
    if _DEBUG:
        print("Cpture3d settings", CAPTURE_3D)
    settings.resolution=(WIDTH, HEIGHT)
    settings.exposure_compensation=EXPOSURE_COMPENSATION
    settings.set()
    if _DEBUG:
        print("Camera Settings:", settings.str())
    return settings

def send_start():
    return send_api_request("start3d", url=COMPUTE_SERVER)

def send_stop():
    return send_api_request("stop3d", url=COMPUTE_SERVER)

def send_picture(fd1, i, info=None):
    # used by /3d
    send_mem_files(fd1, "picture"+str(i), params={'cmd':'picture','pictureno': str(i)}, info=info )
    if _DEBUG:
        files = [('pic1.jpg',fd1[0]),('pic2.jpg',fd1[1]),('pic3.jpg', fd1[2])]
        send_file_objects(files,data={"info":"debug3d", "no": i})

def send_dias(fd1, i, info=None):
    # used by /3dias
    save_mem_files(fd1, "picture"+str(i), params={'cmd':'picture','pictureno': str(i)}, info=info )

def get_picture_infoset(camera):
    # get picture and exposure info
    # used by /3d
    if TESTINFO:
        flash_exp = get_exposure_info_dict(camera)
    if _DEBUG:
        print ("Flash", get_exposure_info(camera))
    set_flash(False)
    set_dias(DIAS_LEVEL)
    fd2 = BytesIO()
    sleep(CAPTURE_DELAY)
    if TESTINFO:
        dias_exp = get_exposure_info_dict(camera)
    if _DEBUG:
        print ("Dias", get_exposure_info(camera))
    camera.capture(fd2, format='jpeg', use_video_port=True, quality=JPEG_QUALITY)
    fd2.truncate()
    fd2.seek(0)
    fix_exposure(camera)
    set_dias(False)
    sleep(CAPTURE_DELAY)
    if TESTINFO:
        dark_exp = get_exposure_info_dict(camera)
    if _DEBUG:
        print ("Dark", get_exposure_info(camera))
    fd3 = BytesIO()
    camera.capture(fd3, format='jpeg', use_video_port=True, quality=JPEG_QUALITY)
    fd3.truncate()
    fd3.seek(0)
    auto_exposure(camera)
    if TESTINFO:
        info = { "color": flash_exp, "dias": dias_exp, "nolight": dark_exp }
        #print(info)
        fdinfo = StringIO(json.dumps(info, indent=4))
    fileobj = [ ("dias.jpg",fd2),("nolight.jpg", fd3),("pict_info.json", fdinfo)]
    return fileobj

def get_picture_set(camera):
    # used by /3d
    if _DEBUG:
        print ("Flash", get_exposure_info(camera))
    set_flash(False)
    set_dias(DIAS_LEVEL)
    fd2 = BytesIO()
    sleep(CAPTURE_DELAY)
    if _DEBUG:
        print ("Dias", get_exposure_info(camera))
    camera.capture(fd2, format='jpeg', use_video_port=True, quality=JPEG_QUALITY)
    fd2.truncate()
    fd2.seek(0)
    fix_exposure(camera)
    set_dias(False)
    sleep(CAPTURE_DELAY)
    if _DEBUG:
        print ("Dark", get_exposure_info(camera))
    fd3 = BytesIO()
    camera.capture(fd3, format='jpeg', use_video_port=True, quality=JPEG_QUALITY)
    fd3.truncate()
    fd3.seek(0)
    auto_exposure(camera)
    #set_flash(FLASH_LEVEL)
    return (fd2, fd3)

def get_pictures(camera):
    # return a picture for MPEG and send Captured Images to  compute server
    # used by /3d
    fd1 = BytesIO()
    i=1
    pic_no = 1
    start = datetime.now()
    if PICTURE_INTERVAL==0:
        pic_modolu=1
    else:
        pic_modolu = int(PICTURE_INTERVAL*10)
    if _DEBUG:
        print("pic_modulo", pic_modolu)
    try:
        while True:
            camera.capture(fd1, format='jpeg', use_video_port=True, quality=JPEG_QUALITY)
            fd1.truncate()
            fd1.seek(0)
            pic = fd1.read()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + pic + b'\r\n')
            fd1.seek(0)
            if i % pic_modolu == 0:
                # get exposure info
                #color_info = get_picture_info_json(camera)
                #(fd2, fd3) = get_picture_set(camera)
                #send_picture([fd1,fd2,fd3], pic_no)
                set_flash(FLASH_LEVEL)
                sleep(CAPTURE_DELAY)
                fdlist = get_picture_infoset(camera)
                fd1.seek(0)
                fdlist.append(['color.jpg', fd1])
                #print(fdlist)
                post_file_objects("scan3d", fdlist, post_data={'pictureno': pic_no})
                fd1.seek(0)
                pic_no = pic_no+1
                if pic_no>NUMBER_PICTURES:
                    break
                set_flash(FLASH_LEVEL)
            i=i+1
            #sleep(0)
    finally:
        stop = datetime.now()
        if _DEBUG:
            print(f"Closing: {i/((stop-start).total_seconds()):2.1f} Billeder/sek")
        camera.close()
        led_off()
        send_stop()

def get_dias(camera, number_pictures=None):
    # used by /3dias
    if not number_pictures:
        number_pictures = NUMBER_PICTURES
    fd1 = BytesIO()
    i=1
    pic_no = 1
    start = datetime.now()
    if PICTURE_INTERVAL==0:
        pic_modolu=1
    else:
        pic_modolu = int(PICTURE_INTERVAL*10)
    try:
        while True:
            camera.capture(fd1, format='jpeg', use_video_port=True, quality=JPEG_QUALITY)
            fd1.truncate()
            fd1.seek(0)
            pic = fd1.read()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + pic + b'\r\n')
            fd1.seek(0)
            if i % pic_modolu == 0:
                print (pic_no, get_exposure_info(camera))
                (fd2, fd3) = get_picture_set(camera)
                send_dias([fd1,fd2,fd3], pic_no)
                fd1.seek(0)
                pic_no = pic_no+1
                if pic_no>number_pictures:
                    break
            i=i+1
            sleep(0)
    finally:
        stop = datetime.now()
        if _DEBUG:
            print(f"Closing: {i/((stop-start).total_seconds()):2.1f} Billeder/sek")
        camera.close()
        led_off()
        send_stop()

# routes

pic3d = Blueprint('3d', __name__, url_prefix='/3d')

@pic3d.route('/3d')
def cam():
    # send 3d set to compute
    # num = request.args.get('number')
    # print(num)

    server_up = send_start()
    if not server_up:
        return '{"result": 0, "reason": "no connection to compute server"}'
    camera = init_camera()
    camera.resolution =(160,160)
    camera.framerate_range =(10,10)
    cam_settings = CameraSettings(camera)
    init_3d_camera(cam_settings)
    size = request.args.get('size', None)
    if size:
        camera.resolution =(int(size),int(size))
    # start
    set_dias(False)
    set_flash(FLASH_LEVEL)
    warm_up()
    warm_up()
    return Response(get_pictures(camera),mimetype='multipart/x-mixed-replace; boundary=frame')

@pic3d.route('/3dp')
def camp():
    # send 3d set to compute - without display
    #num = request.args.get('number')
    send_start()
    camera = init_camera()
    camera.resolution =(160,160)
    #camera.framerate_range =(10,10)
    cam_settings = CameraSettings(camera)
    init_3d_camera(cam_settings)
    size = request.args.get('size', None)
    if size:
        camera.resolution =(int(size),int(size))
    set_dias(False)
    set_flash(FLASH_LEVEL)
    warm_up()
    fd1 = BytesIO()
    camera.capture(fd1, format='jpeg', use_video_port=True, quality=JPEG_QUALITY)
    fd1.truncate()
    fd1.seek(0)
    (fd2, fd3) = get_picture_set(camera)
    send_picture([fd1,fd2,fd3], 1)
    camera.close()
    led_off()
    send_stop()
    res = { "device": DEVICEID }
    return res

@pic3d.route('/3dias')
def cam3dias():
    # send a serie of pictures
    send_start()
    camera = init_camera()
    camera.resolution =(160,160)
    camera.framerate_range =(10,10)
    cam_settings = CameraSettings(camera)
    init_3d_camera(cam_settings)
    size = request.args.get('size', None)
    if size:
        camera.resolution =(int(size),int(size))
    print (get_exposure_info(camera))
    set_dias(False)
    set_flash(True)
    print (get_exposure_info(camera))
    warm_up()
    print (get_exposure_info(camera))
    warm_up()
    print (get_exposure_info(camera))
    warm_up()
    print (get_exposure_info(camera))

    return Response(get_dias(camera, 10),mimetype='multipart/x-mixed-replace; boundary=frame')
