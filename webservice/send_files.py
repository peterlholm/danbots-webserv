#
# send pictures to server
#
import threading
import datetime
from io import BytesIO, open
import requests
from wand_config import  APISERVER # DEBUG,

APIURL = APISERVER + "sendpic"
APIURL = APISERVER + "savefile"
HTTP_TIMEOUT=25
_DEBUG=False

#print (APIURL)

def send_files (files: str or [str], info=None, params=None):
    """ Send a bunch of file to the server
    :param files: filesname(s) as a sting or a list of strings
    :param info: dict send as POST content
    :param param: dict sends as http request Get parameters
    :return: Result of operations
    :rtype: Boolean
    """

    if _DEBUG:
        print("SendFiles:", files, info, params)
    files_spec=None
    data_spec={}
    #info_spec=None
    if isinstance(files, list):
        files_spec=[]
        for myfile in files:
            files_spec.append(('Picture', (myfile, open(myfile,'rb'))))
    else:
        files_spec=[('Picture', (files, open(files,'rb')))]

    if params is not None:
        data_spec = params

    if info is not None:
        data_spec = { **data_spec, "info": info}
    if _DEBUG:
        print('Data', data_spec)
        print ("filespec", files_spec)
    try:
        req = requests.post(APIURL, timeout=HTTP_TIMEOUT, files=files_spec, data=data_spec)
    except requests.exceptions.RequestException as ex:
        print(ex)
        return False

    if req.status_code == requests.codes.ok:  #pylint: disable=no-member
        if _DEBUG:
            print('det gik godt')
            print(req.text)
        return True
    else:
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

    if _DEBUG:
        print("SendFiles:", files, info, params)
    files_spec=None
    data_spec={}
    #info_spec=None

    if isinstance(files,list):
        files_spec=[]
        i = 1
        for fil in files:
            fil.seek(0)
            filename = file_name + str(i) + '.' + file_type
            #print(filename)
            files_spec.append(('Picture', (filename, fil)))
            i = i+1
    else:
        filename = file_name + "." + file_type
        files.seek(0)
        files_spec={'Picture': (filename, files)}

    if params is not None:
        data_spec = params

    if info is not None:
        data_spec = { **data_spec, "info": info}
    if _DEBUG:
        print('Data', data_spec)
        print ("filespec", files_spec)
    try:
        req = requests.post(APIURL, timeout=HTTP_TIMEOUT, files=files_spec, data=data_spec)
    except requests.exceptions.RequestException as ex:
        print(ex)
        return False

    if req.status_code == requests.codes.ok:  #pylint: disable=no-member
        if _DEBUG:
            print('det gik godt')
            print(req.text)
        return True
    else:
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

def sendfile(name):
    print("thread start", datetime.datetime.now())
    print(name)
    with open('file1.jpg', 'rb') as fd:
        fd2 = BytesIO(fd.read())
    send_mem_files_bg(fd2, "testfile")
    print("thread end", datetime.datetime.now())


if __name__ == "__main__":
    print(datetime.datetime.now())
    with open('webservice.py', 'rb') as fh:
        myfd = BytesIO(fh.read())
    RESULT = send_mem_files(myfd, "testfile", file_type='py', info={'myinfo': 22}, params={'myparams':"parameter"})
    print ("send file result", RESULT)
    send_mem_files_bg(myfd, "testfile", file_type='py')
    print ("send file in background")
