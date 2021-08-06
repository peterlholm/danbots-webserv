#import os
from flask import Flask, render_template #, request, session, redirect
from version import VERSION, INSTALLED
from picture import pic
from pic_2d import pic2d
from pic_3d import pic3d
from calibrate.calibrate import calibrate

print("Loading Webservice " + VERSION + " installed: " + INSTALLED)
app = Flask(__name__)
app.debug = True
app.register_blueprint(pic)
app.register_blueprint(pic2d)
app.register_blueprint(pic3d)
app.register_blueprint(calibrate)
app.secret_key = b'_5#y2xyzQ8z\n\xec]/'

@app.route('/')
def home1():
    return render_template('index.html')

@app.route('/version')
def version():
    return "Webservice " + VERSION + " installed: " + INSTALLED


if __name__ == '__main__':
    print("script server running version "+ VERSION + " installed: " + INSTALLED)
    #app = Flask(__name__)
    app.debug = True
    app.env='development'
    app.run(host='0.0.0.0', port=8080)
