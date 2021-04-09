from time import sleep
from datetime import datetime
from io import BytesIO
from flask import Flask, Response, send_file
from .camera import init_camera, print_settings #ScanCam,
from .bench.capture import scan_cont_mem_set
from .picture.capture import get_picture
from .mpeg.capture import mpeg_pictures,scan_cont_pictures
from .send_info import  SendMemFiles_BG # SendMemFiles,

def warm_up():
    sleep(1)

def send_picture(fd1, i):
    SendMemFiles_BG(fd1, "picture"+str(i), params={'cmd':'picture','pictureinfo': "nr"}, info="djdjdjdj" )

def get_pictures(camera):
    fd1 = BytesIO()
    i=1
    pic_no = 1
    start = datetime.now()
    try:
        while True:
            camera.capture(fd1)
            fd1.truncate()
            fd1.seek(0)
            pic = fd1.read()
            #print("sender billede")
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + pic + b'\r\n')
            fd1.seek(0)
            if i % 30 == 0:
                send_picture(fd1, pic)
                fd1.seek(0)
                pic_no = pic_no+1
            i=i+1
            sleep(0)
    finally:
        stop = datetime.now()
        print("Vi lukker og slukker {:2.1f} Billeder/sek".format(i/((stop-start).total_seconds())))
        camera.close()


app = Flask(__name__)

print ("--- Server Ready ---")

@app.route('/')
def umpeg_pictures():
    camera = init_camera()
    camera.warm_up()
    return Response(get_pictures(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/cam')
def cam():
    camera = init_camera()
    warm_up()
    #print("start", datetime.datetime.now())
    return Response(mpeg_pictures(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camm')
def ucamm():
    camera = init_camera()
    warm_up()
    print("start", datetime.now())
    return Response(scan_cont_pictures(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/picture')
def u_picture():
    camera = init_camera()
    warm_up()
    return send_file(get_picture(camera), mimetype='image/jpeg' )

# bench marks

@app.route('/bench/cam')
def u_bench_cam():
    camera = init_camera()
    warm_up()
    antal = 100
    start = datetime.now()
    scan_cont_mem_set(camera, antal)
    strg = print_settings(camera)
    end = datetime.datetime.now()
    dif = end - start
    camera.close()
    return "<h1>Testresults</h1>Billeder pr sek: {:5.1f}<br>".format(antal/dif.total_seconds()) + strg

if __name__ == '__main__':
    #app = Flask(__name__)
    app.debug = False
    app.run(host='0.0.0.0', port=8080)
