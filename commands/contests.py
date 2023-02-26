import click
import requests
import os
from rich.console import Console
from bs4 import BeautifulSoup
from rich.table import Table

console = Console()


@click.command()
@click.argument("_id", default=0, required=False)
def contests(_id: str):
    if _id == 0:
        soup = BeautifulSoup(requests.get("https://codeforces.com/contests").text, "html.parser")
        table = Table(title="Current or upcoming contests", show_lines=True)

        c = soup.find_all('table')[0].find_all('tr')
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
                last = f"[blue link=https://codeforces.com/contestRegistrants/{_id}]{last[3].contents[1].strip()}"

            table.add_row(
                f"[link=https://codeforces.com/contests/{_id}]{tds[0].string.strip()}[/]",
                "\n".join([e.string.strip() for e in tds[1].find_all('a')]),
                f"[blue link={tds[2].a['href']}]{start}[/]",
                tds[3].string.strip(),
                tds[4].contents[0].strip() + "\n[#9c9388]" + tds[4].span.string.strip() + "[/]",
                last
            )

        console.print(table)
    else:
        pass

