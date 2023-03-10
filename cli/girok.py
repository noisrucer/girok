from pathlib import Path
import os
import os.path as osp

import typer
from rich import print
from rich.console import Console
from rich.table import Table

from config import get_config
import api.auth as auth_api
import commands.auth as auth_command
import commands.category as category_command
import commands.task as task_command
import commands.calendar as calendar_command
import utils.general as general_utils
import utils.auth as auth_utils

app = typer.Typer(rich_markup_mode='rich')
app.registered_commands.extend(auth_command.app.registered_commands)
app.registered_commands.extend(category_command.app.registered_commands)
app.registered_commands.extend(task_command.app.registered_commands)
app.registered_commands.extend(calendar_command.app.registered_commands)
cfg = get_config()
    
@app.command()
def test():
    print("test")


@app.callback()
def pre_command_callback(ctx: typer.Context):
    # Setting up app dir and config file if they don't exist
    general_utils.config_setup(cfg.app_dir, cfg.config_path)
    if ctx.invoked_subcommand in ['login', 'logout', 'register']:
        return
        
    # Check if JWT is stored in config file
    stored_access_token = auth_utils.get_access_token_from_json(cfg.config_path)
    if stored_access_token:
        resp = auth_api.validate_access_token(stored_access_token)
        if resp.status_code != 200: # invalid(or expired) JWT -> login again
            print("You're not logged in. Please login with [green]girok login[/green].")
            exit(0)
    else:
        print("You're not logged in. Please login with [green]girok login[/green].")
        exit(0)
        
app()