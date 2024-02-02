import re
from typing_extensions import Annotated
import typer
from rich import print
from rich.console import Console
from rich.markdown import Markdown
from rich.tree import Tree
from rich.text import Text
from rich.style import Style

import girok.api.category as category_api
from girok.commands.category.util import display_categories_tree, get_next_category_color
from girok.constants import DisplayBoxType, CATEGORY_COLOR_PALETTE, Emoji, DEFAULT_CATEGORY_TEXT_COLOR, DisplayArrowType
from girok.utils.display import center_print, arrow_print

app = typer.Typer(rich_markup_mode="rich")
console = Console()


def category_callback(ctx: typer.Context, param: typer.CallbackParam, value: str):
    if value is None:
        return None

    if not re.match("^([a-zA-Z0-9]+/)*[a-zA-Z0-9]+/?$", value):
        raise typer.BadParameter(
            "[Invalid category path] Category path must be in 'xx/yy/zz format.'"
        )

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
    category_path: Annotated[str, typer.Argument(
        ...,
        help="[yellow]Category path - xx/yy/zz..[/yellow]",
        callback=category_callback,
    )],
    color: Annotated[str, typer.Option(
        "-c", "--color",
        help="[yellow]Color[/yellow] for category"
    )] = None
):
    # Resolve color
    if color:
        if color not in CATEGORY_COLOR_PALETTE:
            arrow_print("Unsupported category color\n", DisplayArrowType.ERROR)
            tree = Tree("Supported category colors")
            for color_name, hex in CATEGORY_COLOR_PALETTE.items():
                circle_text = Text(text=Emoji.CIRCLE, style=Style(color=CATEGORY_COLOR_PALETTE[color_name]))
                category_name_text = Text(
                    text=f"{color_name}",
                    style=Style(color=DEFAULT_CATEGORY_TEXT_COLOR)
                )
                item_text = Text.assemble(circle_text, " ", category_name_text)
                tree.add(item_text)
            console.print(tree)
            raise typer.Exit()
    else:
        # If color is not passed, automatically assign the color from the palette
        color = get_next_category_color()
    
    print(category_path)
    print(color)

    resp = category_api.create_category(category_path, color)
    print(resp.is_success)
    print(resp.error_message)
    
    
    
    


    



