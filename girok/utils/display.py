import shutil

from rich import print
from rich.align import Align
from rich.console import Console
from rich.style import Style
from rich.text import Text

from girok.constants import DisplayBoxType, DisplayArrowType

console = Console()


def center_print(text: str, text_type: DisplayBoxType, wrap: bool = False) -> None:
    style = Style(color=text_type.text_color_hex, bgcolor=text_type.bg_color_hex)

    width = shutil.get_terminal_size().columns // 2 if wrap else shutil.get_terminal_size().columns

    content = Text(text, style=style)
    console.print(Align.center(content, style=style, width=width), height=50)


def arrow_print(text: str, text_type: DisplayArrowType) -> None:
    print(f"[{text_type.value}]> {text}[/{text_type.value}]")