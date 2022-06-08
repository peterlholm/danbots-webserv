"""
Return pictures and MPEG images with led control from URL
"""
from datetime import datetime
#from time import perf_counter
import pprint
#from fractions import Fraction
from io import BytesIO
from flask import Blueprint, send_file, Response, request, render_template
from camera import init_camera, warm_up,  get_picture_info, get_exposure_info, myzoom # pylint: disable=line-too-long
from hw.led_control import set_dias, set_flash
from pic_param import get_fix_param

DEFAULT_JPG_QUALITY = 85

_DEBUG = True

def get_set_led():
    "Decode led information from url"
    # 1.003 sec on slow connections
    #start  = perf_counter()
    dias = float(request.args.get('dias',0))
    set_dias(dias)
    flash = float(request.args.get('flash',0))
    set_flash(flash)
    #stop = perf_counter()
    #print (f"GetSetLed {stop - start:.3f} seconds")
    return "dias="+str(dias) +"&flash="+str(flash)

# def get_fix_param(camera):
#     "decode and set camera param from parameters"
#     exp = float(request.args.get('exp',0))
#     iso = float(request.args.get('iso',0))
#     if exp != 0:
#         camera.shutter_speed = int (exp*1000000)
#     if iso != 0:
#         camera.iso = int(iso)

def led_off():
    "Turn both leds off"
    set_flash(0)
    set_dias(0)

def get_picture(camera, format='jpeg', quality=DEFAULT_JPG_QUALITY): # pylint: disable=redefined-builtin
    "Take picture and put in ByteIO stream"
    fd1 = BytesIO()
    camera.capture(fd1, format=format, quality=quality)
    if _DEBUG:
        print(get_exposure_info(camera))
    fd1.truncate()
    fd1.seek(0)
    camera.close()
    led_off()
    return fd1

def scan_cont_pictures(camera, quality=DEFAULT_JPG_QUALITY):
    "Take continues pictures and return in yield"
    j = 1
    stream = BytesIO()
    start = datetime.now()
    try:
        for i in camera.capture_continuous(stream, format='jpeg', quality=quality, use_video_port=True): # pylint: disable=unused-variable,line-too-long
            j = j+1
            stream.truncate()
            stream.seek(0)
            picture = stream.read()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + picture + b'\r\n')
            stream.seek(0)
    finally:
        stop = datetime.now()
        if _DEBUG:
            print(f"Vi lukker og slukker {j/((stop-start).total_seconds()):.2f} billeder/sek")
            print(get_exposure_info(camera))
        camera.close()
        led_off()
    return stream

pic = Blueprint('pic', __name__, url_prefix='/pic')

@pic.route('/picture')
def u_picture():
    "Take picture and return as jpeg image"
    #?quality=85&dias=0&type=jpeg/png
    camera = init_camera()
    camera.resolution =(2592,1944)
    pic_format='jpeg'
    pic_mime='image/jpeg'
    img_type = request.args.get('type', None)
    if img_type=='png':
        pic_format='png'
        pic_mime='image/png'
    pic_quality = DEFAULT_JPG_QUALITY
    quality = request.args.get('quality', None)
    if quality:
        pic_quality=int(quality)
    size = request.args.get('size', None)
    if size:
        camera.resolution = (int(size),int(size))
    compensation = request.args.get('compensation', None)
    if compensation:
        camera.exposure_compensation = int(compensation)
    zoom = request.args.get('zoom', None)
    if zoom:
        res = myzoom(float(zoom))
        print ("zoom", zoom, res)
        camera.zoom = res
    get_set_led()
    warm_up()
    return send_file(get_picture(camera, format=pic_format, quality=pic_quality), mimetype=pic_mime)

@pic.route('/p_picture')
def p_picture():
    "Take picture and return html page with picture and information"
    arg = "?" + get_set_led()
    camera = init_camera()
    warm_up()
    #exposure = get_exposure_info(camera)
    exposure = ""
    camera.close()
    return render_template('picture.html', name="", exposure=exposure, arg=arg)

@pic.route('/p_cam')
def p_cam():
    "Start cam and return html page with mpeg stream and information"
    arg=get_set_led()
    return render_template('cam.html', name="", arg=arg)

@pic.route('/cam')
def cam():
    "Start Cam and return mpeg stream"
    get_set_led()
    camera = init_camera()
    size = request.args.get('size', None)
    if size:
        camera.resolution = (int(size),int(size))
    max_frame = request.args.get('maxframerate', None)
    if max_frame:
        myrange = camera.framerate_range
        camera.framerate_range = (myrange.low, int(max_frame))
    quality = request.args.get('quality', None)
    if quality:
        quality=int(quality)
    else:
        quality = DEFAULT_JPG_QUALITY
    get_fix_param(request, camera)
    #camera.iso = 100

    return Response(scan_cont_pictures(camera, quality=quality),mimetype='multipart/x-mixed-replace; boundary=frame') # pylint: disable=line-too-long

@pic.route('/info')
def info():
    "get picture info without taking picture"
    camera = init_camera()
    get_set_led()
    warm_up()
    camera_info = get_picture_info(camera)
    #pprint.pprint(camera_info)
    camera.close()
    led_off()
    return Response(pprint.pformat(camera_info).replace('\n', '<br />')+'<br><a href="/">Back</a>')
