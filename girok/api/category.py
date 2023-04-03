import requests
from rich.console import Console

from girok.config import get_config
import girok.utils.auth as auth_utils
import girok.utils.general as general_utils
import girok.utils.display as display_utils
import girok.constants as constants

# Guest mode imports
import girok.server.src.category.router as category_router

console = Console()
cfg = get_config()

def get_categories():
    mode = auth_utils.get_mode(cfg.config_path)
    if mode == "user":
        resp = requests.get(
            cfg.base_url + "/categories",
            headers=auth_utils.build_jwt_header(cfg.config_path)
        )
        if resp.status_code == 200:
            return general_utils.bytes2dict(resp.content)
    elif mode == "guest":
        resp = category_router.get_all_categories()
        return resp
    

def add_category(cat_str: str, color=None):
    mode = auth_utils.get_mode(cfg.config_path)
    cats = cat_str.split('/')
    if mode == "user":
        resp = requests.post(
            cfg.base_url + "/categories",
            json={
                "names": cats,
                "color": color
            },
            headers=auth_utils.build_jwt_header(cfg.config_path)
        )
        if resp.status_code == 201:
            display_utils.center_print("Category added successfully!", type="success")
            cats_dict = get_categories()
            display_utils.display_categories(cats_dict, highlight_cat=cat_str)
        elif resp.status_code == 400:
            err_msg = general_utils.bytes2dict(resp.content)['detail']
            display_utils.center_print(err_msg, type="error")
        else:
            print(resp)
        return resp
    elif mode == "guest":
        resp = category_router.create_category({"names": cats, "color": color})
        if resp['success']:
            display_utils.center_print("Category added successfully!", type="success")
            cats_dict = get_categories()
            display_utils.display_categories(cats_dict, highlight_cat=cat_str)
        else:
            display_utils.center_print(resp['detail'], type="error")
        
        
def remove_category(cat_str: str):
    mode = auth_utils.get_mode(cfg.config_path)
    cats = cat_str.split('/')
    if mode == "user":
        resp = requests.delete(
            cfg.base_url + "/categories",
            json={
                "cats": cats
            },
            headers=auth_utils.build_jwt_header(cfg.config_path)
        )
        if resp.status_code == 204:
            display_utils.center_print(f"Deleted {cat_str} successfully.", type="success")
            cats_dict = get_categories()
            display_utils.display_categories(cats_dict)
        elif resp.status_code == 400:
            err_msg = general_utils.bytes2dict(resp.content)['detail']
            display_utils.center_print(err_msg, type="error")
        else:
            display_utils.center_print(resp.content, type="error")
    elif mode == "guest":
        resp = category_router.delete_category({"cats": cats})
        if resp['success']:
            display_utils.center_print(f"Deleted {cat_str} successfully.", type="success")
            cats_dict = get_categories()
            display_utils.display_categories(cats_dict)
        else:
            display_utils.center_print(resp['detail'], type="error")
            
        
def rename_category(cat_str: str, new_name: str):
    mode = auth_utils.get_mode(cfg.config_path)
    cats = cat_str.split('/')
    
    if mode == "user":
        resp = requests.patch(
            cfg.base_url + "/categories/name",
            json={
                "cats": cats,
                "new_name": new_name
            },
            headers=auth_utils.build_jwt_header(cfg.config_path)
        )
        if resp.status_code == 204:
            new_cat = '/'.join(cat_str.split('/')[:-1] + [new_name])
            display_utils.center_print(f"Successfully renamed {cat_str} to {new_cat}.", type="success")
            cats_dict = get_categories()
            display_utils.display_categories(cats_dict, highlight_cat=new_cat)
        elif resp.status_code == 400:
            err_msg = general_utils.bytes2dict(resp.content)['detail']
            display_utils.center_print(err_msg, type="error")
        else:
            display_utils.center_print(resp.content, type="error")
    elif mode == "guest":
        resp = category_router.rename_category({
            "cats": cats,
            "new_name": new_name
        })
        if resp['success']:
            new_cat = '/'.join(cat_str.split('/')[:-1] + [new_name])
            display_utils.center_print(f"Successfully renamed {cat_str} to {new_cat}.", type="success")
            cats_dict = get_categories()
            display_utils.display_categories(cats_dict, highlight_cat=new_cat)
        else:
            display_utils.center_print(resp['detail'], type="error")


