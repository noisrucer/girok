import re

import typer
from rich import print
from rich.console import Console
from rich.markdown import Markdown
from rich.style import Style
from rich.text import Text
from rich.tree import Tree
from typing_extensions import Annotated

import girok.api.category as category_api
from girok.commands.category.util import (
    display_categories_tree,
    display_category_color_palette,
    get_next_category_color,
)
from girok.constants import (
    CATEGORY_COLOR_PALETTE,
    DEFAULT_CATEGORY_TEXT_COLOR,
    DisplayArrowType,
    DisplayBoxType,
    Emoji,
)
from girok.utils.display import arrow_print, center_print

app = typer.Typer(rich_markup_mode="rich")
console = Console()


def category_callback(ctx: typer.Context, param: typer.CallbackParam, value: str):
    if value is None:
        return None

    if ctx.command.name == "mvcat" and param.name == "new_parent_path" and value == "/":
        return value.rstrip("/")

    if not re.match("^([a-zA-Z0-9]+/)*[a-zA-Z0-9]+/?$", value):
        raise typer.BadParameter("[Invalid category path] Category path must be in 'xx/yy/zz format.'")

    if value.endswith("/"):
        value = value[:-1]

    if value == "none":
        raise typer.BadParameter("Sorry, 'none' is a reserved category name.")
    return value


@app.command(
    "showcat",
    help="[yellow]Show[/yellow] all pre-defined categories",
    rich_help_panel=":file_folder: [bold yellow1]Category Commands[/bold yellow1]",
)
def show_categories():
    resp = category_api.get_all_categories()
    if not resp.is_success:
        center_print(resp.error_message, DisplayBoxType.ERROR)
        raise typer.Exit()

    center_print("Event Categories", DisplayBoxType.TITLE)
    root_categories: list[dict] = resp.body["rootCategories"]
    display_categories_tree(root_categories)


@app.command(
    "addcat",
    help="[yellow]Add[/yellow] a new category",
    rich_help_panel=":file_folder: [bold yellow1]Category Commands[/bold yellow1]",
)
def add_category(
    category_path: Annotated[
        str,
        typer.Argument(
            ...,
            help="[yellow]Category path - xx/yy/zz..[/yellow]",
            callback=category_callback,
        ),
    ],
    color: Annotated[str, typer.Option("-c", "--color", help="[yellow]Color[/yellow] for category")] = None,
):
    # Resolve color
    if color:
        if len(category_path.split("/")) != 1:
            arrow_print("You cannot specify non top-level category color", DisplayArrowType.ERROR)
            raise typer.Exit()

        if color not in CATEGORY_COLOR_PALETTE:
            arrow_print("Unsupported category color\n", DisplayArrowType.ERROR)
            display_category_color_palette()
            raise typer.Exit()
    else:
        # If color is not passed and top-level category, automatically assign the color from the palette
        if len(category_path.split("/")) == 1:
            color = get_next_category_color()

    # Create a new category
    resp = category_api.create_category(category_path, color)
    if not resp.is_success:
        center_print(resp.error_message, DisplayBoxType.ERROR)
        raise typer.Exit()

    resp = category_api.get_all_categories()
    if not resp.is_success:
        center_print(resp.error_message, DisplayBoxType.ERROR)
        raise typer.Exit()

    center_print("Event Categories", DisplayBoxType.TITLE)
    root_categories: list[dict] = resp.body["rootCategories"]
    display_categories_tree(root_categories, category_path)


