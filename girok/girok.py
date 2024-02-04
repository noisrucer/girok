import os

import typer
from rich import print

import girok.commands.auth.command as auth_command
import girok.commands.category.command as category_command
import girok.commands.task.command as task_command
from girok.config.auth_handler import AuthHandler
from girok.constants import VERSION, CommandName

app = typer.Typer(
    rich_markup_mode="rich",
    help="Enter [red]girok <command name> --help[/red] to see more detailed documentations of commands!",
)

app.registered_commands.extend(auth_command.app.registered_commands)
app.registered_commands.extend(category_command.app.registered_commands)
app.registered_commands.extend(task_command.app.registered_commands)


@app.command("version")
def version():
    print(VERSION)


@app.callback()
def pre_command_callback(ctx: typer.Context):
    # Get the executed command name
    cmd = ctx.invoked_subcommand

    # Set up application directory and config.json
    AuthHandler.init()

    # Utility commands
    if cmd in [CommandName.VERSION, CommandName.COLORS]:
        return

    """
    Login, Register -> login 되면 X
    나머지 -> login 필수
    """
    is_logged_in = AuthHandler.is_logged_in()

    # Logout required commands
    if cmd in [CommandName.REGISTER, CommandName.LOGIN]:
        if is_logged_in:
            print("[red]You're already logged in. Please log out and try again.[/red]")
            raise typer.Exit()
    # Login required commands
    else:
        if not is_logged_in:
            print("[red]You're not logged in. Please login with [/red][yellow]girok login[/yellow].")
            raise typer.Exit()


if __name__ == "__main__":
    app()
