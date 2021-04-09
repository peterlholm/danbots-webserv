#from time import sleep
#from io import BytesIO

from picamera import PiCamera

def init_camera():
    camera = PiCamera()
    #camera.framerate_range =(20,40)
    #camera.resolution =(150,150)
    return camera

def print_settings(camera):
    strg = "ExposureSpeed: {:5.3f} sec(max {:5.1f}  pic/sec)<br>".format(camera.exposure_speed/1000000, 1000000/camera.exposure_speed)
    strg += "FrameRate: " + str(camera.framerate) + "<br>"
    strg += "FrameRateRange: " + str(camera.framerate_range) + "<br>"
    strg += "PictureSize: " + str(camera.resolution) + "<br>"
    return strg

# class ScanCam:
#     """ Camera capture for danwand """
#     cam = None
#     #print ("initcam", cam)

#     def __init__(self):
#         self.cam = PiCamera()
#         self.cam.resolution =(150,150)

#     def warm_up(self, inittime = 1):
#         print("Starting camera")
#         sleep(inittime)

#     def capture(self, output, format='jpeg'):
#         #print(type(output))
#         if isinstance (output, BytesIO):
#             #print ("fd")
#             self.cam.capture(output, format=format, use_video_port=True)
#         else:
#             self.cam.capture(output)
#             return True
#         return output

#     def pcapture(self, output, format='jpeg'):
#         #print(type(output))
#         if isinstance (output, BytesIO):
#             #print ("fd")
#             self.cam.capture(output, format=format, use_video_port=False)
#         else:
#             self.cam.capture(output)
#             return True

#         return output

#     def exif(self):
#         print ("ExposureSpeed", self.cam.exposure_speed/1000000)
#         print ("FrameRate", self.cam.framerate)
#         print ("FrameRateRange", self.cam.framerate_range)

#     def close(self):
#         self.cam.close()
#         sleep(0.1)
#         self.cam = None
