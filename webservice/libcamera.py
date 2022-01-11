import os
from io import BytesIO

FILENAME = '/tmp/test.jpg'
COMMAND='libcamera-still -o ' + FILENAME

def take_picture(options=None):
    cmd = COMMAND
    if options:
        cmd += ' ' + options
    os.system(cmd)
    f = open(FILENAME, "rb")
    return f
