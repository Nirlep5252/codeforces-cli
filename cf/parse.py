import click
import os
import requests
from rich.console import Console
from bs4 import BeautifulSoup
from utils import get_config

console = Console()


def parse_problem(contest_id: int, problem: str, cf_dir: str, print_info: bool = True):
    slash = "/" if os.name == "posix" else "\\\\"
    r = requests.get(url=f"https://codeforces.com/contest/{contest_id}/problem/{problem}")
    if len(r.history) > 0:
        console.print("[bold red]ERROR:[/] Contest or problem not found OR Contest has not started yet.")
        return
    if r.status_code != 200:
        console.print("[bold red]ERROR: [/]Unable to fetch problem details.")
        return

    contest_dir = f"{cf_dir}{slash}{contest_id}"

    if not os.path.isdir(contest_dir):
        os.mkdir(contest_dir)
        console.print(f"[bold green]INFO: [/]Created directory: `{contest_id}`")

    soup = BeautifulSoup(r.text, "html.parser")
    tests = soup.find('div', {"class": "sample-test"})

    inputs = tests.find_all('div', {'class': 'input'})  # type: ignore
    outputs = tests.find_all('div', {'class': 'output'})  # type: ignore

    final_inps = []
    final_outs = []

    for inp in inputs:
        final_inps.append("\n".join(e.strip() if type(e) == str else e.string.strip() for e in inp.find('pre').contents if not (type(e) != str and e.string is None)))

    for out in outputs:
        final_outs.append("\n".join(e.strip() if type(e) == str else e.string.strip() for e in out.find('pre').contents if not (type(e) != str and e.string is None)))

    for i in range(len(final_inps)):
        console.print(f"[bold green]INFO: [/]Parsing sample test case #{i + 1}...")
        inp = final_inps[i]
        out = final_outs[i]

        with open(f"{contest_dir}{slash}{problem}.{i}.input.test", "w") as f:
            f.write(inp)

        with open(f"{contest_dir}{slash}{problem}.{i}.output.test", "w") as f:
            f.write(out)

    console.print(f"[bold green]Problem {contest_id} {problem} parsed successfully.[/]\n")
    if print_info:
        console.print(f"Use `cd {contest_dir}` to move the contest directory.")
        console.print("Then use `cf run FILENAME` to check the sample test cases.\n")


@click.command()
@click.argument("contest_id", required=True)
@click.argument("problem", default="_", required=False)
def parse(contest_id: int, problem: str):
    """
    Parse the sample test cases for a problem OR a contest.
    """
    problem = problem.lower()
    data = get_config(console)
    if data is None:
        return

    cf_dir = data.get("dir")
    if cf_dir is None:
        console.print("[bold red]ERROR: [/]The default directory for parsing is not set.\nPlease run the `cf config` command.")
        return

    if problem == "_":
        r = requests.get(url=f"https://codeforces.com/contest/{contest_id}")
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
        for i, p in enumerate(problems):
            items = p.find_all('td')
            p_id = items[0].a.string.strip().lower()
            parse_problem(contest_id, p_id, cf_dir, print_info=(i == len(problems) - 1))
    else:
        parse_problem(contest_id, problem, cf_dir)
