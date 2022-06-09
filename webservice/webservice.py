"scanner webservice"
import sys
import signal
import time
from flask import Flask, render_template #, request, session, redirect
from version import VERSION
from picture import pic
from pic_2d import pic2d
from pic_3d import pic3d
#from calibrate.calibrate import calibrate
#from calibrate.camera_test import test
from hw.led_control import set_dias, set_flash

def receive_signal(signal_number, frame):
    "signal handling"
    if signal_number ==signal.SIGINT:
        print("Received SIGINT - terminating")
        sys.exit(0)
    elif signal_number==signal.SIGTERM:
        print("Receiving signal", signal.SIGTERM, " - Terminating")
        sys.exit(0)
    else:
        print(f'Received Signal: {signal_number} {frame}')
        sys.exit(signal_number)

print("Loading Webservice " + VERSION)
app = Flask(__name__)
app.debug = True
app.register_blueprint(pic)
app.register_blueprint(pic2d)
app.register_blueprint(pic3d)
#app.register_blueprint(calibrate)
#app.register_blueprint(calibrate_flash)

app.secret_key = b'_5#y2xyzQ8z\n\xec]/'

# initialization
print ("Starting Webservice")
signal.signal(signal.SIGTERM, receive_signal)
signal.signal(signal.SIGINT, receive_signal)

#print("Test LED")
set_flash(1)
set_dias(1)
time.sleep(0.1)
set_dias(0)
set_flash(0)

@app.route('/')
def home1():
    "testing can be deleted"
    return render_template('index.html')

@app.route('/version')
def version():
    "version"
    return "Webservice " + VERSION

if __name__ == '__main__':
    print("Script server running version "+ VERSION)
    #app = Flask(__name__)
    app.debug = True
    app.env='development'
    app.run(host='0.0.0.0', port=8080)
