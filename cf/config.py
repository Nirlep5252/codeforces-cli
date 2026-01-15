import click
import json
import os
from rich.console import Console
from utils import CFClient

console = Console()


@click.command()
@click.option("--username", prompt="Enter your codeforces username")
@click.option("--cf_dir", prompt="Enter your codeforces directory")
def config(username: str, cf_dir: str):
    """
    Configure the codeforces cli.
    """

    client = CFClient(username)
    if not client.login():
        console.print("[bold red]ERROR: [/]Login failed.")
        return

    if cf_dir.startswith("~"):
        cf_dir = os.path.expanduser('~') + cf_dir[1:]
    if not os.path.isdir(cf_dir):
        os.makedirs(cf_dir, exist_ok=True)
        console.print(f"[dim]Created directory: {cf_dir}[/]")

    cf_dir = os.path.abspath(cf_dir)
    data = {
        "dir": cf_dir,
        "username": username,
    }

    slash = "/" if os.name == "posix" else "\\\\"
    with open(os.path.expanduser('~') + slash + "codeforces.uwu", "w") as f:
        f.write(json.dumps(data))

    console.print("\n[bold green]Config set![/]\n" + f"dir: {cf_dir}")
    console.print(f"\nHappy Coding! {username}")
