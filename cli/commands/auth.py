from pathlib import Path
import os.path as osp

import typer
from rich import print
from rich.console import Console
from rich.table import Table

from config import get_config
import utils.general as general_utils
import utils.auth as auth_utils
import api.auth as auth_api

app = typer.Typer(rich_markup_mode='rich')

cfg = get_config()

@app.command("login")
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
        
    else:
        print("Login failed. Please try again with [green]girok login[/green]")
        exit(0)
    exit(0)
    

@app.command("logout")
def logout():
    access_token = auth_utils.get_access_token_from_json(cfg.config_path)
    if not auth_utils.is_logged_in(access_token):
        print("You're not logged in.")
        exit(0)
    
    auth_utils.remove_access_token(cfg.config_path)
    print("Successfully logged out")
    exit(0)
    
    
    
@app.command("register")
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
            print("Register complete!")
        else:
            register_resp_content = general_utils.bytes2dict(register_resp.content)
            if register_resp.status_code == 400:
                print(register_resp_content['detail'])
            exit(0)
        
        print("Registration successful! Please login by [green]girok login[/green] command")
        exit(0)
    else:
        exit(0)

if __name__ == '__main__':
    app()