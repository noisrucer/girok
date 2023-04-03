import json
from rich import print

import girok.utils.general as general_utils
import girok.utils.display as display_utils
import girok.api.auth as auth_api

def match_passwords(pwd, confirm_pwd):
    if pwd != confirm_pwd:
        print("Confirm password does not match.")
        exit(0)
        

def get_mode(config_path):
    with open(config_path, "r") as f:
        cfg = json.load(f)
        if "mode" not in cfg:
            return None
        return cfg['mode']
            
        
def remove_access_token(config_path):
    with open(config_path, 'r') as f:
        org_data = json.load(f)
        del org_data['access_token']
        org_data['mode'] = "off"

    general_utils.write_json(config_path, org_data)
        
        
def get_access_token_from_json(fpath):
    with open(fpath, 'r') as f:
        data = json.load(f)
        if "access_token" in data:
            return data['access_token']
        else:
            return None
        
def get_user_email_from_json(fpath):
    with open(fpath, 'r') as f:
        data = json.load(f)
        if "email" in data:
            return data['email']
        else:
            return None
        

def build_jwt_header(fpath):
    return {
        "Authorization": "Bearer " + get_access_token_from_json(fpath)
    }
        

def is_logged_in(access_token):
    if access_token is None:
        return False
    resp = auth_api.validate_access_token(access_token)
    return True if resp.status_code == 200 else False


def log_out_from_guest(cfg_path: str):
    general_utils.update_json(cfg_path, {"mode": "off"})
    

def log_out_from_user(cfg_path: str):
    with open(cfg_path, 'r') as f:
        org_data = json.load(f)
        del org_data['access_token']
        org_data['mode'] = "off"

    general_utils.write_json(cfg_path, org_data)


def is_logged_in_as_guest(cfg_path: str):
    mode = get_mode(cfg_path)
    return True if mode == "guest" else False


def is_logged_in_as_user(cfg_path: str):
    access_token = get_access_token_from_json(cfg_path)
    if access_token is None:
        return False
    resp = auth_api.validate_access_token(access_token)
    return True if resp.status_code == 200 else False
        

def store_access_token_to_json(fpath, access_token):
    data = {"access_token": access_token}
    general_utils.update_json(fpath, data)
    