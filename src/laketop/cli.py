import os
import typer

app = typer.Typer(
    name="laketop",
    help="LakeTop - Visual CLI profiler for Delta Lake tables",
    no_args_is_help=True
)

@app.command()
def scan(
    table_path: str = typer.Argument(
        ...,
        help="Local file path to the Delta table directory to profile"
    )
):
    """
    Profiles a local Delta table and displays storage metrics, file fragmentation analysis,
    and the commit ledger in a visual terminal dashboard.
    """
    # Normalize path
    table_path = os.path.abspath(os.path.expanduser(table_path))
    
    # Path validation
    if not os.path.exists(table_path):
        typer.secho(f"Error: Path '{table_path}' does not exist.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
        
    if not os.path.isdir(table_path):
        typer.secho(f"Error: Path '{table_path}' is a file, but must be a directory.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
        
    delta_log_path = os.path.join(table_path, "_delta_log")
    if not os.path.exists(delta_log_path) or not os.path.isdir(delta_log_path):
        typer.secho(
            f"Error: Path '{table_path}' is not a valid Delta table (missing '_delta_log' directory).",
            fg=typer.colors.RED,
            err=True
        )
        raise typer.Exit(code=1)

    try:
        from laketop.ui import LakeTopApp
        tui_app = LakeTopApp(table_path=table_path)
        tui_app.run()
    except Exception as e:
        typer.secho(f"Error launching interface: {str(e)}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