@app.command(
    "rmcat",
    help="[red]Remove[/red] a category",
    rich_help_panel=":file_folder: [bold yellow1]Category Commands[/bold yellow1]",
)
def remove_category(
    category_path: Annotated[
        str,
        typer.Argument(
            ...,
            help="[yellow]Category path - xx/yy/zz..[/yellow]",
            callback=category_callback,
        ),
    ],
    force_yes: Annotated[bool, typer.Option("-y", "--yes", help="[yellow]Ignore confirm message[/yellow]")] = False,
):
    if not force_yes:
        confirm_rm = typer.confirm(
            f"[WARNING] Are you sure to delete '{category_path}'?\nAll the subcategories and tasks will also be deleted."
        )
        if not confirm_rm:
            raise typer.Exit()

    resp = category_api.remove_category(category_path)
    if not resp.is_success:
        center_print(resp.error_message, DisplayBoxType.ERROR)
        raise typer.Exit()

    resp = category_api.get_all_categories()
    if not resp.is_success:
        center_print(resp.error_message, DisplayBoxType.ERROR)
        raise typer.Exit()

    center_print("Event Categories", DisplayBoxType.TITLE)
    root_categories: list[dict] = resp.body["rootCategories"]
    display_categories_tree(root_categories, category_path)


@app.command(
    "upcat",
    help="[green]Rename[/green] a category",
    rich_help_panel=":file_folder: [bold yellow1]Category Commands[/bold yellow1]",
)
def rename_category(
    category_path: Annotated[
        str,
        typer.Argument(
            help="[yellow]Category path - xx/yy/zz..[/yellow]",
            callback=category_callback,
        ),
    ],
    new_name: Annotated[str, typer.Option("-n", "--name", help="[yellow]New category name[/yellow]")] = None,
    new_color: Annotated[str, typer.Option("-c", "--color", help="[yellow]New category color[/yellow]")] = None,
):
    if new_name is None and new_color is None:
        arrow_print("Please provide fields to update", DisplayArrowType.ERROR)
        raise typer.Exit()

    # Resolve color
    if new_color:
        if len(category_path.split("/")) != 1:
            arrow_print("You cannot update non top-level category color", DisplayArrowType.ERROR)
            raise typer.Exit()

        if new_color not in CATEGORY_COLOR_PALETTE:
            arrow_print("Unsupported category color\n", DisplayArrowType.ERROR)
            display_category_color_palette()
            raise typer.Exit()

    resp = category_api.update_category(category_path, new_name, new_color)
    if not resp.is_success:
        center_print(resp.error_message, DisplayBoxType.ERROR)
        raise typer.Exit()

    resp = category_api.get_all_categories()
    if not resp.is_success:
        center_print(resp.error_message, DisplayBoxType.ERROR)
        raise typer.Exit()

    center_print("Event Categories", DisplayBoxType.TITLE)
    root_categories: list[dict] = resp.body["rootCategories"]
    name = new_name if new_name else category_path.split("/")[-1]
    new_path = "/".join(category_path.split("/")[:-1] + [name])
    display_categories_tree(root_categories, new_path)


@app.command(
    "mvcat",
    help="[yellow]Move[/yellow] a category to under category",
    rich_help_panel=":file_folder: [bold yellow1]Category Commands[/bold yellow1]",
)
def move_category(
    path: Annotated[
        str,
        typer.Argument(
            help="[yellow]Category path - xx/yy/zz..[/yellow]",
            callback=category_callback,
        ),
    ],
    new_parent_path: Annotated[
        str,
        typer.Argument(
            help="[yellow]Category path - xx/yy/zz..[/yellow]",
            callback=category_callback,
        ),
    ],
):
    resp = category_api.move_category(path, new_parent_path)
    if not resp.is_success:
        center_print(resp.error_message, DisplayBoxType.ERROR)
        raise typer.Exit()

    resp = category_api.get_all_categories()
    if not resp.is_success:
        center_print(resp.error_message, DisplayBoxType.ERROR)
        raise typer.Exit()

    center_print("Event Categories", DisplayBoxType.TITLE)
    root_categories: list[dict] = resp.body["rootCategories"]
    new_path = "/".join(new_parent_path.split("/") + [path.split("/")[-1]])
    display_categories_tree(root_categories, new_path)


@app.command(
    "colors",
    help="[yellow]Show[/yellow] category color palette",
    rich_help_panel=":file_folder: [bold yellow1]Category Commands[/bold yellow1]",
)
def show_category_color_palette():
    display_category_color_palette()
