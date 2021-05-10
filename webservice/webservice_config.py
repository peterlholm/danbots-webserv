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

# camera

if not myconfig.has_section('camera'):
    myconfig.add_section('camera')
    myconfig['camera']['maxframerate'] = "10"
    myconfig['camera']['warmup_time'] = "0.5"
    save_config(myconfig)

MAXFRAMERATE = float(myconfig['camera'].get('maxframerate'))
WARMUP_TIME = float(myconfig['camera'].get('warmup_time'))
