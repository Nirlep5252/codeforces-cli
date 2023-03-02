import os
import json
import requests
from bs4 import BeautifulSoup
from typing import Optional
from rich.console import Console


def get_config(console: Console) -> Optional[dict]:
    slash = "/" if os.name == "posix" else "\\\\"

    config_path = os.path.expanduser("~") + slash + "codeforces.uwu"
    if not config_path:
        console.print("[bold red]ERROR: [/]Config file not found.\nPlease run `cf config`\n")
        return

    if not os.path.isfile(config_path):
        console.print("[bold red]ERROR: [/]Config file not found.\nPlease run `cf config`\n")
        return

    data = None
    with open(config_path, "r+") as f:
        data = json.loads("".join(f.readlines()))

    return data


class CFClient:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.console = Console()

    def login(self) -> bool:
        self.console.log("Logging in...")
        csrf_token = self.get_csrf("https://codeforces.com/enter")

        r2 = self.session.post("https://codeforces.com/enter", data={
            "csrf_token": csrf_token,
            "action": "enter",
            "handleOrEmail": self.username,
            "password": self.password
        }, headers={
            "X-Csrf-Token": csrf_token
        }, allow_redirects=True)
        s2 = BeautifulSoup(r2.text, "html.parser")

        usr = s2.find_all("div", {"class": "lang-chooser"})[0].find_all('a')
        if usr[-1].string.strip() == "Register":
            return False

        return True

    def get_csrf(self, url) -> str:
        r = self.session.get(url)
        s = BeautifulSoup(r.text, "html.parser")
        return s.find_all("span", {"class": "csrf-token"})[0]["data-csrf"]
