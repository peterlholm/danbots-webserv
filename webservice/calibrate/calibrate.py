from io import BytesIO
import base64
from flask import Blueprint, render_template, request, Markup # Response, send_file,
from camera import init_camera, warm_up, get_exposure_info, get_white_balance


#from webservice import app

calibrate = Blueprint('calibrate', __name__, url_prefix='/calibrate')

def capture_picture(camera):
    fd1 = BytesIO()
    camera.capture(fd1, format='jpeg', use_video_port=False)
    fd1.seek(0)
    return fd1

class CameraSettings:   # pylint: disable=too-many-instance-attributes
    camera = None
    contrast = 0
    brightness = 50
    saturation = 0
    iso = None
    exposure_compensation = 0
    exposure_mode = 'auto'
    awb_mode = 'auto'
    sharpness = 0
    meter_mode = 'average'
    drc_strength = 'off'
    resolution = 'VGA'
    shutter_speed = 0

    def __init__(self, camera):
        self.camera = camera
        #self.reset()

    def set(self):
        self.camera.contrast = self.contrast
        self.camera.brightness = self.brightness
        self.camera.saturation = self.saturation
        if self.iso:
            self.camera.iso = self.iso
        self.camera.exposure_compensation = self.exposure_compensation
        self.camera.exposure_mode = self.exposure_mode
        self.camera.awb_mode = self.awb_mode
        self.camera.sharpness = self.sharpness
        self.camera.meter_mode = self.meter_mode
        self.camera.drc_strength = self.drc_strength
        self.camera.resolution = self.resolution
        self.camera.shutter_speed = self.shutter_speed

    def reset(self):
        self.camera.contrast = 0
        self.camera.brightness = 50
        self.camera.saturation = 0
        self.iso = None
        self.exposure_compensation = 0
        self.exposure_mode = 'auto'
        self.awb_mode = 'auto'
        self.sharpness = 0
        self.meter_mode = 'average'
        self.drc_strength = 'off'
        self.resolution = 'VGA'
        self.shutter_speed = 0

    def str(self):
        return "Contrast: {} Brigthness: {} Saturation: {} Iso: {}".format(self.camera.contrast, self.camera.brightness, self.camera.saturation,  self.camera.iso)

    def set_str(self):
        return "Contrast: {} Brigthness: {} Saturation: {}".format(self.contrast, self.brightness, self.saturation)

@calibrate.route('/test', methods=['GET', 'POST'])
def test():
    camera = init_camera()
    camera.resolution =(640,480)
    warm_up(camera)
    settings = CameraSettings(camera)
    if request.method == 'POST':
        settings.contrast = int(request.form['contrast'])
        settings.brightness = int(request.form['brightness'])
        settings.saturation = int(request.form['saturation'])
        settings.iso = int(request.form['iso'])
        settings.exposure_compensation = int(request.form['exposure_compensation'])
        settings.exposure_mode = request.form['exposure_mode']
        settings.awb_mode = request.form['awb_mode']
        settings.sharpness = int(request.form['sharpness'])
        settings.meter_mode = request.form['meter_mode']
        settings.drc_strength = request.form['drc_strength']
        settings.resolution = request.form['resolution']
        settings.shutter_speed = int(request.form['shutter_speed'])*1000

    fd = capture_picture(camera)
    exposure1 = Markup(get_exposure_info(camera) + "<br>" + get_white_balance(camera))
    img1 = base64.b64encode(fd.getvalue()).decode()
    settings.set()
    mysettings = "Camera: " + settings.str()
    warm_up(camera)
    fd2 = capture_picture(camera)
    exposure2 = Markup(get_exposure_info(camera)+ "<br>" + get_white_balance(camera) + "<br>" + mysettings)
    img2 = base64.b64encode(fd2.getvalue()).decode()
    camera.close()
    return render_template('calibrate.html', header="Calibrate", img1=img1, img2=img2, exposure1=exposure1,exposure2=exposure2)
