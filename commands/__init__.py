import click
from .config import config
from .contests import contests
from .parse import parse


@click.group
def commands():
    pass


commands.add_command(config)
commands.add_command(contests)
commands.add_command(parse)
