from io import BytesIO

def get_picture(camera):
    fd1 = BytesIO()
    camera.pcapture(fd1)
    fd1.truncate()
    fd1.seek(0)
    camera.close()
    return fd1
