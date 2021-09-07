#
# send request to server
#
#import threading
import datetime
#from io import BytesIO, open
import requests
from webservice_config import  API_SERVER, COMPUTE_SERVER, DEVICEID

HTTP_TIMEOUT=5
_DEBUG=False

def send_api_request(function, post_data=None, url=API_SERVER):
    try:
        url_req = API_SERVER + function
        req = requests.post(url_req, timeout=HTTP_TIMEOUT, post_data=data)
    except requests.exceptions.RequestException as ex:
        print(ex)
        return False
    if not req.status_code:
        print('Noget gik galt: ', req.status_code)
        print(req.text)
        return False
    return True



send_api_request("dummy")
