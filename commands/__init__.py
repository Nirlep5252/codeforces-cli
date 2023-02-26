import click
from .config import config
from .contests import contests


@click.group
def commands():
    pass


commands.add_command(config)
commands.add_command(contests)

