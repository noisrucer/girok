import requests
from girok.config import get_config
import girok.utils.general as general_utils
import girok.utils.display as display_utils

cfg = get_config()

base_url = cfg.base_url 
email_base_url = cfg.email_base_url

def register(email, password):
    resp = requests.post(email_base_url + "/register", json={
        "email": email,
        "password": password
    })
    return resp

def verify_verification_code(email, verification_code):
    resp = requests.post(email_base_url + "/register/verification_code", json={
        "email": email,
        "verification_code": verification_code
    })
    if resp.status_code == 200:
        return True
    elif resp.status_code == 401:
        err_msg = general_utils.bytes2dict(resp.content)['detail']
        display_utils.center_print(err_msg, type="error")
        exit(0)
    else:
        err_msg = general_utils.bytes2dict(resp.content)['detail'][0]['msg']
        print(err_msg)
        display_utils.center_print(str(err_msg), type="error") 
        exit(0)
    

def login(email, password):
    files = { 
        "username": (None, email),
        "password": (None, password)
    }
    
    resp = requests.post(base_url + "/login", files=files)
    return resp


def validate_access_token(access_token):
    options = {
        "headers": {
        "Authorization": "Bearer " + access_token,
        }
    }
    

    resp = requests.get(base_url + "/validate-access-token", headers=options['headers'])
    return resp