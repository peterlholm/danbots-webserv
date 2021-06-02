from io import BytesIO
import base64
from flask import Blueprint, render_template, request, Markup # Response, send_file,
from camera import init_camera, warm_up, CameraSettings, get_exposure_info, get_white_balance
from hw.led_control import set_dias, set_flash, get_dias, get_flash
calibrate = Blueprint('calibrate', __name__, url_prefix='/calibrate')

def capture_picture(camera):
    fd1 = BytesIO()
    camera.capture(fd1, format='jpeg', use_video_port=False)
    fd1.seek(0)
    return fd1

@calibrate.route('/test', methods=['GET', 'POST'])
def test():
    camera = init_camera()
    camera.resolution =(640,480)
    warm_up(camera)
    settings = CameraSettings(camera)
    dias = None
    flash = None
    if request.method == 'POST':
        print(request.form)
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
        dias = request.form.get('dias')
        flash = request.form.get('flash')
    print ("Flash", flash)
    print ("Dias", dias)
    fd = capture_picture(camera)
    exposure1 = Markup(get_exposure_info(camera) + "<br>" + get_white_balance(camera))
    img1 = base64.b64encode(fd.getvalue()).decode()
    settings.set()
    mysettings = "Camera: " + settings.str()
    if flash:
        set_flash(True)
    if dias:
        set_dias(True)
    warm_up(camera)
    fd2 = capture_picture(camera)
    exposure2 = Markup(get_exposure_info(camera)+ "<br>" + get_white_balance(camera) + " " + mysettings)
    img2 = base64.b64encode(fd2.getvalue()).decode()
    camera.close()
    set_flash(False)
    set_dias(False)
    return render_template('calibrate.html', header="Calibrate", img1=img1, img2=img2, exposure1=exposure1,exposure2=exposure2)

@calibrate.route('/light', methods=['GET', 'POST'])
def light():
    dias = get_dias()
    flash = get_flash()
    if request.method == 'POST':
        print(request.form)
        dias = float(request.form['dias'])
        flash = float(request.form['flash'])
        set_dias(dias)
        set_flash(flash)
    return render_template('light.html', header="Light", dias=dias, flash=flash)
