import re

import typer
from rich import print
from rich.console import Console
from rich.table import Table
from rich.align import Align
from rich.padding import Padding
from rich.panel import Panel

import constants as constants
from config import get_config
import api.category as category_api
import utils.general as general_utils
import utils.display as display_utils
import utils.auth as auth_utils
import webbrowser

app = typer.Typer(rich_markup_mode='rich')
console = Console()
cfg = get_config()

def category_callback(ctx: typer.Context, param: typer.CallbackParam, value: str):
    command_name = ctx.command.name
    if value is None:
        return None

    if not re.match("^([a-zA-Z0-9]+/)*[a-zA-Z0-9]+/?$", value):
        raise typer.BadParameter("[Invalid category path] Category path must be in 'xx/yy/zz format.'")

    if value.endswith('/'):
        value =value[:-1]
        
    if value == 'none':
        raise typer.BadParameter("Sorry, 'none' is a reserved category name.")
    return value


@app.command("showcat")
def show_categories():
    cats_dict = category_api.get_categories()
    print(cats_dict)
    text = Align.center("[bold red]Task Categories[/bold red]")
    display_utils.center_print(text, constants.DISPLAY_TERMINAL_COLOR_TITLE)
    display_utils.display_categories(cats_dict)
    

@app.command("addcat")
def add_category(
    cat: str = typer.Argument(..., help="Category path - xx/yy/zz..", callback=category_callback),
    color: str = typer.Option(None, "-c", "--color", help="Color for category")
):
    resp = category_api.add_category(cat, color)
    if resp.status_code == 201:
        display_utils.center_print("Task added successfully!", constants.DISPLAY_TERMINAL_COLOR_SUCCESS)
        cats_dict = category_api.get_categories()
        display_utils.display_categories(cats_dict, highlight_cat=cat)
    elif resp.status_code == 400:
        err_msg = general_utils.bytes2dict(resp.content)['detail']
        display_utils.center_print(err_msg, constants.DISPLAY_TERMINAL_COLOR_ERROR)
    else:
        print(resp)
    
    
@app.command("rmcat")
def remove_category(cat: str = typer.Argument(..., help="Category path - xx/yy/zz..")):
    confirm_rm = typer.confirm(f"[WARNING] Are you sure to delete '{cat}'?\nAll the subdirectories will also be deleted.")
    if not confirm_rm:
        exit(0)
        
    resp = category_api.remove_category(cat)
    if resp.status_code == 204:
        display_utils.center_print(f"Deleted {cat} successfully.", constants.DISPLAY_TERMINAL_COLOR_SUCCESS)
        cats_dict = category_api.get_categories()
        display_utils.display_categories(cats_dict)
    elif resp.status_code == 400:
        err_msg = general_utils.bytes2dict(resp.content)['detail']
        display_utils.center_print(err_msg, constants.DISPLAY_TERMINAL_COLOR_ERROR)
    else:
        display_utils.center_print(resp.content, constants.DISPLAY_TERMINAL_COLOR_ERROR)
        
        
@app.command("rncat")
def rename_category(
    cat: str = typer.Argument(..., help="Category path - xx/yy/zz.."),
    new_name: str = typer.Argument(..., help="New category name")
):
    resp = category_api.rename_category(cat, new_name)
    if resp.status_code == 200:
        new_cat = '/'.join(cat.split('/')[:-1] + [new_name])
        display_utils.center_print(f"Successfully renamed {cat} to {new_cat}.", "black on green")
        cats_dict = category_api.get_categories()
        display_utils.display_categories(cats_dict, highlight_cat=new_cat)
    elif resp.status_code == 400:
        err_msg = general_utils.bytes2dict(resp.content)['detail']
        display_utils.center_print(err_msg, constants.DISPLAY_TERMINAL_COLOR_ERROR)
    else:
        display_utils.center_print(resp.content, constants.DISPLAY_TERMINAL_COLOR_ERROR)
        
        
@app.command("mvcat")
def move_category(
    cat: str = typer.Argument(..., help="Category path - xx/yy/zz.."),
    new_parent_cat: str = typer.Argument(..., help="New supercategory path - xx/yy/")
):
    if new_parent_cat.endswith('/'):
        new_parent_cat = new_parent_cat[:-1]
    resp = category_api.move_category(cat, new_parent_cat)
    if resp.status_code == 200:
        new_cat = '/'.join(new_parent_cat.split('/') + [cat.split('/')[-1]])
        display_utils.center_print(f"Successfully moved {cat} to {new_parent_cat}.\nNew path is {new_cat}", "black on green")
        cats_dict = category_api.get_categories()
        display_utils.display_categories(cats_dict, highlight_cat=new_cat)
    elif resp.status_code == 400:
        err_msg = general_utils.bytes2dict(resp.content)['detail']
        display_utils.center_print(err_msg, constants.DISPLAY_TERMINAL_COLOR_ERROR)
    else:
        display_utils.center_print(resp.content, constants.DISPLAY_TERMINAL_COLOR_ERROR)
    

@app.command("open")
def open_girok():
    webbrowser.open("https://github.com")
    
    