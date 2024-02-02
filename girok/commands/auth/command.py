import shutil
import time

import typer
from rich import print
from rich.console import Console
from rich.live import Live
from rich.progress import Progress
from rich.style import Style
from rich.text import Text

import girok.api.auth as auth_api
from girok.auth_handler import AuthHandler
from girok.constants import DisplayBoxType
from girok.utils.display import center_print

app = typer.Typer(rich_markup_mode="rich")
console = Console()


@app.command(
    "register",
    help="[green]Register[/green] a new account",
    rich_help_panel=":lock: [bold yellow1]Authentication Commands[/bold yellow1]",
)
def register():
    print(":star: [yellow]Welcome to girok![/yellow] :star:\n")

    is_register = typer.confirm("> Do you want to register a new account?")
    if not is_register:
        raise typer.Exit()

    # Send email verification code
    email = typer.prompt("\n> Enter email address")
    resp = auth_api.send_verification_code(email=email)
    if not resp.is_success:
        center_print(text=resp.error_message, text_type=DisplayBoxType.ERROR)
        raise typer.Exit()

    # Verify email verification code
    print("\n[yellow]Check your inbox to verify your email address.[/yellow]")
    print(
        "[yellow]If you don't find it in your inbox, please check[/yellow] [red]spam/junk[/red] [yellow]inbox[/yellow]."
    )
    retry_count = 3
    while retry_count > 0:
        verification_code = typer.prompt(
            f"> Enter verification code [{retry_count} tries left]"
        )
        retry_count -= 1
        resp = auth_api.verify_verification_code(
            email=email, verification_code=verification_code
        )

        if resp.is_success:
            break
        else:
            if retry_count == 0:
                center_print(
                    text="Verification code is not valid. Please register again.",
                    text_type=DisplayBoxType.ERROR,
                )
                raise typer.Exit()

    # Register
    print("\n[yellow]Password must be at least 7 characters long[/yellow]")
    print(
        "[yellow]Password must contain at least one lowercase letter, one uppercase letter, and one special character (@, #, $, %, *, !)[/yellow]"
    )
    password = typer.prompt("> Enter password", hide_input=True)
    confirm_password = typer.prompt("> Confirm password", hide_input=True)
    if password != confirm_password:
        center_print(
            text="Password does not match. Please register again.",
            text_type=DisplayBoxType.ERROR,
        )
        raise typer.Exit()

    resp = auth_api.register(
        email=email, verification_code=verification_code, password=password
    )
    if not resp.is_success:
        center_print(resp.error_message, DisplayBoxType.ERROR)
        raise typer.Exit()

    # Registration successful
    register_welcome()


@app.command(
    "login",
    help="[yellow]Login[/yellow] with email and password",
    rich_help_panel=":lock: [bold yellow1]Authentication Commands[/bold yellow1]",
)
def login():
    email = typer.prompt("> Enter email address")
    password = typer.prompt("> Enter password", hide_input=True)

    resp = auth_api.login(email, password)
    if not resp.is_success:
        center_print(resp.error_message, DisplayBoxType.ERROR)
        raise typer.Exit()

    access_token = resp.body["accessToken"]
    AuthHandler.login(access_token)
    print("[yellow]Successfully logged in.[/yellow]")


@app.command(
    "logout",
    help="[red]Logout[/red] from the currently logged-in account",
    rich_help_panel=":lock: [bold yellow1]Authentication Commands[/bold yellow1]",
)
def logout():
    AuthHandler.logout()
    print("[yellow]Successfully logged out.[/yellow]")


