#
# send pictures to server
#
import threading
import datetime
import requests
from io import BytesIO, open
from config import  APISERVER # DEBUG,

APIURL = APISERVER + "sendpic"
HTTP_TIMEOUT=25

#print (APIURL)

def SendFiles (files: str or [str], info=None, params=None):
    """ Send a bunch of file to the server 

    :param files: filesname(s) as a sting or a list of strings
    :param info: dict send as POST content
    :param param: dict sends as http request Get parameters
    :return: Result of operations
    :rtype: Boolean
    """
    DEBUG=False
    if DEBUG: print("SendFiles:", files, info, params)
    files_spec=None
    data_spec={}
    #info_spec=None
    if type(files) is list:
        files_spec=[]
        for f in files:
            files_spec.append(('Picture', (f, open(f,'rb'))))
    else:
        files_spec=[('Picture', (files, open(files,'rb')))]

    if params is not None:
        data_spec = params

    if info is not None:
        data_spec = { **data_spec, "info": info}
    if DEBUG:
        print('Data', data_spec)
        print ("filespec", files_spec)
    try:
        r = requests.post(APIURL, timeout=HTTP_TIMEOUT, files=files_spec, data=data_spec)
    except requests.exceptions.RequestException as e:
        print(e)
        return False

    if r.status_code == requests.codes.ok:
        if DEBUG:
            print('det gik godt')
            print(r.text)
        return True
    else:
        print('Noget gik galt: ', r.status_code)
        print(r.text)
    return False

def SendMemFiles (files, file_name="file", file_type="jpg", info=None, params=None):
    """ Send a bunch of memmory file to the server

    :param files: fd(s)  or a list of fd(s)
    :param filename: str
    :param file_type: type of file
    :param info: dict send as POST content
    :param param: dict sends as http request Get parameters
    :return: Result of operations
    :rtype: Boolean
    """
    DEBUG=False
    if DEBUG: print("SendFiles:", files, info, params)
    files_spec=None
    data_spec={}
    #info_spec=None

    if type(files) is list:
        files_spec=[]
        i = 1
        for f in files:
            f.seek(0)
            filename = file_name + str(i) + '.' + file_type
            #print(filename)
            files_spec.append(('Picture', (filename, f)))
            i = i+1
    else:
        filename = file_name + "." + file_type
        files.seek(0)
        files_spec={'Picture': (filename, files)}
    
    if params is not None:
        data_spec = params
    
    if info is not None:
        data_spec = { **data_spec, "info": info}
    if DEBUG:
        print('Data', data_spec)
        print ("filespec", files_spec)
    try:
        r = requests.post(APIURL, timeout=HTTP_TIMEOUT, files=files_spec, data=data_spec)
    except requests.exceptions.RequestException as e:
        print(e)
        return False
            
    if r.status_code == requests.codes.ok:
        if DEBUG:
            print('det gik godt')
            print(r.text)
        return True
    else:
        print('Noget gik galt: ', r.status_code)
        print(r.text)
    return False

def SendMemFiles_BG (files, file_name="file", file_type="jpg", info=None, params=None):
    x = threading.Thread(target=SendMemFiles, args=(files, file_name, file_type, info, params))
    x.start()
    return


def sendfile(name):
    print("thread start", datetime.datetime.now())
    print(name)
    with open('file1.jpg', 'rb') as fh:
        fd = BytesIO(fh.read())
    res = SendMemFiles_BG(fd, "testfile")
    print("thread end", datetime.datetime.now())




if __name__ == "__main__":
    print(datetime.datetime.now())
    with open('file1.jpg', 'rb') as fh:
        fd = BytesIO(fh.read())

    res = SendMemFiles_BG(fd, "testfile")
    # print ("res")
    # print(datetime.datetime.now())

    # x = threading.Thread(target=sendfile, args=(1,))
    # x.start()
    # print(datetime.datetime.now())
