from sys import platform
from time import sleep
from io import BytesIO
from flask import Blueprint, send_file

# python: disable=unresolved-import

if platform == "linux":
    from picamera import PiCamera   # pylint: disable=import-error
else:
    import pygame
    import pygame.camera # pylint: disable=wrong-import-position
    from pygame.locals import *

def get_picture(camera):
    if platform == "linux":
        fd1 = BytesIO()
        camera.capture(fd1, format='jpeg')
        fd1.truncate()
        fd1.seek(0)
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

def init_camera():
    if platform=="linux":
        camera = PiCamera()
        #camera.framerate_range =(20,40)
        #camera.resolution =(150,150)
        return camera
    else:
        pygame.camera.init()
        cam = pygame.camera.Camera(0,(640,480))
        cam.start()
        return cam

def warm_up():
    sleep(1)


pic = Blueprint('picture', __name__, url_prefix='/picture')
@pic.route('/picture')
def u_picture():
    camera = init_camera()
    warm_up()
    return send_file(get_picture(camera), mimetype='image/jpeg' )
