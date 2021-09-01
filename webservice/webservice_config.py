#
# read config and generate global coonstants
#
import os
#import time
#import datetime
import configparser
#import requests
#import signal

MYDEBUG=False
WINDOWS=False
CONFIGFILE="/etc/danwand.conf"

if os.name=='nt':
    CONFIGFILE=r"..\..\danwand.conf"
    WINDOWS=True
else:
    pass

if MYDEBUG:
    print ("Reading config file")

def save_config(config):
    with open(CONFIGFILE, 'w') as configfile:
        config.write(configfile)

# read config file

myconfig = configparser.ConfigParser()
myconfig.read_file(open(CONFIGFILE,'r'))
DEBUG=myconfig.getboolean('debug','debug',fallback=False)
DEVICEID = myconfig.get('device','deviceid',fallback='11223344')

#print ('Sections: ', config.sections())
API_SERVER=myconfig['server']['apiserver']
COMPUTE_SERVER=myconfig['server']['computeserver']

# hw

LEDHW=''
if myconfig.has_section('hw'):
    LEDHW = myconfig['hw'].get('led','')

print("Led: ", LEDHW)
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

if not myconfig.has_section('capture_3d'):
    myconfig.add_section('capture_3d')
    myconfig['capture_3d']['exposure_compensation'] = "0"
    myconfig['capture_3d']['flash'] = "0.1"
    myconfig['capture_3d']['dias'] = "1.0"
    myconfig['capture_3d']['capture_delay'] = "0.0"
    myconfig['capture_3d']['number_pictures'] = "3"
    myconfig['capture_3d']['picture_interval'] = "0.3"
    save_config(myconfig)

CAPTURE_3D = dict(myconfig.items('capture_3d'))
ZOOM = myconfig['capture_3d'].getfloat('zoom',None)

print("Zoom:", ZOOM)
