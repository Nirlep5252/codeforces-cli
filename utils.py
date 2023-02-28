import os
import json
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
