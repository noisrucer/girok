import typer

app = typer.Typer(rich_markup_mode='rich')

@app.command("version", help="Show version", rich_help_panel=":tear-off_calendar: [bold yellow1]Info Commands[/bold yellow1]")
def show_calendar():
    print("hello")

