import typer
import uvicorn
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def server(
    host: str = "localhost",
    port: int = 8765,
    reload: bool = False
):
    """Start the LangGraph Scrum Server."""
    console.print(f"[green]Starting LangGraph Scrum Server on ws://{host}:{port}[/green]")
    uvicorn.run(
        "langgraph_scrum.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

@app.command()
def version():
    """Show version."""
    from langgraph_scrum import __version__
    print(f"LangGraph Scrum Team v{__version__}")

def main():
    app()

if __name__ == "__main__":
    main()