def register_welcome():
    print()
    with Progress() as progress:
        task = progress.add_task("[green]Registering...", total=100)

        while not progress.finished:
            progress.update(task, advance=1)
            time.sleep(0.02)

    welcome_msg = """[yellow] __      __          ___                                        
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
    l1 = " __      __          ___                                        "
    l2 = "/\ \  __/\ \        /\_ \                                       "
    l3 = "\ \ \/\ \ \ \     __\//\ \     ___    ___     ___ ___      __   "
    l4 = " \ \ \ \ \ \ \  /'__`\\\ \ \   /'___\ / __`\ /' __` __`\  /'__`\ "
    l5 = "  \ \ \_/ \_\ \/\  __/ \_\ \_/\ \__//\ \L\ \/\ \/\ \/\ \/\  __/ "
    l6 = "   \ `\___x___/\ \____\/\____\ \____\ \____/\ \_\ \_\ \_\ \____\\"
    l7 = "    '\/__//__/  \/____/\/____/\/____/\/___/  \/_/\/_/\/_/\/____/"

    r1 = "         __               ____                     __          __     "
    r2 = "        /\ \__           /\  _`\   __             /\ \        /\ \    "
    r3 = "        \ \ ,_\   ___    \ \ \L\_\/\_\  _ __   ___\ \ \/'\    \ \ \   "
    r4 = "         \ \ \/  / __`\   \ \ \L_L\/\ \/\`'__\/ __`\ \ , <     \ \ \  "
    r5 = "          \ \ \_/\ \L\ \   \ \ \/, \ \ \ \ \//\ \L\ \ \ \\\\\`\   \ \_\ "
    r6 = "           \ \__\ \____/    \ \____/\ \_\ \_\\\ \____/\ \_\ \_\   \/\_\\"
    r7 = "            \/__/\/___/      \/___/  \/_/\/_/ \/___/  \/_/\/_/    \/_/"

    #     console.print(Align.center("""[yellow] __      __          ___
    # /\ \  __/\ \        /\_ \
    # \ \ \/\ \ \ \     __\//\ \     ___    ___     ___ ___      __
    #  \ \ \ \ \ \ \  /'__`\\\ \ \   /'___\ / __`\ /' __` __`\  /'__`\
    #   \ \ \_/ \_\ \/\  __/ \_\ \_/\ \__//\ \L\ \/\ \/\ \/\ \/\  __/
    #    \ `\___x___/\ \____\/\____\ \____\ \____/\ \_\ \_\ \_\ \____\\
    #     '\/__//__/  \/____/\/____/\/____/\/___/  \/_/\/_/\/_/\/____/

    #          __               ____                     __          __
    #         /\ \__           /\  _`\   __             /\ \        /\ \
    #         \ \ ,_\   ___    \ \ \L\_\/\_\  _ __   ___\ \ \/'\    \ \ \
    #          \ \ \/  / __`\   \ \ \L_L\/\ \/\`'__\/ __`\ \ , <     \ \ \
    #           \ \ \_/\ \L\ \   \ \ \/, \ \ \ \ \//\ \L\ \ \ \\\\\`\   \ \_\
    #            \ \__\ \____/    \ \____/\ \_\ \_\\\ \____/\ \_\ \_\   \/\_\\
    #             \/__/\/___/      \/___/  \/_/\/_/ \/___/  \/_/\/_/    \/_/

    #                                                               [/yellow]"""))

    print("\n" * 5)
    screen_width = shutil.get_terminal_size().columns // 2
    with Live("", refresh_per_second=4) as live:
        num_iters = (70 * screen_width) // 109
        for _ in range(num_iters):
            space = _
            msg = (
                " " * space
                + l1
                + "\n"
                + " " * space
                + l2
                + "\n"
                + " " * space
                + l3
                + "\n"
                + " " * space
                + l4
                + "\n"
                + " " * space
                + l5
                + "\n"
                + " " * space
                + l6
                + "\n"
                + " " * space
                + l7
                + "\n"
            )
            live.update(Text(msg, style=Style(color="yellow")))
            time.sleep(0.009)
        print("\n")

    with Live("", refresh_per_second=4) as live:
        for _ in range(num_iters):
            space = _
            msg = (
                " " * space
                + r1
                + "\n"
                + " " * space
                + r2
                + "\n"
                + " " * space
                + r3
                + "\n"
                + " " * space
                + r4
                + "\n"
                + " " * space
                + r5
                + "\n"
                + " " * space
                + r6
                + "\n"
                + " " * space
                + r7
                + "\n"
            )
            live.update(Text(msg, style=Style(color="yellow")))
            time.sleep(0.009)

    print("\n" * 1)
    console.print(
        " " * ((70 * screen_width) // 109 + 20)
        + "Enter [green]girok login[/green] to log-in to your account."
    )
    print("\n" * 10)
