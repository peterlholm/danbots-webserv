from sys import platform
from datetime import datetime
from fractions import Fraction
from io import BytesIO
from flask import Blueprint, send_file, Response, request
from camera import init_camera, warm_up, get_camera_settings
if platform == "nt":
    from pygame.image import save_extended

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
        save_extended(img, "testpic.jpg")
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
    camera.resolution =(2592,1944)
    warm_up(camera)
    return send_file(get_picture(camera), mimetype='image/jpeg' )

@pic.route('/cam')
def cam():
    camera = init_camera()
    #camera.resolution =(640,480)
    camera.resolution =(150,150)
    camera.framerate_range =(10,25)
    warm_up(camera)
    print(get_camera_settings(camera))
    size = request.args.get('size', None)
    if size:
        camera.resolution =(int(size),int(size))
    max_frame = request.args.get('maxframerate', None)
    if max_frame:
        camera.framerate_range.high = Fraction(1, int(max_frame))
    return Response(scan_cont_pictures(camera),mimetype='multipart/x-mixed-replace; boundary=frame')
