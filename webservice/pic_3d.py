"""
Module for management of 3d scans
"""
from datetime import datetime
from io import BytesIO, StringIO
from time import sleep, perf_counter
import json
from flask import Blueprint, Response, request
from camera import auto_exposure, fix_exposure, get_exposure_info_dict, init_camera, warm_up, CameraSettings, myzoom
from send2server import send_api_request, post_file_objects, post_file_objects_bg # , post_file_object, get_camera_settings
#from send_files import  send_mem_files, save_mem_files, send_file_objects #, send_mem_files_bg send_start, send_stop,API_START,
from hw.led_control import set_flash, set_dias
from webservice_config import CAPTURE_3D, HEIGHT, WIDTH, myconfig
from webservice_config import COMPUTE_SERVER

_DEBUG = myconfig.getboolean('capture_3d','debug',fallback=False)
_TIMING = False

DIAS_LEVEL = float(CAPTURE_3D['dias'])                  # light level for dias
FLASH_LEVEL = float(CAPTURE_3D['flash'])                # light level for flash
CAPTURE_DELAY = float(CAPTURE_3D['capture_delay'])      # delay to setle light meter
NUMBER_PICTURES = int(CAPTURE_3D['number_pictures'])
PICTURE_INTERVAL = float(CAPTURE_3D['picture_interval']) # delay between pictures
EXPOSURE_COMPENSATION = int(CAPTURE_3D['exposure_compensation'])
JPEG_QUALITY = 85

def led_off():
    "turn both led off"
    set_flash(0)
    set_dias(0)

def init_3d_camera(settings):
    "initialize camerafor 3d capture "
    if _DEBUG:
        print("Cpture3d settings", CAPTURE_3D)
    settings.resolution=(WIDTH, HEIGHT)
    settings.exposure_compensation=EXPOSURE_COMPENSATION
    #settings.drc_strength = 'low', 'high'
    settings.awb_mode = 'flash'
    settings.set()
    if _DEBUG:
        print("Camera Settings:", settings.str())
    return settings

def send_start():
    "send start to server"
    return send_api_request("start3d", url=COMPUTE_SERVER)

def send_stop():
    "send stop to server"
    return send_api_request("stop3d", url=COMPUTE_SERVER)

# def send_picture(fd1, i, info=None):
#     # used by /3d
#     send_mem_files(fd1, "picture"+str(i), params={'cmd':'picture','pictureno': str(i)}, info=info )
#     if _DEBUG:
#         files = [('pic1.jpg',fd1[0]),('pic2.jpg',fd1[1]),('pic3.jpg', fd1[2])]
#         send_file_objects(files,data={"info":"debug3d", "no": i})

# def send_dias(fd1, i, info=None):
#     # used by /3dias
#     save_mem_files(fd1, "picture"+str(i), params={'cmd':'picture','pictureno': str(i)}, info=info )

def get_picture_infoset(camera, picinfo=True):
    "get picture and exposure info used by /3d and return file object to send"
    st1 = perf_counter()
    if picinfo:
        flash_exp = get_exposure_info_dict(camera)
    set_flash(False)
    set_dias(DIAS_LEVEL)
    fd2 = BytesIO()
    sleep(CAPTURE_DELAY)
    if picinfo:
        dias_exp = get_exposure_info_dict(camera)
    camera.capture(fd2, format='jpeg', use_video_port=True, quality=JPEG_QUALITY)
    fix_exposure(camera)
    fd2.truncate()
    fd2.seek(0)
    set_dias(False)
    sleep(CAPTURE_DELAY)
    if picinfo:
        dark_exp = get_exposure_info_dict(camera)
    fd3 = BytesIO()
    camera.capture(fd3, format='jpeg', use_video_port=True, quality=JPEG_QUALITY)
    fd3.truncate()
    fd3.seek(0)
    auto_exposure(camera)
    if picinfo:
        info = { "color": flash_exp, "dias": dias_exp, "nolight": dark_exp }
        fdinfo = StringIO(json.dumps(info, indent=4))
        fileobj = [ ("dias.jpg",fd2),("nolight.jpg", fd3),("pict_info.json", fdinfo)]
    else:
        fileobj = [ ("dias.jpg",fd2),("nolight.jpg", fd3)]
    end = perf_counter()
    if _TIMING:
        print(f"Get_picture_infoset { end-st1 }")
    return fileobj

# def get_picture_set(camera):
#     "get a single set of fringe an nolight used by /3d mm"
#     if _DEBUG:
#         print ("Flash", get_exposure_info(camera))
#     set_flash(False)
#     set_dias(DIAS_LEVEL)
#     fd2 = BytesIO()
#     sleep(CAPTURE_DELAY)
#     if _DEBUG:
#         print ("Dias", get_exposure_info(camera))
#     camera.capture(fd2, format='jpeg', use_video_port=True, quality=JPEG_QUALITY)
#     fd2.truncate()
#     fd2.seek(0)
#     fix_exposure(camera)
#     set_dias(False)
#     sleep(CAPTURE_DELAY)
#     if _DEBUG:
#         print ("Dark", get_exposure_info(camera))
#     fd3 = BytesIO()
#     camera.capture(fd3, format='jpeg', use_video_port=True, quality=JPEG_QUALITY)
#     fd3.truncate()
#     fd3.seek(0)
#     auto_exposure(camera)
#     #set_flash(FLASH_LEVEL)
#     return (fd2, fd3)

