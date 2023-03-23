import typer
import girok.calendar_cli.calendar_main as calendar_main

app = typer.Typer(rich_markup_mode='rich')

@app.command("cal")
def show_calendar():
    app = calendar_main.Entry()
    app.run()

