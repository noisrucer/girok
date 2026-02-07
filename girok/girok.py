import os

import typer
from rich import print

import girok.commands.category.command as category_command
import girok.commands.task.command as task_command
import girok.commands.calendar.command as calendar_command
from girok.config.auth_handler import AuthHandler
from girok.constants import VERSION

app = typer.Typer(
    rich_markup_mode="rich",
    help="Enter [red]girok <command name> --help[/red] to see more detailed documentations of commands!",
)

app.registered_commands.extend(category_command.app.registered_commands)
app.registered_commands.extend(task_command.app.registered_commands)
app.registered_commands.extend(calendar_command.app.registered_commands)


@app.command("version")
def version():
    print(VERSION)


@app.callback()
def pre_command_callback(ctx: typer.Context):
    # Set up application directory, config.json, and default user
    AuthHandler.init()


if __name__ == "__main__":
    app()