def get_pictures(camera, no_pictures=NUMBER_PICTURES, picture_interval=PICTURE_INTERVAL):
    "get mpeg pic stream and send 3d set to server"
    # return a picture for MPEG and send Captured Images to  compute server
    # picture_interval is the interval of frames set to server ????
    # used by /3d
    fd1 = BytesIO()
    i=1
    pic_no = 1
    sstart = datetime.now()
    if picture_interval==0:
        pic_modolu=1
    else:
        pic_modolu = int(picture_interval*10)
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
                if _TIMING:
                    time_start = perf_counter()
                start = datetime.now()
                #set_flash(FLASH_LEVEL)
                #sleep(CAPTURE_DELAY)
                fdlist = get_picture_infoset(camera)
                if _TIMING:
                    time_info = perf_counter()
                    print(f"Take pictures {(time_info-time_start)}")
                fd1.seek(0)
                fdlist.append(['color.jpg', fd1])
                #post_file_objects("scan3d", fdlist, post_data={'pictureno': pic_no})
                post_file_objects_bg("scan3d", fdlist, post_data={'pictureno': pic_no})
                if _TIMING:
                    time_post = perf_counter()
                    print(f" post files time {(time_post-time_info)}")
                fd1.seek(0)
                pic_no = pic_no+1
                if pic_no>no_pictures:
                    break
                set_flash(FLASH_LEVEL)
                sto = datetime.now()
                if _DEBUG:
                    print (" Pictureset time", sto-start)
                if _TIMING:
                    time_end = perf_counter()
                    print(f"Loop time {(time_end-time_start)}")
            i=i+1
    finally:
        sstop = datetime.now()
        if _DEBUG:
            print(f"Closing: {i/((sstop-sstart).total_seconds()):2.1f} displayed pic/sec")
        camera.close()
        led_off()
        send_stop()

def get_test_exposure_pictures(camera, mode="comp"):
    "send pictures with different exposure"
    # return a picture for MPEG and send Captured Images to  compute server
    # but changing exposure
    fd1 = BytesIO()
    i=1
    pic_no = 1
    if mode=="comp":
        compensation = -15
    if mode=="zoom":
        zoom = 0.2
    start = datetime.now()
    if PICTURE_INTERVAL==0:
        pic_modolu=1
    else:
        pic_modolu = int(PICTURE_INTERVAL*10)
    if _DEBUG:
        print("pic_modulo", pic_modolu)
    try:
        while True:
            sleep(CAPTURE_DELAY)
            camera.capture(fd1, format='jpeg', use_video_port=True, quality=JPEG_QUALITY)
            fd1.truncate()
            fd1.seek(0)
            pic = fd1.read()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + pic + b'\r\n')
            fd1.seek(0)
            if i % pic_modolu == 0:
                set_flash(FLASH_LEVEL)
                sleep(CAPTURE_DELAY)
                fdlist = get_picture_infoset(camera)
                fd1.seek(0)
                fdlist.append(['color.jpg', fd1])
                #print(fdlist)
                post_file_objects("scan3d", fdlist, post_data={'pictureno': pic_no})
                fd1.seek(0)
                pic_no = pic_no+1
                if mode=='comp':
                    compensation = compensation+1
                    camera.exposure_compensation = compensation
                if mode=='zoom':
                    zoom = zoom + 0.05
                    rec = myzoom(zoom)
                    camera.zoom = rec
                if pic_no>20:
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

# routes

pic3d = Blueprint('3d', __name__, url_prefix='/3d')

# std 3d stream

@pic3d.route('/3d')
def cam():
    "send 3d set to compute"
    if _DEBUG:
        print(request.args)
    no_pictures = request.args.get('no_pictures', NUMBER_PICTURES, type=int)
    picture_interval = request.args.get('picture_interval', PICTURE_INTERVAL, type=float)
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
    return Response(get_pictures(camera, no_pictures=no_pictures, picture_interval=picture_interval),mimetype='multipart/x-mixed-replace; boundary=frame')

@pic3d.route('/3dexptest')
def exposuretest():
    "generate stream with different exposure"
    server_up = send_start()
    if not server_up:
        return '{"result": 0, "reason": "no connection to compute server"}'
    camera = init_camera()
    camera.resolution =(160,160)
    camera.framerate_range =(10,10)
    cam_settings = CameraSettings(camera)
    mode = ''
    mode = request.args.get('mode', None)
    init_3d_camera(cam_settings)
    # start
    set_dias(False)
    set_flash(FLASH_LEVEL)
    warm_up()
    return Response(get_test_exposure_pictures(camera, mode=mode),mimetype='multipart/x-mixed-replace; boundary=frame')

@pic3d.route('/3dset')
def pic3dset():
    "send 3d set to compute - without display"
    send_start()
    camera = init_camera()
    camera.resolution =(160,160)
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
    fdlist = get_picture_infoset(camera)
    fdlist.append(['color.jpg', fd1])
    post_file_objects_bg("scan3d", fdlist, post_data={'pictureno': 1})
    camera.close()
    led_off()
    send_stop()
    return Response("Det gik fantastisk godt")
