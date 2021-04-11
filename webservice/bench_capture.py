from time import sleep
from datetime import datetime
from io import BytesIO
from picamera import PiCamera
#from shutil import copyfileobj

def scan_cont_mem_set(camera, antal=100, format='jpeg'): # pylint: disable=redefined-builtin
    j = 1
    #filelist = []
    stream = BytesIO()
    for i in camera.capture_continuous(stream, format=format, use_video_port=True): # pylint: disable=unused-variable
        j = j+1
        stream.seek(0)
        if j>=antal:
            break
    stream.truncate()
    stream.seek(0)
    return stream

def print_settings(camera):
    strg = "ExposureSpeed: {:5.3f} sec(max {:5.1f}  pic/sec)<br>".format(camera.exposure_speed/1000000, 1000000/camera.exposure_speed)
    strg += "FrameRate: " + str(camera.framerate) + "<br>"
    strg += "FrameRateRange: " + str(camera.framerate_range) + "<br>"
    strg += "PictureSize: " + str(camera.resolution) + "<br>"
    return strg

camera = PiCamera()
sleep(5)
antal=100
start =datetime.now()
scan_cont_mem_set(camera, antal=antal)
slut = datetime.now()

print ("Billeder pr sek", antal/(slut-start).total_seconds())
strg = "ExposureSpeed: {:5.3f} sec(max {:5.1f}  pic/sec)\r\n".format(camera.exposure_speed/1000000, 1000000/camera.exposure_speed)
strg += "FrameRate: " + str(camera.framerate) + "\r\n"
strg += "FrameRateRange: " + str(camera.framerate_range) + "\r\n"
strg += "PictureSize: " + str(camera.resolution) + "\r\n"
print(strg)

camera.close()
