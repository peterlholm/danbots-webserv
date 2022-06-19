"""
Return pictures and MPEG images
"""
from datetime import datetime
import pprint
#from fractions import Fraction
from io import BytesIO
from flask import Blueprint, send_file, Response, request, render_template
from camera import init_camera, warm_up,  get_picture_info, get_exposure_info, myzoom #get_camera_settings,
from hw.led_control import set_dias, set_flash

_DEBUG = True

def get_set_led():
    dias = float(request.args.get('dias',0))
    set_dias(dias)
    flash = float(request.args.get('flash',0))
    set_flash(flash)
    return "dias="+str(dias) +"&flash="+str(flash)

def led_off():
    set_flash(0)
    set_dias(0)

def get_picture(camera, format='jpeg', quality=None): # pylint: disable=redefined-builtin
    fd1 = BytesIO()
    camera.capture(fd1, format=format, quality=quality)
    fd1.truncate()
    fd1.seek(0)
    camera.close()
    led_off()
    return fd1

def scan_cont_pictures(camera, quality=None):
    if quality is None:
        quality=85
    j = 1
    stream = BytesIO()
    start = datetime.now()
    try:
        for i in camera.capture_continuous(stream, format='jpeg', quality=quality, use_video_port=True): # pylint: disable=unused-variable
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
    #?quality=85&dias=0&type=jpeg/png
    camera = init_camera()
    camera.resolution =(2592,1944)
    pic_format='jpeg'
    pic_mime='image/jpeg'
    img_type = request.args.get('type', None)
    if img_type=='png':
        pic_format='png'
        pic_mime='image/png'
    pic_quality = 85
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
    if _DEBUG:
        print(get_exposure_info(camera))
    return send_file(get_picture(camera, format=pic_format, quality=pic_quality), mimetype=pic_mime)

@pic.route('/p_picture')
def p_picture():
    arg = "?" + get_set_led()
    camera = init_camera()
    warm_up()
    exposure = get_exposure_info(camera)
    camera.close()
    return render_template('picture.html', name="", exposure=exposure, arg=arg)

@pic.route('/p_cam')
def p_cam():
    arg=get_set_led()
    return render_template('cam.html', name="", arg=arg)

@pic.route('/cam')
def cam():
    get_set_led()
    camera = init_camera()
    warm_up()
    if _DEBUG:
        print(get_exposure_info(camera))
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
    return Response(scan_cont_pictures(camera, quality=quality),mimetype='multipart/x-mixed-replace; boundary=frame')

@pic.route('/info')
def info():
    camera = init_camera()
    get_set_led()
    warm_up()
    camera_info = get_picture_info(camera)
    #pprint.pprint(camera_info)
    camera.close()
    led_off()
    return Response(pprint.pformat(camera_info).replace('\n', '<br />')+'<br><a href="/">Back</a>')



@pic.route('/still')
def still():
    #?quality=85&dias=0&type=jpeg/png
    camera = init_camera()
    camera.resolution =(2592,1944)
    pic_format='jpeg'
    pic_mime='image/jpeg'
    img_type = request.args.get('type', None)
    if img_type=='png':
        pic_format='png'
        pic_mime='image/png'
    pic_quality = 85
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

    if _DEBUG:
        print(get_exposure_info(camera))

    fd1 = BytesIO()
    camera.capture(fd1, format='jpeg', quality=quality)
    fd1.truncate()
    fd1.seek(0)
    camera.close()
    led_off()


    camera_info = get_picture_info(camera)
    print (camera_info)

    return send_file(fd1, attachment_filename='python.jpg')
    #return send_file(get_picture(camera, format=pic_format, quality=pic_quality), mimetype=pic_mime)
