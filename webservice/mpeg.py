import datetime
from io import BytesIO

def print_settings(camera):
    strg = "ExposureSpeed: {:5.3f} sec(max {:5.1f}  pic/sec)<br>".format(camera.exposure_speed/1000000, 1000000/camera.exposure_speed)
    strg += "FrameRate: " + str(camera.framerate) + "<br>"
    strg += "FrameRateRange: " + str(camera.framerate_range) + "<br>"
    strg += "PictureSize: " + str(camera.resolution) + "<br>"
    return strg

def mpeg_pictures(camera):
    fd1 = BytesIO()
    i=1
    start = datetime.datetime.now()
    try:
        while True:
            camera.capture(fd1)
            fd1.truncate()
            fd1.seek(0)
            pic = fd1.read()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + pic + b'\r\n')
            fd1.seek(0)
            i = i + 1
    finally:
        stop = datetime.datetime.now()
        print("Vi lukker og slukker {:2.1f} billeder/sek".format(i/((stop-start).total_seconds())))
        camera.close()

def scan_cont_pictures(camera):
    j = 1
    stream = BytesIO()
    start = datetime.datetime.now()
    try:
        for i in camera.capture_continuous(stream, format='jpeg', use_video_port=True): # pylint: disable=unused-variable
            j = j+1
            stream.truncate()
            stream.seek(0)
            pic = stream.read()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + pic + b'\r\n')
            stream.seek(0)
    finally:
        stop = datetime.datetime.now()
        print("Vi lukker og slukker {:2.1f} billeder/sek".format(j/((stop-start).total_seconds())))
        strg = "ExposureSpeed: {:5.3f} sec(max {:5.1f}  pic/sec)\r\n".format(camera.exposure_speed/1000000, 1000000/camera.exposure_speed)
        strg += "FrameRate: " + str(camera.framerate) + "\r\n"
        strg += "FrameRateRange: " + str(camera.framerate_range) + "\r\n"
        strg += "PictureSize: " + str(camera.resolution) + "\r\n"
        print(strg)
        camera.close()
    return stream
