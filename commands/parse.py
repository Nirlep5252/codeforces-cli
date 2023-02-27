import click
import json
import os
import requests
from rich.console import Console
from bs4 import BeautifulSoup

console = Console()


@click.command()
@click.argument("contest_id", required=True)
@click.argument("problem", default="_", required=False)
def parse(contest_id: int, problem: str):
    slash = "/" if os.name == "posix" else "\\\\"

    config_path = os.path.expanduser("~") + slash + "codeforces.uwu"
    if not os.path.isfile(config_path):
        console.print("[bold red]ERROR: [/]Config file not found.\nPlease run `cf config`\n")
        return

    data = None
    with open(os.path.expanduser("~") + slash + "codeforces.uwu", "r") as f:
        data = json.loads("".join(f.readlines()))

    dir = data.get("dir")
    if dir is None:
        console.print("[bold red]ERROR: [/]The default directory for parsing is not set.\nPlease run the `cf config` command.")
        return

    if os.path.isdir(f"{dir}{slash}{contest_id}"):
        console.print(f"[bold red]ERROR: [/]Directory `{contest_id}` already exists.\nMaybe this contest was previously parsed, or this was manually created.\nRemove that directory to parse successfully.")
        return

    if problem == "_":
        r = requests.get(f"https://codeforces.com/contest/{contest_id}")
        if len(r.history) > 0:
            console.print("[bold red]ERROR: [/]Contest has not started yet OR it doesn't exist.\n")
            return

        if r.status_code != 200:
            console.print(f"[bold red]ERROR: [/]Unable to fetch contest details.\nSTATUS CODE: [bold red]{r.status_code}[/]\n")
            return

        soup = BeautifulSoup(r.text, "html.parser")
        p_tables = soup.find_all("table", {"class": "problems"})
        if not p_tables:
            console.print("[bold red]ERROR:[/] Unable to parse problems table.")
            return

        problems = p_tables[0].find_all('tr')[1:]
        for p in problems:
            items = p.find_all('td')
            p_id = items[0].a.string.strip()
            r_p = requests.get(f"https://codeforces.com/contest/{contest_id}/problem/{p_id}")
    else:
        r = requests.get(f"https://codeforces.com/contest/{contest_id}/problem/{problem}")
        if len(r.history) > 0:
            console.print("[bold red]ERROR:[/] Contest or problem not found OR Contest has not started yet.")
            return
        if r.status_code != 200:
            console.print("[bold red]ERROR: [/]Unable to fetch problem details.")
            return
        
        soup = BeautifulSoup(r.text, "html.parser")
        tests = soup.find('div', {"class": "sample-test"})

        inputs = tests.find_all('div', {'class': 'input'})
        outputs = tests.find_all('div', {'class': 'output'})

        final_inps = []
        final_outs = []

        for inp in inputs:
            final_inps.append("\n".join(e.strip() if type(e) == str else e.string.strip() for e in inp.find('pre').contents if not (type(e) != str and e.string is None))) # this line is very long but not as long as my di-

        for out in outputs:
            final_outs.append("\n".join(e.strip() if type(e) == str else e.string.strip() for e in out.find('pre').contents if not (type(e) != str and e.string is None))) # this line is very long but not as long as my di-

        for i in range(len(final_inps)):
            inp = final_inps[i]
            out = final_outs[i]

            console.print(f"Test case #{i}:\nInput:\n{inp}")
            console.print(f"Output:\n{out}\n\n")
        # TODO: save tests in a.0.input.test a.0.output.test ... etc
