from typing import Union
from textual import log
from datetime import datetime
import requests

from girok.config import get_config
import girok.utils.auth as auth_utils
import girok.utils.display as display_utils
import girok.utils.general as general_utils
import girok.utils.task as task_utils
import girok.constants as constants

cfg = get_config()

def create_task(task_data: dict):
    resp = requests.post(
        cfg.base_url + "/tasks",
        json=task_data,
        headers=auth_utils.build_jwt_header(cfg.config_path)
    )
    if resp.status_code == 201:
        task = general_utils.bytes2dict(resp.content)
        task_id = task['task_id']
        return task_id
    elif resp.status_code == 400:
        err_msg = general_utils.bytes2dict(resp.content)['detail']
        display_utils.center_print(err_msg, constants.DISPLAY_TERMINAL_COLOR_ERROR)
    else:
        display_utils.center_print("Error occurred.", constants.DISPLAY_TERMINAL_COLOR_ERROR)
        

def get_single_task(task_id: int):
    resp = requests.get(
        cfg.base_url + f"/tasks/{task_id}",
        headers=auth_utils.build_jwt_header(cfg.config_path),
    )
    if resp.status_code == 200:
        task = general_utils.bytes2dict(resp.content)
        return task
    elif resp.status_code == 400:
        err_msg = general_utils.bytes2dict(resp.content)['detail']
        display_utils.center_print(err_msg, constants.DISPLAY_TERMINAL_COLOR_ERROR)
    else:
        display_utils.center_print(resp.content, constants.DISPLAY_TERMINAL_COLOR_ERROR)
 


def get_tasks(
    cats: Union[list, None] = None,
    start_date: Union[str, None] = None,
    end_date: Union[str, None] = None,
    tag: Union[str, None] = None,
    priority: Union[int, None] = None,
    no_priority: bool = False,
    view: str = "category"
):
    query_str_obj = {
        "category": cats,
        "start_date": start_date,
        "end_date": end_date,
        "tag": tag,
        "priority": priority,
        "no_priority": no_priority,
        "view": view
    }
    resp = requests.get(
        cfg.base_url + "/tasks",
        headers=auth_utils.build_jwt_header(cfg.config_path),
        params=query_str_obj
    )
    return resp


def remove_task(task_id: int):
    resp = requests.delete(
        cfg.base_url + f"/tasks/{task_id}",
        headers=auth_utils.build_jwt_header(cfg.config_path),
    )
    return resp
    

def get_tags():
    resp = requests.get(
        cfg.base_url + "/tasks/tags",
        headers=auth_utils.build_jwt_header(cfg.config_path)
    )
    
    return resp
    
    
def change_task_tag(task_id: int, new_tag_name: str):
    resp = requests.patch(
        cfg.base_url + f"/tasks/{task_id}/tag",
        headers=auth_utils.build_jwt_header(cfg.config_path),
        json={
            "new_tag_name": new_tag_name
        }
    )
    
    if resp.status_code == 204:
        display_utils.center_print(f"Successfully renamed [ID: {task_id}] tag to {new_tag_name}.", "black on green")
    elif resp.status_code == 400:
        err_msg = general_utils.bytes2dict(resp.content)['detail']
        display_utils.center_print(err_msg, constants.DISPLAY_TERMINAL_COLOR_ERROR)
    else:
        display_utils.center_print(resp.content, constants.DISPLAY_TERMINAL_COLOR_ERROR)
        
        
def change_task_priority(task_id: int, new_priority: int):
    resp = requests.patch(
        cfg.base_url + f"/tasks/{task_id}/priority",
        headers=auth_utils.build_jwt_header(cfg.config_path),
        json={
            "new_priority": new_priority
        }
    )
    
    if resp.status_code == 204:
        display_utils.center_print(f"Successfully change [ID: {task_id}] priority to {new_priority}.", "black on green")
    elif resp.status_code == 400:
        err_msg = general_utils.bytes2dict(resp.content)['detail']
        display_utils.center_print(err_msg, constants.DISPLAY_TERMINAL_COLOR_ERROR)
    else:
        display_utils.center_print(resp.content, constants.DISPLAY_TERMINAL_COLOR_ERROR)
        

def change_task_date(task_id: int, new_date: str):
    resp = requests.patch(
        cfg.base_url + f"/tasks/{task_id}/date",
        headers=auth_utils.build_jwt_header(cfg.config_path),
        json={
            "new_date": new_date
        }
    )
    
    if resp.status_code == 204:
        display_utils.center_print(f"Successfully change [ID: {task_id}] date to {new_date}.", "black on green")
    elif resp.status_code == 400:
        err_msg = general_utils.bytes2dict(resp.content)['detail']
        display_utils.center_print(err_msg, constants.DISPLAY_TERMINAL_COLOR_ERROR)
    else:
        display_utils.center_print(resp.content, constants.DISPLAY_TERMINAL_COLOR_ERROR)
        

    
