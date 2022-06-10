""" send 2d scans to server """
from time import sleep
from datetime import datetime
from io import BytesIO
from flask import Blueprint, Response, request, render_template
from camera import init_camera, warm_up, get_exposure_info #get_picture_info,
from send_files import send_file_object #, send_api_request
from webservice_config import API_SERVER, COMPUTE_SERVER, CAPTURE_2D
from hw.led_control import set_flash
from send2server import send_api_request, post_single_file
from pic_param import get_set_led

# python: disable=unresolved-import,import-error

FLASH_LEVEL = float(CAPTURE_2D['flash'])                # light level for flash
CAPTURE_DELAY = float(CAPTURE_2D['capture_delay'])      # delay to setle light meter
NUMBER_PICTURES = int(CAPTURE_2D['number_pictures'])
PICTURE_INTERVAL = float(CAPTURE_2D['picture_interval']) # delay between pictures
#EXPOSURE_COMPENSATION = int(CAPTURE_3D['exposure_compensation'])
#JPEG_QUALITY = 85

_DEBUG = True

def send_picture(fd1, picture_no):
    filename = "picture"+str(picture_no)+'.jpg'
    send_file_object(fd1, filename, data={'cmd':'picture','folder': 'save2d', 'pictureinfo': picture_no}, url = API_SERVER + 'savefile')

def capture_picture(camera):
    fd1 = BytesIO()
    camera.capture(fd1, format='jpeg', use_video_port=False)
    fd1.seek(0)
    return fd1

def get_pictures(camera, cmd=""):
    "take pictures and send cam and pictures to server"
    number_pictures = NUMBER_PICTURES
    fd1 = BytesIO()
    i=1
    pic_no = 1
    #sleep(CAPTURE_DELAY)
    start = datetime.now()
    if PICTURE_INTERVAL==0:
        pic_modolu=1
    else:
        pic_modolu = int(PICTURE_INTERVAL*10)
    if _DEBUG:
        print("pic modolu", pic_modolu)
    try:
        while True:
            camera.capture(fd1, format='jpeg', use_video_port=True)
            fd1.truncate()
            fd1.seek(0)
            pic = fd1.read()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + pic + b'\r\n')
            fd1.seek(0)
            if i % pic_modolu == 0:
                #send_api_request_bg('save2d', url=COMPUTE_SERVER)
                params = {'pictureno': pic_no, 'cmd': cmd}
                post_single_file("save2d", fd1, post_data=params)
                #send_picture(fd1, pic_no)
                fd1.seek(0)
                pic_no = pic_no+1
            i=i+1
            if pic_no>number_pictures:
                break
            sleep(0)
    finally:
        stop = datetime.now()
        print(f"Vi lukker og slukker {i/((stop-start).total_seconds()):2.1f} Billeder/sek")
        print(get_exposure_info(camera))
        camera.close()
        set_flash(False)
        send_api_request('stop2d', url=COMPUTE_SERVER)

pic2d = Blueprint('2d', __name__, url_prefix='/2d')

@pic2d.route('/2d')
def cam():
    "show cam and send pictures"
    set_flash(FLASH_LEVEL)
    send_api_request("start2d?cmd=2d", url=COMPUTE_SERVER)
    camera = init_camera()
    camera.resolution =(640,480)
    #camera.framerate_range =(10,25)
    size = request.args.get('size', None)
    if size:
        camera.resolution =(int(size),int(size))
    get_set_led(request)
    warm_up()
    cmd = request.args.get('cmd', "")
    return Response(get_pictures(camera, cmd=cmd),mimetype='multipart/x-mixed-replace; boundary=frame')

@pic2d.route('/p_2d')
def p_cam():
    return render_template('p2page.html', header="2D Cam", src="/2d/2d")

@pic2d.route('/picture')
def picture():
    # send one picture to API server
    camera = init_camera()
    camera.resolution =(640,480)
    #camera.framerate_range =(10,25)
    size = request.args.get('size', None)
    if size:
        camera.resolution =(int(size),int(size))
    warm_up()
    fd = capture_picture(camera)
    expinfo=get_exposure_info(camera)
    camera.close()
    res=send_file_object(fd, "2d.jpg", data={'folder': "testfolder", 'exposure': expinfo})
    print(res)
    return Response(res)
