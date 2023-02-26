import click
import requests
from rich.console import Console
from bs4 import BeautifulSoup
from rich.table import Table

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
    if _id == 0:
        soup = BeautifulSoup(requests.get("https://codeforces.com/contests").text, "html.parser")
        table = Table(title="Current or upcoming contests", show_lines=True)

        c = soup.find_all('table')[0].find_all('tr')
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
                last = last[0].strip() + "\n[#9c9388]" + last[1].string.strip() + "[/]"
            else:
                last = f"[blue link=https://codeforces.com/contestRegistrants/{_id}]{last[3].contents[1].strip()}\n[/]"
                last += "Until Closing\n"
                last += f"[{colors['gray']}]{tds[5].contents[5].span.string.strip()}[/]"

            table.add_row(
                str(_id),
                f"[link=https://codeforces.com/contests/{_id}]{tds[0].string.strip()}[/]",
                "\n".join([format_writer(e) or "" for e in tds[1].find_all('a')]),
                f"[blue link={tds[2].a['href']}]{start}[/]",
                tds[3].string.strip(),
                tds[4].contents[0].strip() + f"\n[{colors['gray']}]" + tds[4].span.string.strip() + "[/]",
                last
            )

        console.print(table)
    else:
        r = requests.get(f"https://codeforces.com/contest/{_id}")
        if len(r.history) > 0:
            console.print("[bold red]The contest has not started yet OR it doesn't exist.[/]")
            return
        soup = BeautifulSoup(r.text, "html.parser")
        # TODO: - list problems, with table just like browser
        #       - create folder in the default cf dir if config is set
        #       - also do sign in asodhaishud amogus
