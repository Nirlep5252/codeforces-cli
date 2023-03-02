import click
import json
import os
from rich.console import Console
from utils import CFClient

console = Console()


@click.command()
@click.option("--username", prompt="Enter your codeforces username")
@click.password_option()
@click.option("--cf_dir", prompt="Enter your codeforces directory")
def config(username: str, password: str, cf_dir: str):
    """
    Configure the codeforces cli.
    """

    client = CFClient(username, password)
    if not client.login():
        console.print("[bold red]ERROR: [/]Invalid username or password.")
        return

    if cf_dir.startswith("~"):
        cf_dir = os.path.expanduser('~') + cf_dir[1:]
    if not os.path.isdir(cf_dir):
        console.print(f"[bold red]ERROR: [/] Directory `{cf_dir}` not found.")
        return

    cf_dir = os.path.abspath(cf_dir)
    data = {
        "dir": cf_dir,
        "username": username,
        "password": password
    }

    slash = "/" if os.name == "posix" else "\\\\"
    with open(os.path.expanduser('~') + slash + "codeforces.uwu", "w") as f:
        f.write(json.dumps(data))

    console.print("\n[bold green]Config set![/]\n" + f"dir: {cf_dir}")
    console.print(f"\nHappy Coding! {username}")
