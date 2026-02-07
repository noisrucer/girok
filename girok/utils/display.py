import shutil

from rich import print
from rich.align import Align
from rich.console import Console
from rich.style import Style
from rich.text import Text

from girok.constants import DisplayArrowType, DisplayBoxType

console = Console()


def center_print(text: str, text_type: DisplayBoxType, wrap: bool = False) -> None:
    style = Style(color=text_type.text_color_hex, bgcolor=text_type.bg_color_hex)

    width = shutil.get_terminal_size().columns // 2 if wrap else shutil.get_terminal_size().columns

    content = Text(text, style=style)
    console.print(Align.center(content, style=style, width=width), height=50)


def arrow_print(text: str, text_type: DisplayArrowType) -> None:
    print(f"[{text_type.value}]> {text}[/{text_type.value}]")


GIROK_LOGO = r"""[yellow] __      __          ___                                        
/\ \  __/\ \        /\_ \                                       
\ \ \/\ \ \ \     __\//\ \     ___    ___     ___ ___      __   
 \ \ \ \ \ \ \  /'__`\\\ \ \   /'___\ / __`\ /' __` __`\  /'__`\ 
  \ \ \_/ \_\ \/\  __/ \_\ \_/\ \__//\ \L\ \/\ \/\ \/\ \/\  __/ 
   \ `\___x___/\ \____\/\____\ \____\ \____/\ \_\ \_\ \_\ \____\\
    '\/__//__/  \/____/\/____/\/____/\/___/  \/_/\/_/\/_/\/____/
                                                                
                                                                
         __               ____                     __          __     
        /\ \__           /\  _`\   __             /\ \        /\ \    
        \ \ ,_\   ___    \ \ \L\_\/\_\  _ __   ___\ \ \/'\    \ \ \   
         \ \ \/  / __`\   \ \ \L_L\/\ \/\`'__\/ __`\ \ , <     \ \ \  
          \ \ \_/\ \L\ \   \ \ \/, \ \ \ \ \//\ \L\ \ \ \\\\\`\   \ \_\ 
           \ \__\ \____/    \ \____/\ \_\ \_\\\ \____/\ \_\ \_\   \/\_\\
            \/__/\/___/      \/___/  \/_/\/_/ \/___/  \/_/\/_/    \/_/
                                                              
                                                              [/yellow]"""

def print_logo():
    """Print the Girok logo."""
    console.print(GIROK_LOGO)
