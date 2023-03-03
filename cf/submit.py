import click
import json
import websocket
import os
from utils import get_config, CFClient
from bs4 import BeautifulSoup
from rich.console import Console
from rich.live import Live
from rich.text import Text

console = Console()


lang_ids = {
    "py": "70",
    "c": "43",
    "cpp": "73",
    "cs": "79",  # C#
    "d": "28",  # D
    "go": "32",  # Golang
    "hs": "12",  # Haskell
    "java": "74",
    "kt": "83",  # Kotlin
    "ml": "19",  # Ocaml
    "php": "6",
    "rb": "67",  # Ruby
    "rs": "75",  # Rust
    "js": "55",  # Nodejs
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

    r = clnt.session.get(f"https://codeforces.com/contest/{c_id}/my")
    soup = BeautifulSoup(r.text, "html.parser")

    table = soup.find('table', {'class': 'status-frame-datatable'})
    last_sub = table.find_all('tr')[1]  # type: ignore
    sub_id = int(last_sub['data-submission-id'])
    sub_status = last_sub.find('td', {'class': 'status-verdict-cell'})
    if sub_status['waiting'] == "true":
        sub_status = "In Queue"
    else:
        sub_status = "IDK"
    sub_time = last_sub.find('td', {'class': 'time-consumed-cell'}).string
    sub_mem = last_sub.find('td', {'class': 'memory-consumed-cell'}).string

    console.print(f"[bold green]SUBMITTED[/] [bold blue]https://codeforces.com/contest/{c_id}/submission/{sub_id}[/]")
    live_text = f"""
Status:     [bold white]{sub_status.strip()}[/]
Time:       [bold white]{sub_time.strip()}[/]
Memory:     [bold white]{sub_mem.strip()}[/]
                    """

    sub_watcher = websocket.WebSocket()
    sub_watcher.connect("wss://pubsub.codeforces.com/ws/s_1988fd413d914791b025375d6bc48e62dcbb55e5/s_8299e18de2d40feb5075aa02ebb9ec5934e87d77?_=1677814224990")

    live = Live(live_text, console=console)
    live.start()
    live.refresh()
    while (True):
        sub = json.loads(sub_watcher.recv())
        sub_data = json.loads(sub['text'])['d']
        live_sub_id = sub_data[1]
        if live_sub_id == sub_id:
            status = sub_data[6]
            test_case = sub_data[8]

            if status == "OK":
                status_text = "[bold green]ACCEPTED[/]"
            elif status in ("WRONG_ANSWER", "COMPILATION_ERROR", "RUNTIME_ERROR", "TIME_LIMIT_EXCEEDED", "MEMORY_LIMIT_EXCEEDED", "IDLENESS_LIMIT_EXCEEDED", "SECURITY_VIOLATED", "CRASHED", "INPUT_PREPARATION_CRASHED", "CHALLENGED", "SKIPPED", "PARTIAL", "REJECTED"):
                status_text = f"[bold red]{' '.join(status.split('_'))}[/] on test case: {test_case}"
            elif status == "TESTING":
                status_text = f"[bold]Running on test case: {test_case}[/]"
            else:
                status_text = status

            timee = sub_data[9]
            memory = int(sub_data[10]) // 1000
            live_text = f"""
Status:     {status_text}
Time:       [bold]{timee} ms[/]
Memory:     [bold]{memory} KB[/]
            """
            live.update(live_text)
            live.refresh()
            if status != "TESTING":
                live.stop()
                break
