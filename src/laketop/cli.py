import os
import re
import typer
from typing import List, Optional

app = typer.Typer(
    name="laketop",
    help="LakeTop - Visual CLI profiler for Delta Lake tables",
    no_args_is_help=True
)

@app.callback()
def main():
    """
    LakeTop - Visual CLI profiler for Delta Lake tables.
    """
    pass

@app.command()
def scan(
    table_path: str = typer.Argument(
        ...,
        help="Local file path or cloud URI (s3://, gs://, abfss://) to the Delta table"
    ),
    storage_option: Optional[List[str]] = typer.Option(
        None,
        "--storage-option",
        "-s",
        help="Storage option credentials/config in KEY=VALUE format (can be repeated)"
    )
):
    """
    Profiles a Delta table and displays storage metrics, file fragmentation analysis,
    schema structure, and the commit ledger in a visual terminal dashboard.
    """
    # Parse storage options
    options_dict = {}
    if storage_option:
        for opt in storage_option:
            if "=" in opt:
                k, v = opt.split("=", 1)
                options_dict[k.strip()] = v.strip()
            else:
                typer.secho(
                    f"Warning: Ignoring invalid storage option format '{opt}'. Must be KEY=VALUE.",
                    fg=typer.colors.YELLOW,
                    err=True
                )

    # Check for cloud URI
    is_cloud = bool(re.match(r'^(s3|gs|abfss|adl|s3a)://', table_path, re.IGNORECASE))
    
    if not is_cloud:
        # Normalize path for local tables
        table_path = os.path.abspath(os.path.expanduser(table_path))
        
        # Local validation
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
        tui_app = LakeTopApp(table_path=table_path, storage_options=options_dict)
        tui_app.run()
    except Exception as e:
        typer.secho(f"Error launching interface: {str(e)}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
