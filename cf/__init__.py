import click
from .config import config
from .contests import contests
from .parse import parse
from .submit import submit
from .run import run
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
                cmd.help.strip()  # type: ignore
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
