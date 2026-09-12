import sys

# Oldest Python we support, and the newest release this was tested against.
MIN_PYTHON = (3, 9)
LATEST_TESTED_PYTHON = (3, 14)


def _check_python_version() -> None:
    """
    Fail loudly on Python versions we do not support, and warn on untested ones.

    Uses plain print instead of rich: this runs before any third party import,
    because an unsupported interpreter usually breaks those imports first.
    """
    current = ".".join(str(v) for v in sys.version_info[:3])

    if sys.version_info < MIN_PYTHON:
        minimum = ".".join(str(v) for v in MIN_PYTHON)
        print(
            f"ERROR: codeforces-cli needs Python {minimum} or newer, "
            f"but this is Python {current} ({sys.executable}).\n"
            f"Install it under a newer interpreter, for example:\n"
            f"  pipx install --python python3.13 codeforces",
            file=sys.stderr,
        )
        raise SystemExit(1)

    if sys.version_info[:2] > LATEST_TESTED_PYTHON:
        latest = ".".join(str(v) for v in LATEST_TESTED_PYTHON)
        print(
            f"WARNING: Python {current} is newer than the latest version "
            f"codeforces-cli was tested on ({latest}). "
            f"If something breaks, please open an issue.",
            file=sys.stderr,
        )


_check_python_version()

import click
from .config import config
from .contests import contests
from .parse import parse
from .submit import submit
from .run import run
from .unsolved import unsolved
from .edit import edit_cmd
from rich.console import Console
from rich.table import Table
from typing import Dict

console = Console()


class RichGroup(click.Group):
    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter):
        cmds: Dict[str, click.Command] = ctx.command.commands  # type: ignore

        console.print(r"""[bold green]

                  __     ____
  _________  ____/ /__  / __/___  _____________  _____
 / ___/ __ \/ __  / _ \/ /_/ __ \/ ___/ ___/ _ \/ ___/
/ /__/ /_/ / /_/ /  __/ __/ /_/ / /  / /__/  __(__  )
\___/\____/\__,_/\___/_/  \____/_/   \___/\___/____/


        [/]""")

        table = Table(show_header=True, header_style="bold green", show_lines=True)
        table.add_column("Command", style="bright", justify="left")
        table.add_column("Description")

        for name, cmd in cmds.items():
            table.add_row(
                f"{name} {' '.join(['[dim]{' + e.name + '}[/]' for e in cmd.params])}",  # type: ignore
                (cmd.help or "No Description").strip()  # type: ignore
            )

        console.print(table)


@click.group(cls=RichGroup)
def commands():
    pass


commands.add_command(config)
commands.add_command(contests)
commands.add_command(parse)
commands.add_command(run)
commands.add_command(submit)
commands.add_command(unsolved)
commands.add_command(edit_cmd)
