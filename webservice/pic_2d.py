from time import sleep
from datetime import datetime
from io import BytesIO
from flask import Blueprint, Response, request, render_template
from camera import init_camera, warm_up, get_exposure_info #get_picture_info,
from send_files import send_file_object, send_api_request
from webservice_config import  API_SERVER

# python: disable=unresolved-import,import-error

def send_picture(fd1, picture_no):
    filename = "picture"+str(picture_no)+'.jpg'
    send_file_object(fd1, filename, data={'cmd':'picture','folder': 'save2d', 'pictureinfo': picture_no}, url = API_SERVER + 'savefile')
    #send_mem_files_bg(fd1, "picture"+str(i), params={'cmd':'picture','pictureinfo': "nr"}, info="djdjdjdj" )

def capture_picture(camera):
    fd1 = BytesIO()
    camera.capture(fd1, format='jpeg', use_video_port=False)
    fd1.seek(0)
    return fd1

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
        print(get_exposure_info(camera))
        camera.close()

pic2d = Blueprint('2d', __name__, url_prefix='/2d')

@pic2d.route('/2d')
def cam():
    send_api_request("2d/start")
    camera = init_camera()
    camera.resolution =(640,480)
    #camera.framerate_range =(10,25)
    size = request.args.get('size', None)
    if size:
        camera.resolution =(int(size),int(size))
    warm_up(camera)
    return Response(get_pictures(camera),mimetype='multipart/x-mixed-replace; boundary=frame')

@pic2d.route('/p_2d')
def p_cam():
    return render_template('ppage.html', header="2D Cam", src="/2d/2d")

@pic2d.route('/picture')
def picture():
    # send one picture to API server
    camera = init_camera()
    camera.resolution =(640,480)
    #camera.framerate_range =(10,25)
    size = request.args.get('size', None)
    if size:
        camera.resolution =(int(size),int(size))
    warm_up(camera)
    fd = capture_picture(camera)
    expinfo=get_exposure_info(camera)
    camera.close()
    res=send_file_object(fd, "2d.jpg", data={'folder': "testfolder", 'exposure': expinfo})
    print(res)
    return Response(res)
