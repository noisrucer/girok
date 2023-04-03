import re

import typer
from rich import print
from rich.console import Console
from rich.table import Table
from rich.align import Align
from rich.padding import Padding
from rich.panel import Panel

import girok.constants as constants
from girok.config import get_config
import girok.api.category as category_api
import girok.utils.general as general_utils
import girok.utils.display as display_utils
import girok.utils.auth as auth_utils
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


@app.command("showcat", help="[yellow]Show[/yellow] all pre-defined categories", rich_help_panel=":file_folder: [bold yellow1]Category Commands[/bold yellow1]")
def show_categories():
    cats_dict = category_api.get_categories()
    text = "Task Categories"
    display_utils.center_print(text, type='title')
    display_utils.display_categories(cats_dict)
    

@app.command("addcat", help="[yellow]Add[/yellow] a new category", rich_help_panel=":file_folder: [bold yellow1]Category Commands[/bold yellow1]")
def add_category(
    cat: str = typer.Argument(..., help="[yellow]Category path - xx/yy/zz..[/yellow]", callback=category_callback),
    color: str = typer.Option(None, "-c", "--color", help="[yellow]Color[/yellow] for category")
):
    category_api.add_category(cat, color)
    
    
@app.command("rmcat", help="[red]Remove[/red] a category", rich_help_panel=":file_folder: [bold yellow1]Category Commands[/bold yellow1]")
def remove_category(cat: str = typer.Argument(..., help="[yellow]Category path - xx/yy/zz..[/yellow]")):
    confirm_rm = typer.confirm(f"[WARNING] Are you sure to delete '{cat}'?\nAll the subcategories and tasks will also be deleted.")
    if not confirm_rm:
        exit(0)
    category_api.remove_category(cat)
    
        
        
@app.command("rncat", help="[green]Rename[/green] a category", rich_help_panel=":file_folder: [bold yellow1]Category Commands[/bold yellow1]")
def rename_category(
    cat: str = typer.Argument(..., help="[yellow]Category path - xx/yy/zz..[/yellow]"),
    new_name: str = typer.Argument(..., help="[yellow]New category name[/yellow]")
):
    category_api.rename_category(cat, new_name)
        
        
@app.command("mvcat", help="[yellow]Move[/yellow] a category to under category", rich_help_panel=":file_folder: [bold yellow1]Category Commands[/bold yellow1]")
def move_category(
    cat: str = typer.Argument(..., help="[yellow]Category path - xx/yy/zz..[/yellow]"),
    new_parent_cat: str = typer.Argument(..., help="[yellow]New supercategory path - xx/yy/[/yellow]")
):
    if new_parent_cat.endswith('/'):
        new_parent_cat = new_parent_cat[:-1]
    category_api.move_category(cat, new_parent_cat)