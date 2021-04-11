from sys import platform
from time import sleep
from datetime import datetime
from fractions import Fraction
from io import BytesIO
from flask import Blueprint, send_file, Response, request

from camera import init_camera, warm_up, get_camera_settings

# python: disable=unresolved-import,import-error
# from mpeg import scan_cont_pictures

# if platform == "linux":
#     from picamera import PiCamera   # pylint: disable=import-error
# else:
#     import pygame
#     import pygame.camera # pylint: disable=wrong-import-position
#     #from pygame.locals import *

# def init_camera():
#     if platform=="linux":
#         camera = PiCamera()
#         camera.framerate_range =(10,10)
#         # camera.resolution =(1280,720)
#         #camera.resolution =(2592,1944)
#         #camera.resolution =(640,480)
#         camera.resolution =(150,150)

#         return camera
#     else:
#         pygame.camera.init()
#         mycam = pygame.camera.Camera(0,(640,480))
#         mycam.start()
#         return mycam

# def warm_up():
#     sleep(1)


# def get_camera_settings(camera):
#     strg = "ExposureSpeed: {:5.3f} sec(max {:5.1f}  pic/sec)\r\n".format(camera.exposure_speed/1000000, 1000000/camera.exposure_speed)
#     strg += "Mode: " + str(camera.sensor_mode) + " ISO: " + str(camera.iso) + "\r\n"
#     strg += "Gain: analog " + str(camera.analog_gain) + " digital " + str(camera.digital_gain) + "\r\n"
#     strg += "Brightness {:5.3f} Contrast {:5.3f}\r\n".format(camera.brightness,camera.contrast)
#     strg += "Denoise {:5.3f} Sharpness {:5.3f}\r\n".format(camera.image_denoise, camera.sharpness)
#     strg += "FrameRate: " + str(camera.framerate) + "\r\n"
#     strg += "FrameRateRange: " + str(camera.framerate_range) + "\r\n"
#     strg += "PictureSize: " + str(camera.resolution) + "\r\n"
#     return strg

# def print_settings(camera):
#     strg = "ExposureSpeed: {:5.3f} sec(max {:5.1f}  pic/sec)<br>".format(camera.exposure_speed/1000000, 1000000/camera.exposure_speed)
#     strg += "FrameRate: " + str(camera.framerate) + "<br>"
#     strg += "FrameRateRange: " + str(camera.framerate_range) + "<br>"
#     strg += "PictureSize: " + str(camera.resolution) + "<br>"
#     return strg

def get_picture(camera):
    if platform == "linux":
        fd1 = BytesIO()
        camera.capture(fd1, format='jpeg')
        fd1.truncate()
        fd1.seek(0)
        print(get_camera_settings(camera))

        camera.close()
        return fd1
    else:
        fd1 = BytesIO()
        img = camera.get_image()
        pygame.image.save_extended(img, "testpic.jpg")
        camera.stop()
        with open("testpic.jpg" , 'rb') as filehandle:
            fd1 = BytesIO(filehandle.read())
        return fd1

def scan_cont_pictures(camera):
    j = 1
    stream = BytesIO()
    start = datetime.now()
    try:
        for i in camera.capture_continuous(stream, format='jpeg', use_video_port=True): # pylint: disable=unused-variable
            j = j+1
            stream.truncate()
            stream.seek(0)
            picture = stream.read()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + picture + b'\r\n')
            stream.seek(0)
    finally:
        stop = datetime.now()
        print("Vi lukker og slukker {:2.1f} billeder/sek".format(j/((stop-start).total_seconds())))
        print(get_camera_settings(camera))
        camera.close()
    return stream

pic = Blueprint('pic', __name__, url_prefix='/pic')
@pic.route('/picture')
def u_picture():
    camera = init_camera()
    warm_up(camera)
    print(get_camera_settings(camera))
    return send_file(get_picture(camera), mimetype='image/jpeg' )

@pic.route('/cam')
def cam():
    camera = init_camera()
    warm_up(camera)
    print(get_camera_settings(camera))
    size = request.args.get('size', None)
    if size:
        camera.resolution =(int(size),int(size))
    fr = request.args.get('maxframerate', None)
    if fr:
        camera.framerate_range.high = Fraction(1, int(fr))

    #warm_up()
    return Response(scan_cont_pictures(camera),mimetype='multipart/x-mixed-replace; boundary=frame')
