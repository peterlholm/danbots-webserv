import os
from flask import Flask, request, Response, session, send_file, redirect

#from test.test import *

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        HOST="0.0.0.0",
        PORT="4444"
    )

    if test_config is None:
        print("no testconfig")
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=False)
    else:
        print("loading testconfig")
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    import picture
    #print ("__init__")
    app.register_blueprint(picture.pic)

    @app.route('/')
    def home():            # pylint: disable=unused-variable
        return 'Hello, Home'

    # a simple page that says hello
    @app.route('/hello')
    def hello():            # pylint: disable=unused-variable
        return 'Hello, World!'

    return app
