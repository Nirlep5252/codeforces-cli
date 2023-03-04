import click
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from utils import CFClient, get_config

console = Console()


@click.command()
def unsolved():
    """Show unsolved problems"""
    conf = get_config(console)
    if conf is None:
        return

    if "username" not in conf and "password" not in conf:
        console.print("[bold red]ERROR: [/]Username and password not found in config file")
        return

    client = CFClient(conf["username"], conf["password"])
    if not client.login():
        console.print("[bold red]ERROR: [/]Login failed")
        return

    ps = client.session.get("https://codeforces.com/problemset")
    if ps.status_code != 200:
        console.print("[bold red]ERROR: [/]Failed to fetch unsolved problems.")
        return

    soup = BeautifulSoup(ps.text, "html.parser")
    unsolved_table = soup.find('table', {'class': 'rtable'})
    if unsolved_table is None:
        console.print("[bold red]ERROR: [/]Failed to fetch unsolved problems.")
        return
    problems = unsolved_table.find_all('tr')[1:]  # type: ignore

    if len(problems) == 0:
        console.print("[bold green]WOW: [/]You do not have any unsolved problems.")
        console.print("(This means any problem where you have submitted a solution but it was not accepted.)")
        console.print("Obviously you will have several problems that you haven't tried.")
        return

    table = Table(title="Unsolved Problems", show_header=True, header_style="bold green", show_lines=True)
    table.add_column("Problem ID", style="bright", justify="left", no_wrap=True)
    table.add_column("Problem Name", style="bright", justify="left", no_wrap=True)
    table.add_column("Last Submission", style="bright", justify="left", no_wrap=True)
    for problem in problems:
        data = problem.find_all('td')
        _id = data[0].a.string.strip()
        p_url = data[0].a['href'].strip()
        name = data[1].a.string.strip()
        sub_id = data[2].a.string.strip()

        table.add_row(
            f"[link=https://codeforces.com{p_url}]{_id}[/]", name,
            f"[link=https://codeforces.com{data[2].a['href'].strip()}]{sub_id}[/]"
        )

    console.print(table)
