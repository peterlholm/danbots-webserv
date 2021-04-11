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

# read config file

myconfig = configparser.ConfigParser()
myconfig.read_file(open(CONFIGFILE,'r'))
DEBUG=myconfig.getboolean('debug','debug',fallback=False)

DEVICEID = myconfig.get('device','deviceid',fallback='11223344')

# if 'debug' in config:
#     DEBUG=config['debug'].get('debug', DEBUG)
#print ('Sections: ', config.sections())
APISERVER=myconfig['server']['apiserver']
#print(APISERVER)
# scanpicture = config[SCAN_PICTURE]
# no_picture = scanpicture.get(NUMBER_PIC, NO_PICTURE)
#print("ApiServer", APISERVER)
#print ("DEBUG", DEBUG)
