import typer
import girok.calendar_cli.calendar_main as calendar_main

app = typer.Typer(rich_markup_mode='rich')

@app.command("cal", help="[green]Open Calendar GUI[/green]", rich_help_panel=":tear-off_calendar: [bold yellow1]Calendar Commands[/bold yellow1]")
def show_calendar():
    app = calendar_main.Entry()
    app.run()

