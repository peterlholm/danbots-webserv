from sys import platform
from time import sleep
from datetime import datetime
from io import BytesIO
from flask import Blueprint, send_file, Response, request

from send_files import send_mem_files_bg

# python: disable=unresolved-import,import-error

#from mpeg import scan_cont_pictures

if platform == "linux":
    from picamera import PiCamera   # pylint: disable=import-error
else:
    import pygame
    import pygame.camera # pylint: disable=wrong-import-position
    #from pygame.locals import *

def init_camera():
    if platform=="linux":
        camera = PiCamera()
        #camera.framerate_range =(20,40)
        #camera.resolution =(150,150)
        return camera
    else:
        pygame.camera.init()
        mycam = pygame.camera.Camera(0,(640,480))
        mycam.start()
        return mycam

def warm_up():
    sleep(1)


def send_picture(fd1, i):
    send_mem_files_bg(fd1, "picture"+str(i), params={'cmd':'picture','pictureinfo': "nr"}, info="djdjdjdj" )

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
            if i % 30 == 0:
                send_picture(fd1, pic_no)
                fd1.seek(0)
                pic_no = pic_no+1
            i=i+1
            sleep(0)
    finally:
        stop = datetime.now()
        print("Vi lukker og slukker {:2.1f} Billeder/sek".format(i/((stop-start).total_seconds())))
        camera.close()


# app = Flask(__name__)

# print ("--- Server Ready ---")

pic3d = Blueprint('3d', __name__, url_prefix='/3d')


# def cam():
#     camera = init_camera()
#     camera.warm_up()
#     return Response(get_pictures(camera),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')
@pic3d.route('/3d')
def cam():
    camera = init_camera()
    size = request.args.get('size', None)
    if size:
        camera.resolution =(int(size),int(size))
    warm_up()
    return Response(get_pictures(camera),mimetype='multipart/x-mixed-replace; boundary=frame')
