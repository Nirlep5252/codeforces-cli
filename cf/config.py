import click
import json
import os
from rich.console import Console

console = Console()


@click.command()
# @click.option("--username", prompt="Enter your codeforces username")
# @click.password_option()
@click.option("--cf_dir", prompt="Enter your codeforces directory")
# def config(username: str, password: str, dir: str):
def config(cf_dir: str):
    if cf_dir.startswith("~"):
        cf_dir = os.path.expanduser('~') + cf_dir[1:]
    if not os.path.isdir(cf_dir):
        console.print(f"[bold red]ERROR: [/] Directory `{cf_dir}` not found.")
        return

    cf_dir = os.path.abspath(cf_dir)
    data = {
        "dir": cf_dir
    }

    slash = "/" if os.name == "posix" else "\\\\"
    with open(os.path.expanduser('~') + slash + "codeforces.uwu", "w") as f:
        f.write(json.dumps(data))

    console.print("[bold green]Config set![/]\n" + f"dir: {cf_dir}")
