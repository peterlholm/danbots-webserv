#
# send pictures to server
#
import threading
import datetime
from io import BytesIO, open
import requests
from webservice_config import  API_SERVER, COMPUTE_SERVER, DEVICEID

# live
API_SENDPIC = 'sendpic'
API_SAVEFILE = 'savefile'
# compute
API_SCAN3D = 'scan3d'
API_START = 'start3d'
API_STOP = 'stop3d'

HTTP_TIMEOUT=16
_DEBUG=False

def error_handling(myfunction):
    
    def func(*a, **kw):   
        try:
            res = myfunction(*a, **kw)
        except requests.exceptions.RequestException as ex:
            print(ex)
            return False
        return res
    return func


def sendfile(name):
    """ Send one file from disk """
    print("thread start", datetime.datetime.now())
    print(name)
    files_spec = {'file': (name, open(name,'rb') )}
    data_spec =None
    req = requests.post(API_SERVER + API_SAVEFILE, timeout=HTTP_TIMEOUT, files=files_spec, data=data_spec)
    print (req)
    print("thread end", datetime.datetime.now())

def send_file_object(file_object, file_name, data=None, url=None):
    if not url:
        url=API_SERVER + API_SAVEFILE
    file_spec = {'file': (file_name, file_object) }
    req = requests.post(url, timeout=HTTP_TIMEOUT, files=file_spec, data=data)
    if not req:
        print(req)
    return req

def send_file_objects(name_object_list, data=None):
    file_spec = []
    for f in name_object_list:
        file_spec.append(('files', f))
    req = requests.post(API_SERVER + API_SAVEFILE, timeout=HTTP_TIMEOUT, files=file_spec, data=data)
    if not req:
        print(req)
    return req


def sendmemfile(name):
    """ Send one file from disk """
    print("thread start", datetime.datetime.now())
    print(name)
    with open(name, 'rb') as fd:
        fd2 = BytesIO(fd.read())
    send_mem_files_bg(fd2, "testfile")
    print("thread end", datetime.datetime.now())

def send_api_request(function, data=None):
    url = API_SERVER + function
    req = requests.post(url, timeout=HTTP_TIMEOUT, data=data)
    if not req.status_code:
        print('Noget gik galt: ', req.status_code)
        print(req.text)
        return False
    return True

def send_start():
    apiurl = COMPUTE_SERVER + API_START
    data_spec = {"deviceid": DEVICEID }
    try:
        req = requests.post(apiurl, timeout=HTTP_TIMEOUT, data=data_spec)
    except requests.exceptions.RequestException as ex:
        print(datetime.datetime.now(), ex)
        return False
    if not req.status_code == requests.codes.ok:  #pylint: disable=no-member
        print('Noget gik galt: ', req.status_code)
        print(req.text)
        return False
    return True

def send_stop():
    apiurl = COMPUTE_SERVER + API_STOP
    data_spec = {"deviceid": DEVICEID }
    req = requests.post(apiurl, timeout=HTTP_TIMEOUT, data=data_spec)
    if not req.status_code == requests.codes.ok:  #pylint: disable=no-member
        print('Noget gik galt: ', req.status_code)
        print(req.text)
        return False
    return True

def send_files (files: str or [str], info=None, params=None):
    """ Send a bunch of file to the server
    :param files: filesname(s) as a sting or a list of strings
    :param info: dict send as POST content
    :param param: dict sends as http request Get parameters
    :return: Result of operations
    :rtype: Boolean
    """
    apiurl = COMPUTE_SERVER + API_SENDPIC
    if _DEBUG:
        print("SendFiles:", files, info, params)
    files_spec=None
    data_spec={}
    #info_spec=None
    if isinstance(files, list):
        files_spec=[]
        for myfile in files:
            files_spec.append(('Pictures', (myfile, open(myfile,'rb'))))
    else:
        files_spec=[('Picture', (files, open(files,'rb')))]

    if params is not None:
        data_spec = params

    if info is not None:
        data_spec = { **data_spec, "info": info, "deviceid": DEVICEID}
    if _DEBUG:
        print('Data', data_spec)
        print ("filespec", files_spec)
    try:
        req = requests.post(apiurl, timeout=HTTP_TIMEOUT, files=files_spec, data=data_spec)
    except requests.exceptions.RequestException as ex:
        print(ex)
        return False

    if req.status_code == requests.codes.ok:  #pylint: disable=no-member
        if _DEBUG:
            print('det gik godt')
            print(req.text)
        return True

    print('Noget gik galt: ', req.status_code)
    print(req.text)
    return False

def send_mem_files (files, file_name="file", file_type="jpg", info=None, params=None):
    """ Send a bunch of memmory file to the server

    :param files: fd(s)  or a list of fd(s)
    :param filename: str
    :param file_type: type of file
    :param info: dict send as POST content
    :param param: dict sends as http request Get parameters
    :return: Result of operations
    :rtype: Boolean
    """
    apiurl = COMPUTE_SERVER + API_SCAN3D
    if _DEBUG:
        print("SendFiles:", files, info, params)
    files_spec=None
    data_spec={}
    #info_spec=None
    namelist =['color_picture','french_picture','noLight_picture']
    if isinstance(files,list):
        files_spec=[]
        i = 1
        for fil in files:
            fil.seek(0)
            filename = file_name + str(i) + '.' + file_type
            #print(filename)
            files_spec.append((namelist.pop(0), (filename, fil)))
            i = i+1
    else:
        filename = file_name + "." + file_type
        files.seek(0)
        files_spec={'Picture': (filename, files)}

    if params is not None:
        data_spec = params

    if info is not None:
        data_spec = { **data_spec, "info": info, "deviceid": DEVICEID}
    if _DEBUG:
        print('Data', data_spec)
        print ("filespec", files_spec)
    try:
        req = requests.post(apiurl, timeout=HTTP_TIMEOUT, files=files_spec, data=data_spec)
    except requests.exceptions.RequestException as ex:
        print(ex)
        return False

    if req.status_code == requests.codes.ok:  #pylint: disable=no-member
        if _DEBUG:
            print('det gik godt')
            print(req.text)
        return True
    print('Noget gik galt: ', req.status_code)
    print(req.text)
    return False

def send_mem_files_bg (files, file_name="file", file_type="jpg", info=None, params=None):
    # myfiles=BytesIO()
    # myfilename=file_name
    # myfiletype=file_type
    # myinfo=info
    # myparams=params
    th1 = threading.Thread(target=send_mem_files, args=(files, file_name, file_type, info, params))
    th1.start()


# if __name__ == "__main__":
#     fd = open('pic_3d.py','rb')
#     fd2 = open('pic_2d.py','rb')

#     send_file_objects([('fil3.py', fd),('fil2.py', fd2)], {"dummy":"hhh"})
    