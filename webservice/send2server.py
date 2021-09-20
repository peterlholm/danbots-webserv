#
# send request to server
#
import threading
import os.path
#import datetime
#from io import BytesIO, open
import requests
from webservice_config import  API_SERVER, COMPUTE_SERVER, DEVICEID

SENDFILES = "sendfiles"

HTTP_TIMEOUT=5
_DEBUG=False

def send_api_request(function, post_data=None, url=API_SERVER):
    params = {"deviceid": DEVICEID}

    if post_data:
        params.update(post_data)
    try:
        url_req = url + function
        print (params)
        req = requests.post(url_req, timeout=HTTP_TIMEOUT, data=params)
    except requests.exceptions.RequestException as ex:
        print(ex)
        return False
    if not req.status_code == requests.codes.ok:    #pylint: disable=no-member
        print('Noget gik galt: ', req.status_code)
        print(req.text)
        return False
    return True

def send_api_request_bg (function, post_data=None, url=API_SERVER):
    th1 = threading.Thread(target=send_api_request, args=(function, post_data, url))
    th1.start()

def post_file_object(function, fileobj, post_data=None, url=COMPUTE_SERVER):
    url_req = url + function
    file_spec = []

    params = {"deviceid": DEVICEID}
    if post_data:
        params.update(post_data)

    file_spec = {'Picture': ("finavn.png", fileobj)}
    try:
        req = requests.post(url_req, timeout=HTTP_TIMEOUT, files=file_spec, data=params)
    except requests.exceptions.RequestException as ex:
        print(ex)
        return False
    if req.status_code == requests.codes.ok:  #pylint: disable=no-member
        print('det gik godt')
        print(req.text)
        return True
    print('Noget gik galt: ', req.status_code)
    print(req.text)
    return False



def post_file_objects(function, name_object_list, params=None,url=COMPUTE_SERVER):
    url_req = url + function
    file_spec = []
    for f in name_object_list:
        file_spec.append(('files', f))
    print(url_req)
    print(params)
    req = requests.post(url_req, timeout=HTTP_TIMEOUT, files=file_spec, data=params)
    if not req:
        print(req)
    return req

def send_files (files, post_data=None, url=COMPUTE_SERVER):
    """ Send a bunch of file to the server
    :param files: filesname(s) as a sting or a list of strings
    :param post_data: dict send as POST content
    :return: Result of operations
    :rtype: Boolean
    """
    apiurl = url + SENDFILES
    if _DEBUG:
        print("SendFiles:", files, post_data)
    files_spec=None
    data_spec={}
    files_spec=[]
    for myfile in files:
        filename = os.path.basename(myfile)
        files_spec.append(('files', (filename, open(myfile,'rb'))))

    params = {"deviceid": DEVICEID}
    if post_data:
        params.update(post_data)

    if _DEBUG:
        print('Data', data_spec)
        print ("filespec", files_spec)
    try:
        req = requests.post(apiurl, timeout=HTTP_TIMEOUT, files=files_spec, data=params)
    except requests.exceptions.RequestException as ex:
        print(ex)
        return False

    if req.status_code == requests.codes.ok:  #pylint: disable=no-member
        if _DEBUG:
            print('det gik godt')
            print(req.text)
        print (req.json())
        return req.json()

    print('Noget gik galt: ', req.status_code)
    print(req.text)
    return False

if __name__ == '__main__':
    param= {
        "my": "peter",
        "ole": 0
    }
    #send_api_request("savefile", post_data=param)
    filer = ["/tmp/calib/color.jpg", "/tmp/calib/color.json"]
    send_files(filer, post_data=param)
