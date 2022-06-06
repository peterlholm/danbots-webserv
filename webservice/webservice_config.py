"Initialise webservie config"
# read config and generate global constants
#
#import os
from sys import platform
import configparser

_DEBUG=False
WINDOWS=False
CONFIGFILE="/etc/danwand.conf"

if platform=="win32":
    print("windows")
    CONFIGFILE = '..\\danwand.conf'

# with open ("/etc/debian_version", "r") as myfile:
#     DEBIAN_VERSION=myfile.readlines()

# print ("Debian version: " + DEBIAN_VERSION[0])

if _DEBUG:
    print ("Reading config file")

def save_config(config):
    "save the current config in file"
    with open(CONFIGFILE, 'w', encoding="UTF8") as configfile:
        config.write(configfile)

# read config file

myconfig = configparser.ConfigParser(strict=False)
myconfig.read_file(open(CONFIGFILE,'r', encoding="UTF8"))
DEBUG=myconfig.getboolean('debug','debug',fallback=False)
DEVICEID = myconfig.get('device','deviceid',fallback='11223344')

#print ('Sections: ', config.sections())
API_SERVER=myconfig['server']['apiserver']
COMPUTE_SERVER=myconfig['server']['computeserver']

# hw

LEDHW=''
if myconfig.has_section('hw'):
    LEDHW = myconfig['hw'].get('led','')

#print("Led: ", LEDHW)
# camera

if not myconfig.has_section('camera'):
    myconfig.add_section('camera')
    myconfig['camera']['minframerate'] = "5"
    myconfig['camera']['maxframerate'] = "10"
    myconfig['camera']['warmup_time'] = "0.1"
    myconfig['camera']['width'] = "160"
    myconfig['camera']['height'] = "160"
    save_config(myconfig)
MINFRAMERATE = float(myconfig['camera'].get('minframerate'))
MAXFRAMERATE = float(myconfig['camera'].get('maxframerate'))
WARMUP_TIME = float(myconfig['camera'].get('warmup_time',1))
HEIGHT = int(myconfig['camera'].get('height',160))
WIDTH = int(myconfig['camera'].get('width',160))
ZOOM = float(myconfig['camera'].get('zoom',1))

if not myconfig.has_section('capture_3d'):
    myconfig.add_section('capture_3d')
    myconfig['capture_3d']['exposure_compensation'] = "0"
    myconfig['capture_3d']['flash'] = "0.07"
    myconfig['capture_3d']['dias'] = "1.0"
    myconfig['capture_3d']['capture_delay'] = "1.0"
    myconfig['capture_3d']['number_pictures'] = "3"
    myconfig['capture_3d']['picture_interval'] = "1.3"
    save_config(myconfig)

CAPTURE_3D = dict(myconfig.items('capture_3d'))

#ZOOM = myconfig['capture_3d'].getfloat('zoom',None)

# if not myconfig.has_section('capture_2d'):
#     myconfig.add_section('capture_2d')
#     #myconfig['capture_2d']['exposure_compensation'] = "0"
#     myconfig['capture_2d']['flash'] = "0.2"
#     myconfig['capture_2d']['capture_delay'] = "0.5"
#     myconfig['capture_2d']['number_pictures'] = "10"
#     myconfig['capture_2d']['picture_interval'] = "1.0"
#     save_config(myconfig)

# CAPTURE_2D = dict(myconfig.items('capture_2d'))
