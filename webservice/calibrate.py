from io import BytesIO
from pprint import pprint
from camera import init_camera, warm_up,  get_picture_info, get_exposure_info, fix_exposure, auto_exposure, calibrate_picture #get_camera_settings,
from send_files import send_file_objects

ANTAL = 6


camera = init_camera()
#camera.shutter_speed = 500000
camera.iso  = 1200
warm_up(camera)
#pprint(get_picture_info(camera))
#print(get_exposure_info(camera))
#fix_exposure(camera)
fdlist = []
for i in range(ANTAL):
    filename = "billed_"+str(i)+'.jpg'
    fd = BytesIO()
    camera.capture(fd, format='jpeg', use_video_port=False)
    fd.seek(0)
    fdlist.append((filename, fd))
    print(i, get_exposure_info(camera))
    # if i == 14:
    #     auto_exposure(camera)

cal = calibrate_picture(camera)

send_file_objects(fdlist)
print(cal)

info = get_picture_info(camera)
pprint(info)
print(get_exposure_info(camera))
camera.close()
