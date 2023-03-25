from pathlib import Path
import os.path as osp

import typer
from rich import print
from rich.console import Console
from rich.table import Table

from girok.config import get_config
import girok.utils.general as general_utils
import girok.utils.auth as auth_utils
import girok.api.auth as auth_api
import girok.utils.display as display_utils

app = typer.Typer(rich_markup_mode='rich')

cfg = get_config()

@app.command("login", help="[yellow]Login[/yellow] with email and password", rich_help_panel=":lock: [bold yellow1]Authentication Commands[/bold yellow1]")
def login():
    # Check if the user holds a valid JWT (logged in)
    stored_access_token = auth_utils.get_access_token_from_json(cfg.config_path)
    if stored_access_token:
        resp = auth_api.validate_access_token(stored_access_token)
        if resp.status_code == 200:
            print("You have already logged in. Enjoy!")
            exit(0)
    
    # Log-in
    print("Please login to proceed")
    email = typer.prompt("Enter email address")
    password = typer.prompt("Enter password", hide_input=True)
    
    resp = auth_api.login(email, password)
    if resp.status_code == 200:
        access_token = general_utils.bytes2dict(resp.content)['access_token']
        general_utils.update_json(cfg.config_path, {"access_token": access_token, "email": email})
        print("You're logged in!")
    elif resp.status_code == 401:
        err_msg = general_utils.bytes2dict(resp.content)['detail']
        display_utils.center_print(err_msg, type="error")
        exit(0)
    else:
        print("Login failed. Please try again with [green]girok login[/green]")
        exit(0)
    exit(0)
    

@app.command("logout", help="[red]Logout[/red] from the currently logged-in account", rich_help_panel=":lock: [bold yellow1]Authentication Commands[/bold yellow1]")
def logout():
    access_token = auth_utils.get_access_token_from_json(cfg.config_path)
    if not auth_utils.is_logged_in(access_token):
        print("You're not logged in.")
        exit(0)
    
    auth_utils.remove_access_token(cfg.config_path)
    print("Successfully logged out")
    exit(0)
    
    
@app.command("register", help="[green]Register[/green] a new account", rich_help_panel=":lock: [bold yellow1]Authentication Commands[/bold yellow1]")
def register():
    access_token = auth_utils.get_access_token_from_json(cfg.config_path)
    if access_token and auth_utils.is_logged_in(access_token):
        print("You're logged in. Please try after log out.")
        exit(0)
        
    print(":star: This is your first time to use [yellow]girok[/yellow]! :star:\n")
    is_register = typer.confirm("Do you want to register a new account?")
    if is_register:
        email = typer.prompt("Enter email address")
        password = typer.prompt("Enter password", hide_input=True)
        confirm_password = typer.prompt("Confirm password", hide_input=True)
        auth_utils.match_passwords(password, confirm_password)
        
        # register a new account
        register_resp = auth_api.register(email, password)
        if register_resp.status_code == 201:
            verification_code = typer.prompt("Enter the verification code sent to your email")
            if auth_api.verify_verification_code(email, verification_code): 
                pass
            else:
                exit(0)
        elif register_resp.status_code == 400:
            err_msg = general_utils.bytes2dict(register_resp.content)['detail']
            display_utils.center_print(err_msg, type="error")
            exit(0)
        else:
            err_msg = general_utils.bytes2dict(register_resp.content)['detail']
            display_utils.center_print(str(err_msg), type="error")
        print("Registration successful! Please login by [green]girok login[/green] command")
        exit(0)
    else:
        exit(0)

if __name__ == '__main__':
    app()