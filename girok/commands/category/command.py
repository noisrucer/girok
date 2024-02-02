import typer
from rich import print
from rich.console import Console
from rich.style import Style
from rich.text import Text

import girok.api.category as category_api
from girok.constants import COLOR_PALETTE, DisplayBoxType, Emoji
from girok.utils.display import center_print

app = typer.Typer(rich_markup_mode="rich")
console = Console()


@app.command(
    "showcat",
    help="[yellow]Show[/yellow] all pre-defined categories",
    rich_help_panel=":file_folder: [bold yellow1]Category Commands[/bold yellow1]",
)
def show_categories():
    # resp = category_api.get_all_categories()
    # if not resp.is_success:
    #     center_print(resp.error_message, DisplayBoxType.ERROR)
    #     raise typer.Exit()

    circle_text = Text(
        text=Emoji.CIRCLE, style=Style(color=COLOR_PALETTE["GREYISH_YELLOW"])
    )

    normal_text = Text(text="Hello Category", style=Style(color="#D7C8B7", bold=True))

    console.print(Text.assemble(circle_text, " ", normal_text))
    # console.print(Text(
    #     text=Emoji.CIRCLE + " " + "hello"
    # ))
