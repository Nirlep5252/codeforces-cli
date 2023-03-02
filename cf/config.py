import click
import json
import os
import requests
from bs4 import BeautifulSoup
from rich.console import Console

console = Console()


@click.command()
@click.option("--username", prompt="Enter your codeforces username")
@click.password_option()
@click.option("--cf_dir", prompt="Enter your codeforces directory")
def config(username: str, password: str, cf_dir: str):
    """
    Configure the codeforces cli.
    """

    r1 = requests.get("https://codeforces.com/enter")
    s1 = BeautifulSoup(r1.text, "html.parser")
    csrf_token: str = s1.find_all("span", {"class": "csrf-token"})[0]["data-csrf"]  # type: ignore
    console.log(csrf_token)

    r2 = requests.post("https://codeforces.com/enter", data={
        "csrf_token": csrf_token,
        "action": "enter",
        "handleOrEmail": username,
        "password": password,
    }, headers={
        "X-Csrf-Token": csrf_token
    }, allow_redirects=True)
    s2 = BeautifulSoup(r2.text, "html.parser")

    with open("testing.html", "w") as f:
        f.write(r2.text)

    usr = s2.find_all("div", {"class": "lang-chooser"})[0].find_all('a')  # type: ignore
    if usr[-1].string.strip() == "Register":
        console.print("[bold red]ERROR: [/] Login failed, you may have entered incorrect username/password.")
        return

    console.log(r2.cookies, r2.headers)

    if cf_dir.startswith("~"):
        cf_dir = os.path.expanduser('~') + cf_dir[1:]
    if not os.path.isdir(cf_dir):
        console.print(f"[bold red]ERROR: [/] Directory `{cf_dir}` not found.")
        return

    cf_dir = os.path.abspath(cf_dir)
    data = {
        "dir": cf_dir,
        "username": username,
        "password": password
    }

    slash = "/" if os.name == "posix" else "\\\\"
    with open(os.path.expanduser('~') + slash + "codeforces.uwu", "w") as f:
        f.write(json.dumps(data))

    console.print("[bold green]Config set![/]\n" + f"dir: {cf_dir}")
