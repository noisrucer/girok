import requests
from girok.config import get_config
cfg = get_config()

base_url = cfg.base_url 

def register(email, password):
    resp = requests.post(base_url + "/register", json={
        "email": email,
        "password": password
    })
    return resp
    

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