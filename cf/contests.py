import click
from bs4 import BeautifulSoup
from rich.table import Table
from rich.console import Console
from rich.style import Style
from utils import CFClient, get_config

console = Console()


colors = {
    "red": "#ff1c1d",
    "orange": "#ff981a",
    "violet": "#ff55ff",
    "gray": "#9c9388",
    "blue": "#254b8c",
    "admin": "#ffffff",
    "cyan": "#57fcf2",
    "green": "#72ff72"
}


def format_writer(writer) -> str:
    if writer.string is None:
        return f"[white]{writer.contents[0].string}[/white][{colors['red']}]{writer.contents[1]}[/]"
    else:
        return f"[{colors[writer['class'][1].split('-')[1]]}]{writer.string.strip()}[/]"


@click.command()
@click.argument("_id", default=0, required=False)
def contests(_id: str):
    """
    Get the list of current or upcoming contests.
    """
    config = get_config(console)
    if config is None:
        return
    if "username" not in config or "password" not in config:
        console.print("[bold red]ERROR: [/]Username and password not set. Please use `cf config`.\n")
        return

    client = CFClient(config['username'], config['password'])
    client.login()

    if _id == 0:
        console.log("Fetching contest details...")
        r = client.session.get("https://codeforces.com/contests?complete=true")
        if r.status_code != 200:
            console.print(f"[bold red]ERROR:[/] Status Code: {r.status_code}")
            return

        soup = BeautifulSoup(r.text, "html.parser")
        table = Table(title="Current or upcoming contests", show_lines=True)

        c = soup.find('div', {'class': 'contestList'}).find('table').find_all('tr')  # type: ignore
        if not c:
            console.print("[bold red]An error occured.[/]")
            return
        table.add_column("ID", justify="center")
        for col in c[0].find_all('th'):
            table.add_column(col.string, justify="center")

        for cont in c[1:]:
            _id = cont['data-contestid']
            tds = cont.find_all('td')
            start = tds[2].a.span.string.strip()
            start = "\n".join(start.split())

            last = tds[5].contents

            if len(last) == 3:
                last = last[0].strip() + "\n[#9c9388]" + (last[1].string or last[1].contents[1]).strip() + "[/]"
            else:
                last = f"[blue link=https://codeforces.com/contestRegistrants/{_id}]{last[3].contents[1].strip()}\n[/]"
                last += "Until Closing\n"
                last += f"[{colors['gray']}]{tds[5].contents[5].span.string.strip()}[/]"

            print(tds[0])
            table.add_row(
                str(_id),
                f"[link=https://codeforces.com/contests/{_id}]{(tds[0].string or tds[0].contents[0]).strip()}[/]",
                "\n".join([format_writer(e) or "" for e in tds[1].find_all('a')]),
                f"[blue link={tds[2].a['href']}]{start}[/]",
                tds[3].string.strip(),
                (tds[4].contents[0].strip() or "Running") + f"\n[{colors['gray']}]" + tds[4].span.string.strip() + "[/]",
                last
            )

        console.print("\n\n", table)
        console.print("[bold green]NOTE:[/] Use `cf contests ID` to view problems of an ongoing contest.\nAnd use `cf parse ID` to parse them.\n")
    else:
        console.log("Fetching contest details...")
        r = client.session.get(f"https://codeforces.com/contest/{_id}")
        if r.status_code != 200:
            console.print(f"[bold red]ERROR:[/] Status Code: {r.status_code}")
            return
        if len(r.history) > 0:
            console.print("[bold red]ERROR:[/] The contest has not started yet OR it doesn't exist.")
            return

        soup = BeautifulSoup(r.text, "html.parser")
        p_tables = soup.find_all("table", {"class": "problems"})
        if not p_tables:
            console.print("[bold red]ERROR:[/] Unable to parse problems table.")
            return

        problems = p_tables[0].find_all('tr')[1:]
        contest = soup.find_all("table", {"class": "rtable"})[0].find_all('tr')
        contest_name = contest[0].th.a.string.strip()
        contest_time = contest[1].td.span.string.strip()
        table = Table(title=f"{contest_name} - {contest_time}", show_lines=True)

        table.add_column("#", justify="center")
        table.add_column("Name", justify="left")
        table.add_column(" ", justify="center")
        table.add_column(" ", justify="center")

        for problem in problems:
            kwargs = {}
            if "accepted-problem" in (problem.get('class') or []):
                kwargs['style'] = Style(bgcolor="#00ff00", color="#000000")
            elif "rejected-problem" in (problem.get('class') or []):
                kwargs['style'] = Style(bgcolor="red", color="#000000")
            items = problem.find_all('td')
            problem_name = items[1].find('a').contents[1].strip()
            problem_details = items[1].find('div', {'class': 'notice'}).contents
            table.add_row(
                items[0].a.string.strip(),
                f"[link=https://codeforces.com/contest/{_id}/problem/{items[0].a.string.strip()}]{problem_name}[/]",
                f"[{colors['gray']}]" + problem_details[1].string.strip() + "\n" + problem_details[2].strip() + "[/]",
                f"[blue link=https://codeforces.com/contest/{_id}/status/{items[0].a.string.strip()}]{items[3].a.contents[1].strip()}[/]",
                **kwargs
            )

        console.print("\n\n", table)
        console.print(f"\n[bold green]NOTE:[/] Use `cf parse {_id}` to parse all the problems and solve them from your terminal.\n\n")
