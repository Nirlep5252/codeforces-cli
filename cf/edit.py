import click
import os
import subprocess
from rich.console import Console
from utils import get_config

console = Console()

editor_cmds = {
    "vscode": "code {path}",
    "neovim": "nvim {path}",
    "vim": "vim {path}",
}


@click.command(name="edit")
@click.argument("contest_id", required=True)
@click.option("--editor", type=click.Choice(["vscode", "neovim", "vim"]), prompt="Select an editor: ")
def edit_cmd(contest_id: str, editor: str):
    conf = get_config(console)
    if conf is None:
        return

    cf_dir = conf.get("dir")
    if cf_dir is None:
        console.print("[bold red]ERROR: [/]The default directory is not set.\nPlease run the `cf config` command.")
        return

    if not os.path.isdir(cf_dir):
        console.print("[bold red]ERROR: [/]The default directory does not exist.\nPlease run the `cf config` command.")
        return

    contest_dir = os.path.join(cf_dir, contest_id)
    if not os.path.isdir(contest_dir):
        console.print(f"\n[bold red]ERROR: [/]The contest directory `{contest_dir}` does not exist.")
        console.print(f"[bold green]TIP: [/]Use `cf parse {contest_id}` to create the directory and parse the contest.")
        return

    subprocess.run(editor_cmds[editor].format(path=os.path.join(cf_dir, contest_id)), shell=True)
