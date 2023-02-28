import click
import json
import os
from rich.console import Console

console = Console()


@click.command()
# @click.option("--username", prompt="Enter your codeforces username")
# @click.password_option()
@click.option("--dir", prompt="Enter your codeforces directory")
# def config(username: str, password: str, dir: str):
def config(dir: str):
    if dir.startswith("~"):
        dir = os.path.expanduser('~') + dir[1:]
    if not os.path.isdir(dir):
        console.print(f"[bold red]ERROR: [/] Directory `{dir}` not found.")
        return

    data = {
        "dir": dir
    }

    slash = "/" if os.name == "posix" else "\\\\"
    with open(os.path.expanduser('~') + slash + "codeforces.uwu", "w") as f:
        f.write(json.dumps(data))

    console.print("[bold green]Config set![/]\n" + f"dir: {dir}")
