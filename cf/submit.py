import click
import os
from utils import get_config, CFClient
from rich.console import Console

console = Console()


lang_ids = {
    "py": "70",
    "c": "43",
    "cpp": "73"
}


@click.command()
@click.argument("file", required=True)
def submit(file: str):
    """
    Submits your solution
    """
    slash = "/" if os.name == "posix" else "\\"

    data = get_config(console)
    if data is None:
        return

    cf_dir = data.get("dir")
    if cf_dir is None:
        console.print("[bold red]ERROR: [/]The default directory for parsing is not set.\nPlease run the `cf config` command.")
        return

    current_dir = os.getcwd()
    cf_dir = os.path.abspath(cf_dir)
    if not current_dir.startswith(cf_dir) and current_dir != cf_dir:
        console.print("[bold red]ERROR: [/]The current directory is not a contest directory.\n")
        return

    c_id = current_dir.split(slash)[-1]
    if not c_id.isdigit():
        console.print("[bold red]ERROR: [/]The current directory is not a contest directory.\n")
        return

    if not os.path.isfile(file):
        console.print("[bold red]ERROR: [/]The file does not exist.\n")
        return

    p_id = file.split(".")[0].lower()
    p_ext = file.split(".")[-1]

    if p_ext not in lang_ids:
        console.print("[bold red]ERROR: [/]The file extension is not supported.\n")
        return

    if "username" not in data or "password" not in data:
        console.print("[bold red]ERROR: [/]Username and password not set. Please use `cf config`.\n")
        return

    clnt = CFClient(data['username'], data['password'])
    if not clnt.login():
        console.print("[bold red]ERROR: [/]Unable to login")
        return

    url = f"https://codeforces.com/contest/{c_id}/submit"
    csrf = clnt.get_csrf(url)
    url += f"?csrf_token={csrf}"
    resp = clnt.session.post(url=url, allow_redirects=True, data={
        "csrf_token": csrf,
        "ftaa": "",
        "bfaa": "",
        "action": "submitSolutionFormSubmitted",
        "submittedProblemIndex": p_id,
        "programTypeId": lang_ids[p_ext],
        "contestId": c_id,
        "source": open(file, "r").read(),
        "tabSize": "4",
        "sourceCodeConfirmed": "true",
    })
    if not resp.url.startswith(f"https://codeforces.com/contest/{c_id}/my"):
        console.print("[bold red]ERROR: [/] Submission failed.")
        return

    console.print(f"Submitted. idk whether it was accepted or not (work in progress >.<)\ncheck it yourself [link={resp.url}]{resp.url}[/]")

    # TODO: pubsub stuff