def move_category(cat_str: str, new_parent_cat_str: str):
    mode = auth_utils.get_mode(cfg.config_path)
    if cat_str.endswith('/'):
        cat_str = cat_str[:-1]
    if new_parent_cat_str.endswith('/'):
        new_parent_cat_str = new_parent_cat_str[:-1]
        
    cats = cat_str.split('/') if cat_str else []
    new_parent_cats = new_parent_cat_str.split('/') if new_parent_cat_str else []

    if mode == "user":
        resp = requests.patch(
            cfg.base_url + "/categories/parent",
            json={
                "cats": cats,
                "new_parent_cats": new_parent_cats
            },
            headers=auth_utils.build_jwt_header(cfg.config_path)
        )
        if resp.status_code == 200:
            new_cat = '/'.join(new_parent_cat_str.split('/') + [cat_str.split('/')[-1]])
            display_utils.center_print(f"Successfully moved {cat_str} to {new_parent_cat_str}/.", type="success")
            cats_dict = get_categories()
            display_utils.display_categories(cats_dict, highlight_cat=new_cat)
        elif resp.status_code == 400:
            err_msg = general_utils.bytes2dict(resp.content)['detail']
            display_utils.center_print(err_msg, type="error")
        else:
            display_utils.center_print(resp.content, type="error")
        return resp
    elif mode == "guest":
        resp = category_router.move_category({
            "cats": cats,
            "new_parent_cats": new_parent_cats
        })
        if resp['success']:
            new_cat = '/'.join(new_parent_cat_str.split('/') + [cat_str.split('/')[-1]])
            display_utils.center_print(f"Successfully moved {cat_str} to {new_parent_cat_str}/.", type="success")
            cats_dict = get_categories()
            display_utils.display_categories(cats_dict, highlight_cat=new_cat)
        else:
            display_utils.center_print(resp['detail'], type="error") 


def get_last_cat_id(cats: list):
    mode = auth_utils.get_mode(cfg.config_path)
    if mode == "user":
        resp = requests.get(
            cfg.base_url + "/categories/last-cat-id",
            json={
                "cats": cats
            },
            headers=auth_utils.build_jwt_header(cfg.config_path)
        )
        if resp.status_code == 200:
            return general_utils.bytes2dict(resp.content)['cat_id']
        elif resp.status_code == 400:
            err_msg = general_utils.bytes2dict(resp.content)['detail']
            display_utils.center_print(err_msg, type="error")
            exit(0)
        else:
            display_utils.center_print(resp.content, type="error")
            exit(0)
    elif mode == "guest":
        resp = category_router.get_last_cat_id({"cats": cats})
        if resp['success']:
            return resp['cat_id']
        else:
            display_utils.center_print(resp['detail'], type="error")
    exit(0)
            
        
        
def get_category_color(cat_id: int):
    mode = auth_utils.get_mode(cfg.config_path)
    if mode == "user":
        resp = requests.get(
            cfg.base_url + f"/categories/{cat_id}/color",
            headers=auth_utils.build_jwt_header(cfg.config_path)
        )
        
        if resp.status_code == 200:
            return general_utils.bytes2dict(resp.content)['color']
        elif resp.status_code == 400:
            err_msg = general_utils.bytes2dict(resp.content)['detail']
            display_utils.center_print(err_msg, type="error")
            exit(0)
        else:
            display_utils.center_print(resp.content, type="error")
            exit(0)
    elif mode == "guest":
        resp = category_router.get_category_color(cat_id)
        if resp['success']:
            return resp['color']
        else:
            display_utils.center_print(resp.content, type="error")
    exit(0)
    
def get_color_dict():
    mode = auth_utils.get_mode(cfg.config_path)
    if mode == "user":
        resp = requests.get(
            cfg.base_url + "/categories/color",
            headers=auth_utils.build_jwt_header(cfg.config_path)
        )
        if resp.status_code == 200:
            color_dict = general_utils.bytes2dict(resp.content)
            return color_dict
        elif resp.status_code == 400:
            err_msg = general_utils.bytes2dict(resp.content)['detail']
            display_utils.center_print(err_msg, type="error")
        else:
            display_utils.center_print("Error occurred.", type="error")
    elif mode == "guest":
        resp = category_router.get_category_colors_dict()
        if resp['success']:
            return resp['colors']    
        else:
            display_utils.center_print("Error occurred.", type="error")
    exit(0)
            