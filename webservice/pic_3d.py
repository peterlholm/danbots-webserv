from time import sleep
from datetime import datetime
from io import BytesIO
from flask import Blueprint, Response, request
from camera import init_camera, warm_up, get_camera_settings
from send_files import send_mem_files_bg
from gpiozero import LED

LED_dias = LED(12)
LED_flash = LED(13)

def set_flash(on_off):
    if on_off:
        LED_flash.on()
    else:
        LED_flash.off()

def set_dias(on_off):
    if on_off:
        LED_dias.on()
    else:
        LED_dias.off()

# python: disable=unresolved-import,import-error

def send_picture(fd1, i):
    send_mem_files_bg(fd1, "picture"+str(i), params={'cmd':'picture','pictureno': str(i)}, info="djdjdjdj" )

def get_picture_set(camera):
    #print("Lysbilled on")
    set_flash(False)
    set_dias(True)
    fd2 = BytesIO()
    #sleep(1)
    camera.capture(fd2, format='jpeg', use_video_port=True)
    fd2.truncate()
    fd2.seek(0)
    set_dias(False)
    #print("led off")
    #sleep(1)
    fd3 = BytesIO()
    camera.capture(fd3, format='jpeg', use_video_port=True)
    fd3.truncate()
    fd3.seek(0)
    #print ("Normal light")
    set_flash(True)
    return (fd2, fd3)

def get_pictures(camera):
    fd1 = BytesIO()
    i=1
    pic_no = 1
    start = datetime.now()
    try:
        while True:
            camera.capture(fd1, format='jpeg', use_video_port=True)
            fd1.truncate()
            fd1.seek(0)
            pic = fd1.read()
            #print("sender billede")
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + pic + b'\r\n')
            fd1.seek(0)
            if i % 60 == 0:
                (fd2, fd3) = get_picture_set(camera)
                send_picture([fd1,fd2,fd3], pic_no)
                fd1.seek(0)
                pic_no = pic_no+1
                #break
            i=i+1
            sleep(0)

    finally:
        stop = datetime.now()
        print("Vi lukker og slukker {:2.1f} Billeder/sek".format(i/((stop-start).total_seconds())))
        print(get_camera_settings(camera))
        camera.close()

pic3d = Blueprint('3d', __name__, url_prefix='/3d')

@pic3d.route('/3d')
def cam():
    camera = init_camera()
    #camera.resolution =(640,480)
    camera.resolution =(150,150)
    camera.framerate_range =(10,10)

    size = request.args.get('size', None)
    if size:
        camera.resolution =(int(size),int(size))
    set_dias(False)
    set_flash(True)
    warm_up(camera)
    return Response(get_pictures(camera),mimetype='multipart/x-mixed-replace; boundary=frame')